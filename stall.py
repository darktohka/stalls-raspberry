from enum import Enum
from state import StateEvent
from settings import DEBUG
from state import StallState
import time, logging

UPDATE_DELAY = 0.5

class Stall(object):

    def __init__(self, id, state_queue, human_sensor, door_sensor, red_light, green_light):
        self.id = id
        self.state_queue = state_queue
        self.human_sensor = human_sensor
        self.door_sensor = door_sensor
        self.red_light = red_light
        self.green_light = green_light

        self.current_state = StallState.Free
        self.next_state = StallState.Free
        self.state_update_at = 0
    
    def init_pins(self):
        self.human_sensor.init_pins()
        self.door_sensor.init_pins()
        self.red_light.init_pins()
        self.green_light.init_pins()
        self.green_light.set(True)

    def cleanup(self):
        self.red_light.set(False)
        self.green_light.set(False)

    def update_state(self, state):
        if self.current_state == state:
            # No state transition is required.
            return

        if self.next_state != state:
            # A new state has been detected.
            # Reset the timer.
            self.state_update_at = time.time() + UPDATE_DELAY
            self.next_state = state
            return

        if self.state_update_at >= time.time():
            # The state hasn't been active for long.
            # Wait until setting the next state.
            return
        
        # Update the state!
        self.current_state = state

        occupied = self.current_state == StallState.Occupied

        self.red_light.set(occupied)
        self.green_light.set(not occupied)

        print(f'State changed: {self.current_state}')
        self.state_queue.queue_event(StateEvent(self.id, time.time(), self.current_state))

    def update_sensors(self):
        human_distance = self.human_sensor.distance()
        door_distance = self.door_sensor.distance()

        if DEBUG:
            logging.info('Human distance: %.1f cm', human_distance)
            logging.info('Door distance: %.1f cm', door_distance)

        is_door_open = door_distance < 15
        occupied = human_distance < 15 and not is_door_open

        state = StallState.Occupied if occupied else StallState.Free
        self.update_state(state)