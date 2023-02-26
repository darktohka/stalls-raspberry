import RPi.GPIO as GPIO
import time

MAX_MOVING_WINDOW = 3

class DistanceSensor(object):

    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.moving_window = []

    def init_pins(self):
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def __read_distance(self):
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2

        return distance

    def distance(self):
        distance = self.__read_distance()

        if len(self.moving_window) > MAX_MOVING_WINDOW:
            self.moving_window.pop(0)

        self.moving_window.append(distance)
        return sum(self.moving_window) / len(self.moving_window)
