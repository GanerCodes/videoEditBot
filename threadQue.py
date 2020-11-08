from threading import Thread
from os import cpu_count
import threading
import ctypes, time

class returnThreadWithQueUpdate(Thread):
    def __init__(self, group=None, target=None, name=None, wrapper=None, args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self.wrapper = wrapper
        self.startTime = time.time()
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
    def get_id(self): 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
    def raise_exception(self, msg = ""): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        print(msg)
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            print("Couldn't kill thread!")

class dummyThread():
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

class threadQue():
    def __init__(self, threadCount = cpu_count(), timeout = 10 * 60, que = [], threads = [], useWrapper = True, l = False):
        self.que, self.threads, self.threadCount, self.useWrapper, self.timeout = que, threads, threadCount, useWrapper, timeout
        if l:
            print(f"Created ThreadQue with {threadCount} threads.")
    def addThread(self, dummyThread):
        self.que.append(dummyThread)
        self.runQuedThreads()
    def runQuedThreads(self):
        currentTime = time.time()
        for t in self.threads:
            if killThread := currentTime - t.startTime >= self.timeout:
                t.raise_exception(f"Thread took longer than {self.timeout} second(s) to finish! Killing thread.")
            if killThread or not t.is_alive():
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
    def __len__(self):
        return len(self.threads)
    def __repr__(self):
        return f"Thread count: {len(self)}, Que length: {len(self.que)}"