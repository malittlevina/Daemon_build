from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from core.event_bus import EventBus, GLOBAL_EVENT_BUS
from kernel.actions import ActionSpec
from kernel.capabilities import CapabilityManager
from kernel.identity import Principal
from kernel.messages import MessageBus
from kernel.policy import PolicyEngine
from kernel.resources import ResourceGovernor
from kernel.scheduler import Scheduler
from kernel.services import Service, ServiceInfo, ServiceRegistry


class Kernel:
    """
    Minimal kernel for the daemon:
    - services (registry + basic lifecycle hooks)
    - actions (uniform invocation surface)
    - policy + capabilities
    - resource governor hooks
    - IPC (message bus)
    - scheduler (tick-based)
    - observability (event bus)
    """

    def __init__(self, *, event_bus: EventBus = GLOBAL_EVENT_BUS):
        self.event_bus = event_bus
        self.services = ServiceRegistry()
        self.bus = MessageBus()
        self.scheduler = Scheduler()
        self.caps = CapabilityManager()
        self.policy = PolicyEngine(event_bus)
        self.resources = ResourceGovernor()
        self._actions: Dict[str, ActionSpec] = {}

    def register_service(self, info: ServiceInfo, svc: Service) -> None:
        self.services.register(info, svc)
        self.event_bus.publish(
            "kernel.service.register",
            {"service": asdict(info)},
            source="kernel",
            tags=["kernel", "services"],
        )

    def register_action(self, spec: ActionSpec) -> None:
        if not spec.fn:
            raise ValueError(f"Action '{spec.name}' missing fn")
        self._actions[spec.name] = spec
        self.event_bus.publish(
            "kernel.action.register",
            {"name": spec.name, "required_caps": spec.required_caps, "tags": spec.tags},
            source="kernel",
            tags=["kernel", "actions"],
        )

    def list_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": a.name,
                "description": a.description,
                "args_schema": a.args_schema,
                "required_caps": a.required_caps,
                "tags": a.tags,
            }
            for a in self._actions.values()
        ]

    def invoke(self, name: str, args: Optional[Dict[str, Any]] = None, *, principal: Optional[Principal] = None, trace_id: Optional[str] = None) -> Dict[str, Any]:
        if name not in self._actions:
            raise ValueError(f"Unknown action: {name}")
        principal = principal or Principal(id="ui", kind="ui", roles=["ui"])
        spec = self._actions[name]

        # Policy gate (roles/tags)
        decision = self.policy.decide(principal=principal, action=name, tags=spec.tags, trace_id=trace_id)
        if not decision.allow:
            self.event_bus.publish(
                "kernel.action.denied",
                {"name": name, "reason": decision.reason, "principal": {"id": principal.id, "kind": principal.kind, "roles": principal.roles}, "trace_id": trace_id},
                source="kernel",
                severity="error",
                tags=["kernel", "actions"] + ([f"trace:{trace_id}"] if trace_id else []),
            )
            raise PermissionError(decision.reason)

        # Capability gate
        if not self.caps.has_all(principal, spec.required_caps):
            self.event_bus.publish(
                "kernel.action.denied",
                {"name": name, "reason": "missing_capability", "required_caps": spec.required_caps, "principal": {"id": principal.id, "kind": principal.kind}, "trace_id": trace_id},
                source="kernel",
                severity="error",
                tags=["kernel", "actions"] + ([f"trace:{trace_id}"] if trace_id else []),
            )
            raise PermissionError("missing_capability")

        # Rate limit hook (by action name)
        if not self.resources.allow_rate(f"action:{name}", cost=1.0):
            self.event_bus.publish(
                "kernel.action.rate_limited",
                {"name": name, "trace_id": trace_id},
                source="kernel",
                severity="error",
                tags=["kernel", "resources"] + ([f"trace:{trace_id}"] if trace_id else []),
            )
            raise RuntimeError("rate_limited")

        self.event_bus.publish(
            "kernel.action.invoke",
            {"name": name, "args": args or {}, "principal": {"id": principal.id, "kind": principal.kind}, "trace_id": trace_id},
            source="kernel",
            tags=["kernel", "actions"] + ([f"trace:{trace_id}"] if trace_id else []),
        )
        out = spec.fn(args or {}, principal)
        self.event_bus.publish(
            "kernel.action.result",
            {"name": name, "result": out, "trace_id": trace_id},
            source="kernel",
            tags=["kernel", "actions"] + ([f"trace:{trace_id}"] if trace_id else []),
        )
        return out

    def tick(self) -> None:
        ran = self.scheduler.run_due()
        if ran:
            self.event_bus.publish("kernel.scheduler.ran", {"count": len(ran)}, source="kernel", tags=["kernel", "scheduler"])

    def snapshot_state(self) -> Dict[str, Any]:
        svc_states: Dict[str, Any] = {}
        for info in self.services.list():
            svc = self.services.get(info.name)
            state: Dict[str, Any] = {}
            if svc and hasattr(svc, "state"):
                try:
                    state = svc.state()  # type: ignore[misc]
                except Exception as e:
                    state = {"error": str(e)}
            svc_states[info.name] = {"info": asdict(info), "state": state}

        return {
            "kernel": {
                "services": svc_states,
                "actions": self.list_actions(),
                "capabilities": self.caps.snapshot(),
                "resources": self.resources.snapshot(),
                "scheduler": self.scheduler.list(),
            }
        }

    def world_model(self) -> Dict[str, Any]:
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        def add_node(node_id: str, label: str, kind: str, meta: Optional[Dict[str, Any]] = None) -> None:
            nodes.append({"id": node_id, "label": label, "kind": kind, "meta": meta or {}})

        def add_edge(src: str, dst: str, rel: str) -> None:
            edges.append({"from": src, "to": dst, "rel": rel})

        add_node("kernel:core", "Kernel", "kernel")
        add_node("kernel:ipc", "MessageBus", "ipc")
        add_node("kernel:scheduler", "Scheduler", "scheduler")
        add_node("kernel:policy", "PolicyEngine", "policy")
        add_node("kernel:caps", "CapabilityManager", "capabilities")
        add_node("kernel:resources", "ResourceGovernor", "resources")
        add_node("events:bus", "EventBus", "events")

        add_edge("kernel:core", "kernel:ipc", "owns")
        add_edge("kernel:core", "kernel:scheduler", "owns")
        add_edge("kernel:core", "kernel:policy", "owns")
        add_edge("kernel:core", "kernel:caps", "owns")
        add_edge("kernel:core", "kernel:resources", "owns")
        add_edge("kernel:core", "events:bus", "publishes_events_to")

        for info in self.services.list():
            sid = f"service:{info.name}"
            add_node(sid, info.name, info.kind, meta=info.meta)
            add_edge("kernel:core", sid, "registers")
            for dep in info.depends_on:
                add_edge(sid, f"service:{dep}", "depends_on")

        for a in self._actions.values():
            aid = f"action:{a.name}"
            add_node(aid, a.name, "action", meta={"required_caps": a.required_caps, "tags": a.tags})
            add_edge("kernel:core", aid, "exposes")

        return {"version": "0.1", "nodes": nodes, "edges": edges}

