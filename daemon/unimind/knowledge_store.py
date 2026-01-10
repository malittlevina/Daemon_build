from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _tokens(text: str) -> List[str]:
    toks = re.findall(r"[A-Za-z][A-Za-z0-9_\\-]{2,}", (text or "").lower())
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
        "how",
        "make",
        "build",
        "shape",
        "object",
        "daemon",
        "unimind",
    }
    out: List[str] = []
    seen: Set[str] = set()
    for t in toks:
        if t in stop or t in seen:
            continue
        out.append(t)
        seen.add(t)
        if len(out) >= 32:
            break
    return out


@dataclass(frozen=True)
class ConceptCard:
    """
    Small semantic artifact: definition + parameters + constraints + examples.
    """

    id: str
    title: str
    definition: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)


@dataclass(frozen=True)
class SkillRecipe:
    """
    Procedural artifact: steps + checks + failure modes.
    """

    id: str
    goal: str
    steps: List[str]
    quality_checks: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)


@dataclass(frozen=True)
class PrefabTemplate:
    """
    Reusable world object blueprint with parameter ranges.
    """

    id: str
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)


class KnowledgeStore:
    """
    Durable, compact semantic/procedural store with a simple inverted index.

    Storage:
    - Each artifact is stored as a JSON file under `root`.
    - A lightweight `index.json` supports fast lookup by tags/tokens.
    """

    def __init__(self, root: str = "daemon/unimind/knowledge"):
        self.root = root
        os.makedirs(self.root, exist_ok=True)

        self._concepts: Dict[str, ConceptCard] = {}
        self._recipes: Dict[str, SkillRecipe] = {}
        self._prefabs: Dict[str, PrefabTemplate] = {}

        self._tag_index: Dict[str, Set[str]] = {}
        self._token_index: Dict[str, Set[str]] = {}

        self._load()

    def counts(self) -> Dict[str, int]:
        return {"concepts": len(self._concepts), "recipes": len(self._recipes), "prefabs": len(self._prefabs)}

    def has_tag(self, tag: str) -> bool:
        return bool(self._tag_index.get(tag))

    def iter_all(self) -> List[Dict[str, Any]]:
        """
        Return all artifacts as dicts (for rebuilding the mind palace).
        """
        out: List[Dict[str, Any]] = []
        for c in self._concepts.values():
            out.append({"kind": "concept", **asdict(c)})
        for r in self._recipes.values():
            out.append({"kind": "recipe", **asdict(r)})
        for p in self._prefabs.values():
            out.append({"kind": "prefab", **asdict(p)})
        return out

    # ---- Persistence ----
    def _index_path(self) -> str:
        return os.path.join(self.root, "index.json")

    def _artifact_path(self, kind: str, artifact_id: str) -> str:
        safe = artifact_id.replace("/", "_")
        return os.path.join(self.root, f"{kind}__{safe}.json")

    def _load(self) -> None:
        # Load artifacts
        for name in os.listdir(self.root):
            if not name.endswith(".json"):
                continue
            if name == "index.json":
                continue
            path = os.path.join(self.root, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue

            if name.startswith("concept__"):
                try:
                    self._concepts[data["id"]] = ConceptCard(**data)
                except Exception:
                    continue
            elif name.startswith("recipe__"):
                try:
                    self._recipes[data["id"]] = SkillRecipe(**data)
                except Exception:
                    continue
            elif name.startswith("prefab__"):
                try:
                    self._prefabs[data["id"]] = PrefabTemplate(**data)
                except Exception:
                    continue

        # Load index if present; otherwise rebuild.
        try:
            with open(self._index_path(), "r", encoding="utf-8") as f:
                idx = json.load(f)
            self._tag_index = {k: set(v) for k, v in (idx.get("tags") or {}).items()}
            self._token_index = {k: set(v) for k, v in (idx.get("tokens") or {}).items()}
        except Exception:
            self._rebuild_index()

    def _save_index(self) -> None:
        idx = {
            "updated_at": _now(),
            "tags": {k: sorted(list(v)) for k, v in self._tag_index.items()},
            "tokens": {k: sorted(list(v)) for k, v in self._token_index.items()},
        }
        with open(self._index_path(), "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, indent=2)

    def _write_artifact(self, kind: str, artifact: Any) -> None:
        path = self._artifact_path(kind, artifact.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(artifact), f, ensure_ascii=False, indent=2)

    def _rebuild_index(self) -> None:
        self._tag_index.clear()
        self._token_index.clear()
        for a in list(self._concepts.values()) + list(self._recipes.values()) + list(self._prefabs.values()):
            self._index_artifact(a)
        self._save_index()

    # ---- Indexing ----
    def _index_artifact(self, artifact: Any) -> None:
        aid = str(getattr(artifact, "id"))
        tags = list(getattr(artifact, "tags", []) or [])
        text_parts = []
        for k in ("title", "definition", "goal", "name", "description"):
            v = getattr(artifact, k, None)
            if isinstance(v, str) and v:
                text_parts.append(v)
        for k in ("steps", "constraints", "quality_checks", "failure_modes", "examples", "related"):
            v = getattr(artifact, k, None)
            if isinstance(v, list) and v:
                text_parts.append(" ".join([str(x) for x in v[:12]]))
        text = " ".join(text_parts)

        for t in tags:
            self._tag_index.setdefault(t, set()).add(aid)
        for tok in _tokens(text):
            self._token_index.setdefault(tok, set()).add(aid)

    # ---- Public API: upserts ----
    def upsert_concept(self, card: ConceptCard) -> ConceptCard:
        existing = self._concepts.get(card.id)
        if existing:
            merged_examples = list(dict.fromkeys((existing.examples + card.examples)))[-10:]
            merged_related = list(dict.fromkeys((existing.related + card.related)))[-20:]
            merged_tags = list(dict.fromkeys((existing.tags + card.tags)))[-30:]
            merged_constraints = list(dict.fromkeys((existing.constraints + card.constraints)))[-20:]
            merged_params = existing.parameters if existing.parameters else card.parameters
            card = ConceptCard(
                id=existing.id,
                title=card.title or existing.title,
                definition=card.definition or existing.definition,
                parameters=merged_params,
                constraints=merged_constraints,
                related=merged_related,
                tags=merged_tags,
                examples=merged_examples,
                created_at=existing.created_at,
                updated_at=_now(),
            )
        self._concepts[card.id] = card
        self._index_artifact(card)
        self._write_artifact("concept", card)
        self._save_index()
        return card

    def upsert_recipe(self, recipe: SkillRecipe) -> SkillRecipe:
        existing = self._recipes.get(recipe.id)
        if existing:
            recipe = SkillRecipe(
                id=existing.id,
                goal=recipe.goal or existing.goal,
                steps=(recipe.steps or existing.steps)[:30],
                quality_checks=list(dict.fromkeys((existing.quality_checks + recipe.quality_checks)))[-20:],
                failure_modes=list(dict.fromkeys((existing.failure_modes + recipe.failure_modes)))[-20:],
                tags=list(dict.fromkeys((existing.tags + recipe.tags)))[-30:],
                created_at=existing.created_at,
                updated_at=_now(),
            )
        self._recipes[recipe.id] = recipe
        self._index_artifact(recipe)
        self._write_artifact("recipe", recipe)
        self._save_index()
        return recipe

    def upsert_prefab(self, prefab: PrefabTemplate) -> PrefabTemplate:
        existing = self._prefabs.get(prefab.id)
        if existing:
            prefab = PrefabTemplate(
                id=existing.id,
                name=prefab.name or existing.name,
                description=prefab.description or existing.description,
                parameters={**existing.parameters, **(prefab.parameters or {})},
                tags=list(dict.fromkeys((existing.tags + prefab.tags)))[-30:],
                created_at=existing.created_at,
                updated_at=_now(),
            )
        self._prefabs[prefab.id] = prefab
        self._index_artifact(prefab)
        self._write_artifact("prefab", prefab)
        self._save_index()
        return prefab

    # ---- Public API: retrieval ----
    def get(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        if artifact_id in self._concepts:
            return {"kind": "concept", **asdict(self._concepts[artifact_id])}
        if artifact_id in self._recipes:
            return {"kind": "recipe", **asdict(self._recipes[artifact_id])}
        if artifact_id in self._prefabs:
            return {"kind": "prefab", **asdict(self._prefabs[artifact_id])}
        return None

    def search(self, query: str, *, tags: Sequence[str] | None = None, top_k: int = 5) -> List[Dict[str, Any]]:
        tags = list(tags or [])
        q_tokens = _tokens(query or "")
        candidates: Set[str] = set()

        # Tag filtering (prefer intersection; fall back to union if too restrictive).
        tag_candidates: Optional[Set[str]] = None
        if tags:
            for t in tags:
                ids = set(self._tag_index.get(t, set()))
                tag_candidates = ids if tag_candidates is None else (tag_candidates & ids)
            if not tag_candidates:
                # fall back to union across tags
                tag_candidates = set()
                for t in tags:
                    tag_candidates |= set(self._tag_index.get(t, set()))

        if tag_candidates:
            candidates = set(tag_candidates)

        # Token candidates as a union (used for ranking, and optionally as a filter).
        token_union: Set[str] = set()
        for tok in q_tokens[:8]:
            token_union |= set(self._token_index.get(tok, set()))

        if not candidates:
            candidates = set(token_union)
        elif token_union:
            # Light filter (one-shot), not repeated intersections.
            candidates = candidates & token_union or candidates

        # Rank: simple overlap score
        results: List[Tuple[int, str]] = []
        for aid in candidates:
            a = self.get(aid)
            if not a:
                continue
            blob = json.dumps(a, ensure_ascii=False).lower()
            score = sum(1 for tok in q_tokens[:10] if tok in blob)
            if score > 0:
                results.append((score, aid))

        results.sort(key=lambda x: (-x[0], x[1]))
        out: List[Dict[str, Any]] = []
        for _, aid in results[:top_k]:
            a = self.get(aid)
            if a:
                out.append(a)
        return out

