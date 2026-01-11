from __future__ import annotations

from typing import Any, Optional

from unimind.context import UnimindContext


class ScrollRouterModule:
    """
    Logic/action router: maps common patterns to ScrollEngine invocations.

    This ensures non-XR actions still travel through the same Unimind pipeline.
    """

    def __init__(self, scroll_engine):
        self.scrolls = scroll_engine

    def process(self, user_input: str, context: UnimindContext) -> Optional[Any]:
        text = (user_input or "").strip()
        text_l = text.lower()

        intent = context.get("intent")
        if isinstance(intent, dict) and intent.get("intent", "").startswith("xr."):
            name = intent.get("intent")
            context.emit("intent_execute", intent)
            if name == "xr.list_apps":
                return self.scrolls.invoke("xr list apps")
            if name == "xr.launch_app":
                return self.scrolls.invoke("xr launch app", intent.get("app"), intent.get("dry_run", True))
            if name == "xr.create_world":
                return self.scrolls.invoke("xr create world", intent.get("goal"), intent.get("kind", "xr"))
            if name == "xr.train_sim":
                return self.scrolls.invoke(
                    "xr train sim",
                    intent.get("goal"),
                    intent.get("kind", "xr"),
                    intent.get("steps", 300),
                    intent.get("delete_raw_run", True),
                )

        if isinstance(intent, dict) and intent.get("intent") == "memory.sort_day":
            context.emit("intent_execute", intent)
            return self.scrolls.invoke("sort my day", intent.get("day"))

        if isinstance(intent, dict) and intent.get("intent") == "memory.garden":
            context.emit("intent_execute", intent)
            return self.scrolls.invoke("memory garden", intent.get("day"))

        if isinstance(intent, dict) and intent.get("intent", "").startswith("garden."):
            context.emit("intent_execute", intent)
            name = intent.get("intent")
            if name == "garden.status":
                return self.scrolls.invoke("garden status")
            if name == "garden.open":
                return self.scrolls.invoke("garden open", intent.get("day"))
            if name == "garden.plots":
                return self.scrolls.invoke("garden plots", intent.get("day"))
            if name == "garden.walk":
                return self.scrolls.invoke("garden walk", intent.get("plot"))
            if name == "garden.seeds":
                return self.scrolls.invoke("garden seeds", intent.get("plot"), intent.get("limit", 10))
            if name == "garden.inspect":
                if intent.get("error"):
                    return f"[Garden] {intent.get('error')}"
                return self.scrolls.invoke("garden inspect", intent.get("plot"), intent.get("index"))
            if name == "garden.tag":
                if intent.get("error"):
                    return f"[Garden] {intent.get('error')}"
                return self.scrolls.invoke("garden tag", intent.get("plot"), intent.get("index"), intent.get("tag"))
            if name == "garden.promote":
                if intent.get("error"):
                    return f"[Garden] {intent.get('error')}"
                return self.scrolls.invoke(
                    "garden promote", intent.get("plot"), intent.get("index"), intent.get("category", "general")
                )
            return "[Garden] Unknown garden intent."

        if isinstance(intent, dict) and intent.get("intent", "").startswith("app."):
            context.emit("intent_execute", intent)
            name = intent.get("intent")
            if name == "app.list":
                return self.scrolls.invoke("app list")
            if name == "app.info":
                return self.scrolls.invoke("app info", intent.get("app_id"))
            if name == "app.scaffold":
                return self.scrolls.invoke("app scaffold", intent.get("app_id"))
            if name == "app.run":
                if intent.get("error"):
                    return f"[App] {intent.get('error')}"
                return self.scrolls.invoke(
                    "app run",
                    intent.get("app_id"),
                    intent.get("action", "default"),
                    intent.get("params", {}),
                    intent.get("dry_run", True),
                )
            return "[App] Unknown app intent."

        # If NLU already produced a non-trivial result, don't override it.
        nlu_result = context.get("nlu_result")
        if nlu_result is not None and not (
            isinstance(nlu_result, str) and nlu_result.startswith("[NLUEngine] No known intent")
        ):
            return None

        if text_l == "optimize self":
            context.emit("scroll_invoke", {"name": "optimize self"})
            return self.scrolls.invoke("optimize self")

        if text_l.startswith("run task "):
            desc = text[9:].strip()
            context.emit("scroll_invoke", {"name": "run task", "task": desc})
            return self.scrolls.invoke("run task", desc)

        if text_l.startswith("multi step plan "):
            goal = text[len("multi step plan ") :].strip()
            context.emit("scroll_invoke", {"name": "multi step plan", "goal": goal})
            return self.scrolls.invoke("multi step plan", goal)

        if text_l.startswith("study topic "):
            topic = text[len("study topic ") :].strip()
            context.emit("scroll_invoke", {"name": "study topic", "topic": topic})
            return self.scrolls.invoke("study topic", topic)

        if text_l.startswith("study "):
            topic = text[len("study ") :].strip()
            context.emit("scroll_invoke", {"name": "study topic", "topic": topic})
            return self.scrolls.invoke("study topic", topic)

        return None

