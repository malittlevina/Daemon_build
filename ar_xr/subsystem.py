import os
import subprocess
from typing import Any, Dict, List, Optional

from ar_xr.app_registry import ARXRAppRegistry
from ar_xr.sim.distiller import distill_run, write_knowledge
from ar_xr.sim.learner import ThrustGainSearchLearner
from ar_xr.sim.run_manager import delete_run_dir, make_run_dir
from ar_xr.sim.simulator import run_headless_episode
from ar_xr.sim.world import WorldSpec, synthesize_world
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

    def create_world(self, goal: str, kind: str = "xr", world_id: Optional[str] = None) -> Dict[str, Any]:
        world = synthesize_world(goal=goal, kind=kind, world_id=world_id)
        self._record("world_created", world.to_dict(), context={"goal": goal, "kind": kind, "world_id": world.world_id})
        return {"ok": True, "world": world.to_dict()}

    def simulate_train_distill(
        self,
        goal: str,
        kind: str = "xr",
        steps: int = 300,
        delete_raw_run: bool = True,
        episodes: int = 1,
    ) -> Dict[str, Any]:
        """
        Core loop you described:
        - create a world
        - place the daemon-agent in it (agent_body entity)
        - simulate
        - distill durable knowledge (heuristics + keyframes)
        - delete raw run artifacts (trajectory)
        """
        world = synthesize_world(goal=goal, kind=kind)

        # Run one or more episodes. If multiple, keep the best and delete the rest.
        episodes_i = max(1, int(episodes))
        best_run_summary = None
        best_trajectory_path = None
        best_run_dir = None
        best_gain = None
        episode_dirs: list[str] = []

        def _run_episode(policy=None):
            rp = make_run_dir()
            episode_dirs.append(rp.run_dir)
            return run_headless_episode(world=world, steps=steps, run_dir=rp.run_dir, policy=policy)

        if episodes_i == 1:
            sim = _run_episode(policy=None)
            best_run_summary = sim["run"]
            best_trajectory_path = sim["trajectory_path"]
            best_run_dir = sim["run"]["run_dir"]
        else:
            learner = ThrustGainSearchLearner()
            # Respect requested episode count by limiting gain trials.
            learner.gains = learner.gains[:episodes_i]
            best, all_eps = learner.run(world, run_episode=_run_episode)
            best_gain = best.gain
            best_run_summary = best.run
            best_trajectory_path = best.trajectory_path
            best_run_dir = best.run.get("run_dir")

        knowledge = distill_run(world=world, run=best_run_summary, trajectory_path=best_trajectory_path)
        # annotate with learner selection if used
        if best_gain is not None:
            knowledge.params["learner"] = {"type": "thrust_gain_search", "best_gain": best_gain, "episodes": episodes_i}
        knowledge_paths = write_knowledge(knowledge)

        self._record(
            "sim_distilled",
            {"knowledge": knowledge.to_dict(), "knowledge_paths": knowledge_paths},
            context={"world_id": world.world_id, "run_id": best_run_summary.get("run_id")},
        )

        if delete_raw_run:
            for d in sorted(set(episode_dirs or ([] if not best_run_dir else [best_run_dir]))):
                try:
                    delete_run_dir(d)
                    self._record("sim_run_deleted", {"run_dir": d}, context={"run_id": best_run_summary.get("run_id")})
                except Exception as e:
                    self._record("sim_run_delete_failed", {"run_dir": d, "error": str(e)})

        return {
            "ok": True,
            "world": world.to_dict(),
            "run": best_run_summary,
            "knowledge_paths": knowledge_paths,
            "deleted_raw_run": bool(delete_raw_run),
            "episodes": episodes_i,
            "best_gain": best_gain,
        }

