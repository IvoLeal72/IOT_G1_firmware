from machine import Pin, Timer


class Tamper:
    def __init__(self, pin, active=False):
        self.pin = pin
        self.__active = active
        if not active:
            self.enable_interrupt()

    @property
    def active(self) -> bool:
        return self.__active

    def enable_interrupt(self):
        def pin_handler(pin):
            self.__active = True
            pin.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, None)
            
        self.pin.callback(Pin.IRQ_RISING | Pin.IRQ_FALLING, pin_handler)
