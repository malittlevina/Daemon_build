from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from devices.events import DeviceEvent
from devices.types import DevicePassport


@dataclass(slots=True)
class RegistryUpdate:
    event: DeviceEvent
    is_new: bool


class DeviceRegistry:
    """
    In-memory registry of device passports.
    """

    def __init__(self):
        self._devices: dict[str, DevicePassport] = {}

    def upsert(self, passport: DevicePassport) -> RegistryUpdate:
        existing = self._devices.get(passport.device_id)
        if existing is None:
            self._devices[passport.device_id] = passport
            return RegistryUpdate(
                event=DeviceEvent(kind="device.discovered", passport=passport),
                is_new=True,
            )

        # Merge updates
        existing.merge(identity=passport.identity, fingerprints=passport.fingerprints)
        existing.capabilities |= passport.capabilities
        if passport.trust_state and passport.trust_state != "unknown":
            existing.trust_state = passport.trust_state

        return RegistryUpdate(
            event=DeviceEvent(kind="device.updated", passport=existing),
            is_new=False,
        )

    def get(self, device_id: str) -> DevicePassport | None:
        return self._devices.get(device_id)

    def all(self) -> list[DevicePassport]:
        return list(self._devices.values())

    def snapshot(self) -> list[dict[str, Any]]:
        return [d.to_dict() for d in self.all()]

