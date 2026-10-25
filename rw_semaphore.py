"""Readers-Writers problem - SEMAPHORE based (readers-preference).

Shared resource : shared["data"]  (a counter that writers update)
Critical section: the reading / writing code between acquire and release
Semaphores:
  mutex    (init 1) - protects the variable read_count
  resource (init 1) - gives exclusive access to the data; first reader locks
                      it for all readers, last reader unlocks it
Note: readers-preference can starve writers if readers keep arriving.
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
mutex = threading.Semaphore(1)
resource = threading.Semaphore(1)
read_count = 0
shared = {"data": 0}


def reader(i):
    global read_count
    name = f"R{i}"
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0.1, 0.6))           # think before reading
        rec.log(actor=name, state="waiting")

        mutex.acquire()                                  # wait(mutex)
        read_count += 1
        if read_count == 1:
            resource.acquire()                           # first reader blocks writers
        rec.log(actor=name, state="reading", readers=read_count, data=shared["data"])
        mutex.release()                                  # signal(mutex)

        time.sleep(random.uniform(0.3, 0.7))             # --- reading (critical section)

        mutex.acquire()
        read_count -= 1
        if read_count == 0:
            resource.release()                           # last reader lets writers in
        rec.log(actor=name, state="done", readers=read_count)
        mutex.release()


def writer(i):
    name = f"W{i}"
    for _ in range(ROUNDS):
        time.sleep(random.uniform(0.1, 0.6))
        rec.log(actor=name, state="waiting")

        resource.acquire()                               # exclusive access
        temp = shared["data"]
        rec.log(actor=name, state="writing", data=temp)
        time.sleep(random.uniform(0.3, 0.7))             # --- writing (critical section)
        shared["data"] = temp + 1                        # safe: nobody else is inside
        rec.log(actor=name, state="done", data=shared["data"])
        resource.release()


if __name__ == "__main__":
    threads = [threading.Thread(target=reader, args=(i,)) for i in range(1, NUM_READERS + 1)]
    threads += [threading.Thread(target=writer, args=(i,)) for i in range(1, NUM_WRITERS + 1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Final data value:", shared["data"], "(expected", NUM_WRITERS * ROUNDS, ")")
    make_html(rec.events, "Readers-Writers (Semaphore)", "rw", "readers_writers_semaphore.html")