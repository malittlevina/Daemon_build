from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable
import threading
import time

from devices.types import DevicePassport


PassportCallback = Callable[[DevicePassport], None]


class DiscoveryDriver(ABC):
    """
    Base class for discovery drivers. Drivers emit DevicePassport updates.
    """

    name: str

    def __init__(self, *, interval_s: float = 30.0):
        self.interval_s = interval_s
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run_forever(self, emit: PassportCallback) -> None:
        while not self._stop.is_set():
            try:
                for passport in self.scan_once():
                    emit(passport)
            except Exception as e:
                # Driver isolation: one driver failing shouldn't kill the daemon.
                # Emitted via fabric logging, so keep this quiet here.
                _ = e
            time.sleep(self.interval_s)

    @abstractmethod
    def scan_once(self) -> list[DevicePassport]:
        raise NotImplementedError

