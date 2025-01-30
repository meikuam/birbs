import os
from pathlib import Path
from threading import Lock
from contextlib import contextmanager


def project_root() -> Path:
    return Path(
        os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../..")
        )
    )


class TimeoutLock(object):
    def __init__(self):
        self._lock = Lock()

    def acquire(self, blocking: bool = True, timeout: int = -1):
        return self._lock.acquire(blocking, timeout)

    @contextmanager
    def acquire_timeout(self, timeout: int = -1):
        result = self.acquire(timeout=timeout)
        try:
            yield result
        finally:
            if result:
                self.release()

    def release(self):
        self._lock.release()
