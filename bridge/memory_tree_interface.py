from __future__ import annotations

from typing import Any, Dict, List, Optional

class MemoryTreeInterface:
    def __init__(self, memory_logger):
        self.memory_logger = memory_logger
        print("[MemoryTreeInterface] Connected to symbolic memory engine.")

    def plant_memory_seed(self, content: str, tags: list = None, context: str = None):
        print(f"[MemoryTree] Planting memory seed: {content}")
        print(f"[MemoryTree] Tags: {tags}")
        tags = tags or []
        ctx: Dict[str, Any]
        if isinstance(context, dict):
            ctx = dict(context)
        else:
            ctx = {"context": context} if context else {}
        ctx["tags"] = list(tags)

        # Support either module-level helpers or a MemoryLogger instance.
        if hasattr(self.memory_logger, "log_event"):
            self.memory_logger.log_event("memory", content, context=ctx)
        elif hasattr(self.memory_logger, "log_memory"):
            try:
                self.memory_logger.log_memory(content, context=ctx)
            except TypeError:
                # Older signature variants.
                self.memory_logger.log_memory(content)
        else:
            try:
                from memory_tree.memory_logger import log_memory  # type: ignore
                log_memory(content, context=ctx)
            except Exception:
                return

    def fetch_memories(self, query: str):
        print(f"[MemoryTree] Searching for: {query}")
        # You can expand this in future to support fuzzy/symbolic search
        if hasattr(self.memory_logger, "get_latest_events"):
            return self.memory_logger.get_latest_events(50)
        if hasattr(self.memory_logger, "retrieve_log"):
            return self.memory_logger.retrieve_log()
        try:
            from memory_tree.memory_logger import retrieve_log  # type: ignore
            return retrieve_log()
        except Exception:
            return []

    def summarize_memories(self):
        # Optional method for summarizing memory logs
        log = self.fetch_memories(query="*")
        return [m[:100] + "..." if len(m) > 100 else m for m in log]
