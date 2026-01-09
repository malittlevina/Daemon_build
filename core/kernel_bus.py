from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from core.kernel_types import KernelMessage, KernelResult


FilterFn = Callable[[KernelMessage], bool]
HandlerFn = Callable[[KernelMessage], Optional[KernelResult]]


@dataclass(slots=True)
class KernelBus:
    """
    In-process pub/sub bus for kernel messages.
    """

    _subs: List[Tuple[FilterFn, HandlerFn]] = field(default_factory=list)

    def subscribe(self, filt: FilterFn, handler: HandlerFn) -> None:
        self._subs.append((filt, handler))

    def publish(self, msg: KernelMessage) -> List[KernelResult]:
        results: List[KernelResult] = []
        for filt, handler in list(self._subs):
            try:
                if not filt(msg):
                    continue
                out = handler(msg)
                if out is not None:
                    results.append(out)
            except Exception as e:
                results.append(KernelResult(ok=False, error=str(e)))
        return results

