from __future__ import annotations

from typing import Any
import threading

from codex.ingestion import ingest_observation
from memory_tree.memory_logger import MemoryLogger
from scrolls.scroll_engine import ScrollEngine

from devices.drivers.arp import ArpNeighborDriver
from devices.drivers.base import DiscoveryDriver
from devices.drivers.ssdp import SsdpDiscoveryDriver
from devices.events import DeviceEvent
from devices.policy import DevicePolicyEngine, summarize_event
from devices.registry import DeviceRegistry
from devices.types import DevicePassport


class DeviceFabric:
    """
    Orchestrates device discovery drivers -> registry -> events -> memory/policy.
    """

    def __init__(
        self,
        *,
        memory: MemoryLogger | None = None,
        scrolls: ScrollEngine | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.memory = memory or MemoryLogger()
        self.scrolls = scrolls
        self.registry = DeviceRegistry()
        self.policy = DevicePolicyEngine()

        self.config = config or {}
        self._threads: list[threading.Thread] = []
        self._drivers: list[DiscoveryDriver] = self._default_drivers()

        # Default policy: log to Codex as a narrative trace.
        if self.config.get("codex_ingest_enabled", True):
            self.policy.register_handler(self._codex_ingest_policy)

        # Default policy: optional scroll hook.
        self.policy.register_handler(self._scroll_hook_policy)

    def _default_drivers(self) -> list[DiscoveryDriver]:
        dcfg = (self.config or {}).get("drivers", {})
        ssdp_cfg = dcfg.get("ssdp", {})
        arp_cfg = dcfg.get("arp", {})

        drivers: list[DiscoveryDriver] = []
        if ssdp_cfg.get("enabled", True):
            drivers.append(
                SsdpDiscoveryDriver(
                    interval_s=float(ssdp_cfg.get("interval_s", 30.0)),
                    mx=int(ssdp_cfg.get("mx", 2)),
                    st=str(ssdp_cfg.get("st", "ssdp:all")),
                    timeout_s=float(ssdp_cfg.get("timeout_s", 3.0)),
                )
            )
        if arp_cfg.get("enabled", True):
            drivers.append(
                ArpNeighborDriver(
                    interval_s=float(arp_cfg.get("interval_s", 60.0)),
                    arp_path=str(arp_cfg.get("arp_path", "/proc/net/arp")),
                )
            )
        return drivers

    def start(self) -> None:
        for driver in self._drivers:
            t = threading.Thread(
                target=driver.run_forever,
                args=(self._on_passport,),
                daemon=True,
                name=f"device-driver:{driver.name}",
            )
            t.start()
            self._threads.append(t)

        self._log_system("device.fabric.started", {"drivers": [d.name for d in self._drivers]})

    def stop(self) -> None:
        for driver in self._drivers:
            driver.stop()
        self._log_system("device.fabric.stopped", {})

    def _on_passport(self, passport: DevicePassport) -> None:
        update = self.registry.upsert(passport)
        event = update.event
        self._emit(event)

    def _emit(self, event: DeviceEvent) -> None:
        # Memory event (structured)
        summary = summarize_event(event)
        try:
            self.memory.log_event("device", summary, context=event.to_dict())
        except Exception:
            pass

        # Policy (integration hooks)
        self.policy.handle(event)

    def _log_system(self, name: str, context: dict[str, Any]) -> None:
        try:
            self.memory.log_event("system", name, context=context)
        except Exception:
            pass

    def _codex_ingest_policy(self, event: DeviceEvent) -> None:
        # Keep Codex ingestion lightweight: summary string only.
        ingest_observation(summarize_event(event))

    def _scroll_hook_policy(self, event: DeviceEvent) -> None:
        """
        Optional bridge into the Scroll subsystem.

        If you later create scrolls like:
        - "device discovered"
        - "device updated"
        this hook can invoke them automatically.
        """
        if not self.scrolls:
            return

        hook_map = {
            "device.discovered": "device discovered",
            "device.updated": "device updated",
            "device.ready": "device ready",
        }
        scroll_name = hook_map.get(event.kind)
        if not scroll_name:
            return

        try:
            # Current ScrollEngine scrolls don't include device hooks yet.
            # This is a forward-compatible integration point.
            self.scrolls.invoke(scroll_name, event.to_dict())
        except Exception:
            return

