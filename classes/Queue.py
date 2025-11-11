#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from queue import Queue, Full

########################################
#           QUEUE SINIFLAR             #
########################################

class DiscardOldestQueue:
    def __init__(self, maxsize=3):
        self.queue = Queue(maxsize=maxsize)
    
    def put(self, item):
        try:
            self.queue.put(item, block=False)
        except Full:
            self.queue.get()
            self.queue.put(item, block=False)
    
    def get(self, block=True, timeout=None):
        return self.queue.get(block=block, timeout=timeout)
    
    def qsize(self):
        return self.queue.gsize()
    
    def empty(self):
        return self.queue.empty()
    
    def full(self):
        return self.queue.full()
    
