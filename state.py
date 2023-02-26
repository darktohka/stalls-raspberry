from threading import Lock, Thread
from settings import CLOUD_SERVER
from enum import Enum
import time, traceback
import requests

STATE_UPDATE_SLEEP = 1.5
UPLOAD_TIMEOUT = 2

StallState = Enum('StallState', ['Free', 'Occupied'])

class StateUpdateThread(Thread):

    def __init__(self, queue):
        Thread.__init__(self, daemon=True)
        self.queue = queue
    
    def run(self):
        while True:
            self.send_events()
            time.sleep(STATE_UPDATE_SLEEP)
    
    def send_events(self):
        self.queue.lock.acquire(blocking=True)
        
        if self.queue.queue:
            # Upload measurements to the cloud
            url = f'{CLOUD_SERVER}/api/measurements'
            data = {'measurements': [event.format_json() for event in self.queue.queue]}

            try:
                response = requests.post(url, json=data, timeout=UPLOAD_TIMEOUT).json()
                assert(response['ok'])
            except:
                print('Error occurred during HTTP upload! Will try again when web server is available...')
                print(traceback.format_exc())
                time.sleep(2)

        self.queue.flush()
        self.queue.lock.release()

class StateEvent(object):

    def __init__(self, stall_id, update_time, state):
        self.stall_id = stall_id
        self.update_time = update_time
        self.state = state
    
    def format_json(self):
        return {'stall_id': self.stall_id, 'update_time': self.update_time, 'state': self.state == StallState.Occupied}

    def __str__(self):
        return f'StateEvent(stall_id={self.stall_id}, update_time={self.update_time}, state={self.state})'

class StateQueue(object):

    def __init__(self):
        # Queue to send
        self.queue = []
        self.lock = Lock()

        self.pending_queue = []
        self.state_update_thread = StateUpdateThread(self)
    
    def flush(self):
        self.queue = self.pending_queue
        self.pending_queue = []

    def start(self):
        self.state_update_thread.start()
    
    def queue_event(self, event):
        successfully_acquired = self.lock.acquire(False)

        if successfully_acquired:
            # The lock has been successfully acquired.
            # We can use the official queue.
            self.queue.append(event)
            self.lock.release()
        else:
            # The queue is currently being sent to the server.
            # Queue it in a separate queue.
            self.pending_queue.append(event)
