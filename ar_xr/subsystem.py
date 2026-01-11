import os
import subprocess
from typing import Any, Dict, List, Optional

from ar_xr.app_registry import ARXRAppRegistry
from ar_xr.training import build_training_plan, load_training_modules, start_training_session


class ARXRSubsystem:
    """
    Facade for AR/XR capabilities.

    Design goals:
    - Keep side effects explicit (launch, logs)
    - Record actions into memory/codex when available
    - Integrate with symbolic state when available
    """

    def __init__(
        self,
        app_registry: Optional[ARXRAppRegistry] = None,
        ingest_observation=None,
        log_memory=None,
        update_symbolic_state=None,
    ):
        self.apps = app_registry or ARXRAppRegistry()
        self._ingest_observation = ingest_observation
        self._log_memory = log_memory
        self._update_symbolic_state = update_symbolic_state

    def _record(self, event_type: str, content: Any, context: Optional[Dict[str, Any]] = None) -> None:
        ctx = dict(context or {})
        ctx["subsystem"] = "ar_xr"
        ctx["event_type"] = event_type

        if callable(self._update_symbolic_state):
            try:
                self._update_symbolic_state(f"[ar_xr:{event_type}] {content}")
            except Exception:
                pass

        if callable(self._ingest_observation):
            try:
                self._ingest_observation({"type": f"ar_xr.{event_type}", "content": content, "context": ctx})
            except Exception:
                pass

        if callable(self._log_memory):
            try:
                self._log_memory(content, context=ctx)
            except Exception:
                pass

    def list_apps(self, kind: Optional[str] = None) -> Dict[str, Any]:
        apps = self.apps.list_apps(kind=kind)
        result = {
            "ok": True,
            "kind": kind,
            "apps": [{"id": a.get("id"), "name": a.get("name"), "kind": a.get("kind"), "runtime": a.get("runtime")} for a in apps],
        }
        self._record("list_apps", result, context={"kind": kind, "count": len(apps)})
        return result

    def launch_app(self, app_name_or_id: str, dry_run: bool = True) -> Dict[str, Any]:
        app = self.apps.get_by_id(app_name_or_id) or self.apps.find_by_name(app_name_or_id)
        if not app:
            result = {"ok": False, "error": f"Unknown AR/XR app: {app_name_or_id}"}
            self._record("launch_app_failed", result, context={"query": app_name_or_id})
            return result

        launch = app.get("launch") or {}
        launch_type = launch.get("type")
        value = launch.get("value")

        intent = {"app": {"id": app.get("id"), "name": app.get("name")}, "launch": launch, "dry_run": dry_run}
        self._record("launch_app_intent", intent, context={"runtime": app.get("runtime"), "kind": app.get("kind")})

        if dry_run:
            return {"ok": True, "dry_run": True, "intent": intent, "note": "Dry-run enabled; not executing launch."}

        # Best-effort launching (may not work in headless environments).
        try:
            if launch_type == "command" and isinstance(value, str):
                proc = subprocess.run(value.split(), capture_output=True, text=True)
                result = {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}
                self._record("launch_app_command", result, context={"cmd": value})
                return result

            if launch_type == "url" and isinstance(value, str):
                # Prefer xdg-open on Linux.
                proc = subprocess.run(["xdg-open", value], capture_output=True, text=True)
                result = {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode}
                self._record("launch_app_url", result, context={"url": value})
                return result

            result = {"ok": False, "error": f"Unsupported launch type: {launch_type}"}
            self._record("launch_app_failed", result, context={"launch": launch})
            return result
        except FileNotFoundError as e:
            result = {"ok": False, "error": f"Launcher not available: {e}"}
            self._record("launch_app_failed", result, context={"launch": launch})
            return result
        except Exception as e:
            result = {"ok": False, "error": f"Launch failed: {e}"}
            self._record("launch_app_failed", result, context={"launch": launch})
            return result

    def start_training(self, goal: str, kind: str = "xr") -> Dict[str, Any]:
        modules = load_training_modules()
        plan = build_training_plan(goal=goal or "XR fundamentals", kind=kind, modules=modules)
        session = start_training_session(plan)
        self._record("training_started", session, context={"goal": goal, "kind": kind})
        return {"ok": True, "session": session}

