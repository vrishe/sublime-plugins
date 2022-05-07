import sys

from threading import *

class CompletionSource:
    def __init__(self):
        self.condition = Condition();
        self.result = None
        self.done = False

    def set_result(self, result):
        if self.done:
            raise RuntimeError('result is already set.')

        self.condition.acquire()
        self.result = result;
        self.done = True
        self.condition.notify()
        self.condition.release()

    def get_result(self):
        self.condition.acquire()
        while not self.done:
            self.condition.wait()
        self.condition.release()
        return self.result

    def reset(self):
        self.done = False
        self.result = None