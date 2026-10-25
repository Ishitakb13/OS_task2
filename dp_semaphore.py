"""Dining Philosophers (4 philosophers) - SEMAPHORE based.

Forks: fork[i] is a semaphore (init 1). Philosopher i uses fork i (left)
and fork (i+1)%4 (right).
Deadlock prevention: a 'room' semaphore initialised to 3 lets at most 3
philosophers try to pick up forks at once. With 4 forks and at most 3
philosophers competing, at least one can always get both forks, so the
circular wait can never close.
Starvation: not completely excluded (a philosopher could keep losing the
race), but with the random delays used here it is very unlikely.
"""
import threading
import random
import time
from common import Recorder
from viz import make_html

N = 4
MEALS = 3

rec = Recorder()
fork = [threading.Semaphore(1) for _ in range(N)]
room = threading.Semaphore(N - 1)
owner = [-1] * N          # who holds each fork (only used for visualization)


def philosopher(i):
    name = f"P{i}"
    left, right = i, (i + 1) % N
    for _ in range(MEALS):
        rec.log(actor=name, state="thinking")
        time.sleep(random.uniform(0.2, 0.8))

        rec.log(actor=name, state="hungry")
        room.acquire()                                   # enter the "room" (max 3)
        fork[left].acquire()
        owner[left] = i
        rec.log(actor=name, state="acquiring", forks=list(owner))
        time.sleep(0.1)
        fork[right].acquire()
        owner[right] = i

        rec.log(actor=name, state="eating", forks=list(owner))
        time.sleep(random.uniform(0.3, 0.8))

        owner[left] = owner[right] = -1                  # mark free before releasing
        rec.log(actor=name, state="releasing", forks=list(owner))
        fork[left].release()
        fork[right].release()
        room.release()
    rec.log(actor=name, state="thinking")


if __name__ == "__main__":
    threads = [threading.Thread(target=philosopher, args=(i,)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("All philosophers finished - no deadlock.")
    make_html(rec.events, "Dining Philosophers (Semaphore)", "dp", "dining_philosophers_semaphore.html")
