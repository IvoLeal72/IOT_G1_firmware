from machine import Pin, Timer


class Tamper:
    def __init__(self, pin, callback):
        self.callback = callback
        self.pin = Pin(pin, mode=Pin.IN)
        self.__active = False
        self.enable_interrupt()

    @property
    def active(self) -> bool:
        return self.__active

    def enable_interrupt(self):
        def alarm_handler(alarm):
            self.__active = False
            self.enable_interrupt()
            if self.callback:
                self.callback(False)

        def pin_handler(pin):
            self.__active = True
            pin.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, None)
            self.alarm = Timer.Alarm(handler=alarm_handler, s=1)
            if self.callback:
                self.callback(True)

        self.pin.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, pin_handler)
