from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from kernel.identity import Principal


ActionFn = Callable[[Dict[str, Any], Principal], Dict[str, Any]]


@dataclass(frozen=True)
class ActionSpec:
    name: str
    description: str
    args_schema: Dict[str, Any] = field(default_factory=dict)
    required_caps: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    fn: Optional[ActionFn] = None

