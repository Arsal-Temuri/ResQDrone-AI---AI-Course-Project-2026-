from collections import deque
from typing import List


class EventManager:
    def __init__(self, maxlen: int = 200):
        self._queue: deque = deque(maxlen=maxlen)

    def push(self, event: dict):
        self._queue.appendleft(event)

    def recent(self, n: int = 10) -> List[dict]:
        return list(self._queue)[:n]

    def all(self) -> List[dict]:
        return list(self._queue)

    def clear(self):
        self._queue.clear()
