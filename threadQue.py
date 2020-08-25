from threading import Thread
from os import cpu_count

class returnThreadWithQueUpdate(Thread):
    def __init__(self, group=None, target=None, name=None, wrapper=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self.wrapper = wrapper
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
            if self.wrapper is not None:
                self.wrapper.threads.remove(self)
                if len(self.wrapper.que) > 0 and len(self.wrapper.threads) < self.wrapper.threadCount:
                    self.wrapper.que.remove(q := self.wrapper.que[0])
                    tt = returnThreadWithQueUpdate(*q.args, wrapper = self.wrapper, **q.kwargs)
                    tt.start()
                    self.wrapper.threads.append(tt)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class dummyThread():
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

class threadQue():
    def __init__(self, threadCount = cpu_count(), que = [], threads = [], useWrapper = True, l = False):
        self.que, self.threads, self.threadCount, self.useWrapper = que, threads, threadCount, useWrapper
        if l:
            print(f"Created ThreadQue with {threadCount} threads.")
    def addThread(self, dummyThread):
        self.que.append(dummyThread)
        self.runQuedThreads()
    def runQuedThreads(self):
        for t in self.threads:
            if not t.is_alive():
                t.join()
                self.threads.remove(t)

        if len(self.threads) < self.threadCount:
            for q in self.que[:self.threadCount - len(self.threads)]:
                if self.useWrapper:
                    tt = returnThreadWithQueUpdate(*q.args, wrapper = self, **q.kwargs)
                else:
                    tt = returnThreadWithQueUpdate(*q.args, wrapper = self, **q.kwargs)
                tt.start()
                self.threads.append(tt)
                self.que.remove(q)
    def __repr__(self):
        return f"Thread count: {len(self.threads)}, Que length: {len(self.que)}"