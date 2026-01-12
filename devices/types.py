from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import hashlib
import json


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_hash(payload: dict[str, Any]) -> str:
    """
    Deterministic hash for device_id derivation.
    Keep the schema stable: only hash values intended to identify a device.
    """
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:24]


@dataclass(slots=True)
class DevicePassport:
    """
    Canonical daemon-wide device representation.

    - identity: stable identifiers (IP, MAC, USN, serial, cert fingerprints, etc.)
    - fingerprints: discovery/protocol metadata used for capability inference
    - capabilities: computed tags that other subsystems can reason about
    - trust_state: unknown|seen|paired|trusted|blocked
    """

    # Stable ID (derived from identity + driver namespace). Do not use random UUIDs.
    device_id: str
    source: str  # driver name, e.g. "ssdp", "arp", later "ble", "nfc"

    # Identity + fingerprinting
    identity: dict[str, Any] = field(default_factory=dict)
    fingerprints: dict[str, Any] = field(default_factory=dict)

    # Computed / inferred
    capabilities: set[str] = field(default_factory=set)

    # Lifecycle
    first_seen: str = field(default_factory=_utc_now_iso)
    last_seen: str = field(default_factory=_utc_now_iso)
    trust_state: str = "unknown"

    def touch(self) -> None:
        self.last_seen = _utc_now_iso()

    def merge(self, *, identity: dict[str, Any] | None = None, fingerprints: dict[str, Any] | None = None) -> None:
        """
        Merge partial updates into the passport. New keys win; existing keys remain
        unless overwritten.
        """
        if identity:
            self.identity.update(identity)
        if fingerprints:
            self.fingerprints.update(fingerprints)
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "source": self.source,
            "identity": self.identity,
            "fingerprints": self.fingerprints,
            "capabilities": sorted(self.capabilities),
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "trust_state": self.trust_state,
        }

    @staticmethod
    def derive_device_id(*, source: str, identity: dict[str, Any]) -> str:
        # Namespace by driver so different transports don't collide.
        return f"{source}:{_stable_hash({'source': source, 'identity': identity})}"

