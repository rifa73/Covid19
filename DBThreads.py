import threading
import queue
import Db
import ctypes
import logging

logging.basicConfig(level=logging.INFO)

class Threads:

    def __init__(self):
        self.database = Db.Db()
        self.crowd_q = queue.Queue()
        self.mask_q = queue.Queue()
        self.t1 = threading.Thread(target=self.populateMask)
        self.t2 = threading.Thread(target=self.populateCrowd)


    def populateMask(self):
        while True:
            np_image ,place, ct = self.mask_q.get()
            if np_image is None or ct is None or place is None:
                break
            else:
                self.database.populateMaskViolation(np_image, ct, place)
                self.mask_q.task_done()
    
    def populateCrowd(self):
        while True:
            frame, place, ct, violation_type = self.crowd_q.get()
            if frame is None or ct is None or place is None:
                break
            else:
                self.database.populateCrowdViolation(frame, ct, place, violation_type)
                self.crowd_q.task_done()

