from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class CodexHit:
    path: str
    line_no: int
    line: str


class CodexIndex:
    """
    Lightweight, dependency-free Codex index.

    The repository contains multiple Codex implementations; some are incomplete
    (e.g., vector store references). This index intentionally avoids external
    dependencies and simply searches local `codex/data` files.
    """

    def __init__(self, root: str = "codex/data"):
        self.root = root
        self._cache: Dict[str, List[str]] = {}

    def _iter_files(self) -> Iterable[str]:
        if not os.path.isdir(self.root):
            return []
        for name in os.listdir(self.root):
            path = os.path.join(self.root, name)
            if os.path.isfile(path) and any(path.endswith(ext) for ext in (".txt", ".md", ".json")):
                yield path

    def _read_lines(self, path: str) -> List[str]:
        if path in self._cache:
            return self._cache[path]
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
        except Exception:
            lines = []
        self._cache[path] = lines
        return lines

    def search(self, query: str, max_hits: int = 20) -> List[CodexHit]:
        if not query:
            return []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        hits: List[CodexHit] = []
        for path in self._iter_files():
            lines = self._read_lines(path)
            for i, line in enumerate(lines, start=1):
                if pattern.search(line):
                    hits.append(CodexHit(path=path, line_no=i, line=line.strip()))
                    if len(hits) >= max_hits:
                        return hits
        return hits

    def snippet_around(self, hit: CodexHit, window: int = 2) -> str:
        lines = self._read_lines(hit.path)
        start = max(0, hit.line_no - 1 - window)
        end = min(len(lines), hit.line_no + window)
        chunk = lines[start:end]
        return "\n".join(chunk)

    def top_terms_from_snippets(self, snippets: List[str], max_terms: int = 20) -> List[str]:
        """
        Extract candidate terms from snippets for concept expansion.
        """
        text = "\n".join(snippets)
        tokens = re.findall(r"[A-Za-z][A-Za-z0-9_\\-]{2,}", text)
        stop = {
            "the",
            "and",
            "for",
            "with",
            "this",
            "that",
            "from",
            "into",
            "your",
            "you",
            "are",
            "was",
            "were",
            "will",
            "can",
            "not",
            "but",
            "all",
            "any",
            "its",
            "our",
        }
        freq: Dict[str, int] = {}
        for t in tokens:
            k = t.lower()
            if k in stop:
                continue
            freq[k] = freq.get(k, 0) + 1
        # Return original-lowercase unique terms sorted by frequency
        return [k for k, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:max_terms]]

    def search_snippets(self, query: str, max_hits: int = 10, window: int = 2) -> Tuple[List[CodexHit], List[str]]:
        hits = self.search(query, max_hits=max_hits)
        snippets = [self.snippet_around(h, window=window) for h in hits]
        return hits, snippets
