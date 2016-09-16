# 2012/12/26 SS - created, a timer that can be paused and puts data in a queue at a given interval

from threading import Thread
from threading import Event
import time

class customTimer(Thread):
    def __init__(self, interval, targetQueue, myName, command):
        Thread.__init__(self)
        self.interval = interval
        self.isPaused = Event()
        self.targetQueue = targetQueue
        self.name = myName #"GrdPollTimer"
        self.command = command
 
    def run(self):
        while True:
            if not self.isPaused.is_set():
                self.isPaused.wait(self.interval)
                if not self.isPaused.is_set():
                    self.targetQueue.put(('WAS',self.name,self.command))
            else:
                time.sleep(1) # Go to sleep when paused
 
    def pause(self):
        self.isPaused.set()

    def resume(self):
        self.isPaused.clear()

