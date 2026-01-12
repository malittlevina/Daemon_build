# bridge/memory_tree_interface.py

class MemoryTreeInterface:
    def __init__(self, memory_logger):
        self.memory_logger = memory_logger
        print("[MemoryTreeInterface] Connected to symbolic memory engine.")

    def plant_memory_seed(self, content: str, tags: list = None, context: str = None):
        print(f"[MemoryTree] Planting memory seed: {content}")
        print(f"[MemoryTree] Tags: {tags}")
        self.memory_logger.log_memory(content, tags=tags or [], context=context)

    def fetch_memories(self, query: str):
        print(f"[MemoryTree] Searching for: {query}")
        # You can expand this in future to support fuzzy/symbolic search
        return self.memory_logger.retrieve_log()

    def summarize_memories(self):
        # Optional method for summarizing memory logs
        log = self.memory_logger.retrieve_log()
        return [m[:100] + "..." if len(m) > 100 else m for m in log]
