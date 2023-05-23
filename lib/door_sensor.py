from machine import Pin
import utime


class DoorSensor:
    def __init__(self, pin, callback=None, check=False):
        def pin_handler(pin):
            value = pin()
            if self.__value != value:
                self.__value = value
                if callback:
                    callback(self.open)
        self.pin = pin
        self.pin.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, pin_handler)
        self.__value = self.pin()
        if check:
            if callback:
                callback(self.open)

    @property
    def open(self) -> bool:
        return bool(self.__value)


class DoorSensorEvent:
    def __init__(self, state, ticks=None):
        if ticks is None:
            ticks = utime.ticks_ms()
        self.ticks=ticks
        self.state=state

    def to_memory(self, actual_epoch, epoch_ticks):
        return (int(actual_epoch-(epoch_ticks-self.ticks)/1000) << 1 | 1 if self.state else 0)& 0xffffffff
    
class MemoryDoorSensorEvent:
    def __init__(self, bin):
        self.state=bool(bin&1)
        self.epoch=bin>>1

    def to_lora(self):
        dt=utime.gmtime(self.epoch)
        ts=utime.mktime((1970,1,1,dt[3], dt[4], dt[5], None, None))
        return (1 if self.state else 0)<<17 | (ts & 0x1ffff)
        
    

