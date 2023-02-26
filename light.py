import RPi.GPIO as GPIO

class Light(object):

    def __init__(self, pin):
        self.pin = pin

    def init_pins(self):
        GPIO.setup(self.pin, GPIO.OUT)
        self.set(False)
    
    def set(self, enabled):
        GPIO.output(self.pin, enabled)
