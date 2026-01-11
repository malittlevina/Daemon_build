from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]{2,}")


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimpleVectorStore:
    """
    Dependency-free, local "vector store".

    Uses token overlap scoring (not embeddings) so it works offline and deterministically.
    """

    def __init__(self):
        self._docs: List[Document] = []
        self._doc_tokens: List[set[str]] = []

    def add_texts(self, texts: Iterable[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        metas = metadatas or []
        for i, t in enumerate(list(texts)):
            meta = metas[i] if i < len(metas) else {}
            doc = Document(page_content=t, metadata=dict(meta))
            self._docs.append(doc)
            self._doc_tokens.append(set(_tokenize(t)))

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        q_tokens = set(_tokenize(query))
        if not q_tokens:
            return self._docs[:k]

        scored: List[tuple[float, int]] = []
        for idx, tokens in enumerate(self._doc_tokens):
            inter = len(tokens & q_tokens)
            if inter == 0:
                continue
            # a simple normalized score
            denom = math.sqrt(len(tokens) * len(q_tokens)) or 1.0
            score = inter / denom
            scored.append((score, idx))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [self._docs[idx] for _, idx in scored[:k]]

