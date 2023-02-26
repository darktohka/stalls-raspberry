#raspberri py distance sensor

from distance import DistanceSensor
from light import Light
from stall import Stall
from state import StateQueue
import RPi.GPIO as GPIO
import time, atexit

# GPIO pins
TRIGGER_PIN_1 = 17
ECHO_PIN_1 = 27

TRIGGER_PIN_2 = 23
ECHO_PIN_2 = 24

REDLIGHT = 5
GREENLIGHT = 6

STALL_ID = 1

state_queue = StateQueue()
stalls = [
    Stall(
        id=STALL_ID,
        state_queue=state_queue,
        human_sensor=DistanceSensor(TRIGGER_PIN_1, ECHO_PIN_1),
        door_sensor=DistanceSensor(TRIGGER_PIN_2, ECHO_PIN_2),
        red_light=Light(REDLIGHT),
        green_light=Light(GREENLIGHT)
    )
]

def cleanup():
    for stall in stalls:
        stall.cleanup()

def main():
    global stalls, state_queue

    GPIO.setmode(GPIO.BCM)
    atexit.register(cleanup)

    for stall in stalls:
        stall.init_pins()
    
    state_queue.start()

    while True:
        for stall in stalls:
            stall.update_sensors()

        time.sleep(0.02)

if __name__ == '__main__':
    main()
