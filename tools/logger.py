import os
from queue import Queue, Empty
import threading


# thread safe appending to file
class Logger:
    def __init__(self, *args):
        self.args = args
        self.queue = Queue()
        self.finished = False
        threading.Thread(target=self.internal_writer).start()

    def write(self, data):
        self.queue.put(data)

    def internal_writer(self):
        while not self.finished:
            try:
                data = self.queue.get(True, 1)
            except Empty:
                continue
            try:
                f = open(*self.args)
                f.write(data)
                f.close()
            except Exception as e:
                f = open(*self.args)
                f.write("-- An error occured here: " + str(e) + " --")
                f.close()
            self.queue.task_done()

    def close(self):
        self.queue.join()
        self.finished = True
