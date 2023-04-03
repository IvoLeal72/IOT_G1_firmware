from machine import Pin

class DoorControl:
    def __init__(self, pin):
        self.pin=Pin(pin, mode=Pin.OUT)
        self.pin(1)

    def open(self):
        self.pin(0)

    def close(self):
        self.pin(1)

    def is_open(self) -> bool:
        return not self.pin()
