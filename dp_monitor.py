"""Dining Philosophers (4 philosophers) - MONITOR based.

The monitor keeps each philosopher's state. A philosopher may start eating
only if neither neighbour is eating, and both forks are taken together
inside the monitor, so a philosopher never holds one fork while waiting
for the other -> no hold-and-wait -> no deadlock.
Each philosopher waits on its own condition variable.
Starvation is possible in theory (neighbours may keep taking turns).
"""
import threading
import random
import time
from common import Recorder
from viz import make_html

N = 4
MEALS = 3

rec = Recorder()


class DiningMonitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = ["thinking"] * N
        self.can_eat = [threading.Condition(self.lock) for _ in range(N)]
        self.owner = [-1] * N                             # fork owners (for visualization)

    def _neighbours_free(self, i):
        return (self.state[(i - 1) % N] != "eating" and
                self.state[(i + 1) % N] != "eating")

    def pickup(self, i):
        with self.lock:
            self.state[i] = "hungry"
            rec.log(actor=f"P{i}", state="hungry")
            while not self._neighbours_free(i):
                self.can_eat[i].wait()                    # wait until neighbours finish
            self.state[i] = "eating"
            self.owner[i] = self.owner[(i + 1) % N] = i   # take both forks at once
            rec.log(actor=f"P{i}", state="eating", forks=list(self.owner))

    def putdown(self, i):
        with self.lock:
            self.state[i] = "thinking"
            self.owner[i] = self.owner[(i + 1) % N] = -1
            rec.log(actor=f"P{i}", state="releasing", forks=list(self.owner))
            # a neighbour may now be able to eat
            for n in ((i - 1) % N, (i + 1) % N):
                if self.state[n] == "hungry":
                    self.can_eat[n].notify()


monitor = DiningMonitor()


def philosopher(i):
    for _ in range(MEALS):
        rec.log(actor=f"P{i}", state="thinking")
        time.sleep(random.uniform(0.2, 0.8))
        monitor.pickup(i)
        time.sleep(random.uniform(0.3, 0.8))              # eating
        monitor.putdown(i)
    rec.log(actor=f"P{i}", state="thinking")


if __name__ == "__main__":
    threads = [threading.Thread(target=philosopher, args=(i,)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("All philosophers finished - no deadlock.")
    make_html(rec.events, "Dining Philosophers (Monitor)", "dp", "dining_philosophers_monitor.html")
