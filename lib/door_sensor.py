from machine import Pin

class DoorSensor:
    def __init__(self, pin, callback=None):
        def pin_handler(pin):
            self.__value=pin()
            if callback:
                callback(self.open)
        self.pin=Pin(pin, mode=Pin.IN)
        self.pin.callback(Pin.IRQ_RAISING | Pin.IRQ_FALLING, pin_handler)
        self.__value=self.pin()

    @property
    def open(self) -> bool:
        return bool(self.__value)

    

