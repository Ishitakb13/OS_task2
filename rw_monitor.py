"""Readers-Writers problem - MONITOR based (writer-preference).

Python has no built-in monitor, so the class below is a monitor made of one
lock + two condition variables. Only one thread runs inside the monitor
methods at a time (the lock), and threads wait on conditions when they
cannot proceed.
Shared resource : shared["data"]
Writer-preference: new readers wait if a writer is waiting, so writers do
not starve (but readers could starve if writers keep coming).
"""
import threading
import random
import time
from common import Recorder
from viz import make_html

NUM_READERS = 4
NUM_WRITERS = 2
ROUNDS = 2

rec = Recorder()
shared = {"data": 0}


class RWMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.can_read = threading.Condition(self.lock)
        self.can_write = threading.Condition(self.lock)
        self.active_readers = 0
        self.writing = False
        self.waiting_writers = 0

    def start_read(self, name):
        with self.lock:
            rec.log(actor=name, state="waiting")
            while self.writing or self.waiting_writers > 0:
                self.can_read.wait()
            self.active_readers += 1
            rec.log(actor=name, state="reading", readers=self.active_readers, data=shared["data"])

    def end_read(self, name):
        with self.lock:
            self.active_readers -= 1
            rec.log(actor=name, state="done", readers=self.active_readers)
            if self.active_readers == 0:
                self.can_write.notify()

    def start_write(self, name):
        with self.lock:
            rec.log(actor=name, state="waiting")
            self.waiting_writers += 1
            while self.writing or self.active_readers > 0:
                self.can_write.wait()
            self.waiting_writers -= 1
            self.writing = True
            rec.log(actor=name, state="writing", data=shared["data"])

    def end_write(self, name):
        with self.lock:
            self.writing = False
            rec.log(actor=name, state="done", data=shared["data"])
            if self.waiting_writers > 0:
                self.can_write.notify()
            else:
                self.can_read.notify_all()


monitor = RWMonitor()


def reader(i):
    name = f"R{i}"
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0.1, 0.6))
        monitor.start_read(name)
        time.sleep(random.uniform(0.3, 0.7))             # reading
        monitor.end_read(name)


def writer(i):
    name = f"W{i}"
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0.1, 0.6))
        monitor.start_write(name)
        temp = shared["data"]
        time.sleep(random.uniform(0.3, 0.7))             # writing
        shared["data"] = temp + 1
        monitor.end_write(name)


if __name__ == "__main__":
    threads = [threading.Thread(target=reader, args=(i,)) for i in range(1, NUM_READERS + 1)]
    threads += [threading.Thread(target=writer, args=(i,)) for i in range(1, NUM_WRITERS + 1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Final data value:", shared["data"], "(expected", NUM_WRITERS * ROUNDS, ")")
    make_html(rec.events, "Readers-Writers (Monitor)", "rw", "readers_writers_monitor.html")
