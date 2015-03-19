from efl import ecore

import threading
try:
    import Queue
except:
    import queue as Queue

class ThreadedFunction(object):
    def __init__(self, doneCB=None):
        # private stuff
        self._commandQueue = Queue.Queue()
        self._replyQueue = Queue.Queue()
        self._doneCB = doneCB

        # add a timer to check the data returned by the worker thread
        self._timer = ecore.Timer(0.1, self.checkReplyQueue)

        # start the working thread
        threading.Thread(target=self.threadFunc).start()

    def run(self, action):
        self._commandQueue.put(action)

    def shutdown(self):
        self._timer.delete()
        self._commandQueue.put('QUIT')

    def checkReplyQueue(self):
        if not self._replyQueue.empty():
            result = self._replyQueue.get()
            if callable(self._doneCB):
                self._doneCB()
        return True

    # all the member below this point run in the thread
    def threadFunc(self):
        while True:
            # wait here until an item in the queue is present
            func = self._commandQueue.get()
            if callable(func):
                func()
            elif func == 'QUIT':
                break
            self._replyQueue.put("done")
