from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Budget:
    name: str
    limit: float
    used: float = 0.0

    def remaining(self) -> float:
        return max(0.0, self.limit - self.used)

    def charge(self, amount: float) -> bool:
        if amount <= 0:
            return True
        if self.used + amount > self.limit:
            return False
        self.used += amount
        return True


class RateLimiter:
    """
    Token-bucket-ish limiter (very small).
    """

    def __init__(self, rate_per_sec: float, burst: float):
        self.rate_per_sec = float(rate_per_sec)
        self.burst = float(burst)
        self.tokens = float(burst)
        self.last = time.monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()
        elapsed = max(0.0, now - self.last)
        self.last = now
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate_per_sec)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


class ResourceGovernor:
    """
    Hook point for:
    - rate limiting
    - budgets (per action class)
    - timeouts (enforced by call sites later)
    """

    def __init__(self):
        self.budgets: Dict[str, Budget] = {}
        self.limiters: Dict[str, RateLimiter] = {}

    def set_budget(self, name: str, limit: float) -> None:
        self.budgets[name] = Budget(name=name, limit=float(limit))

    def set_rate_limiter(self, name: str, rate_per_sec: float, burst: float) -> None:
        self.limiters[name] = RateLimiter(rate_per_sec=rate_per_sec, burst=burst)

    def charge(self, budget_name: str, amount: float) -> bool:
        b = self.budgets.get(budget_name)
        if not b:
            return True
        return b.charge(amount)

    def allow_rate(self, limiter_name: str, cost: float = 1.0) -> bool:
        lim = self.limiters.get(limiter_name)
        if not lim:
            return True
        return lim.allow(cost=cost)

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        return {
            "budgets": {k: {"limit": v.limit, "used": v.used, "remaining": v.remaining()} for k, v in self.budgets.items()},
            "limiters": {k: {"rate_per_sec": v.rate_per_sec, "burst": v.burst, "tokens": v.tokens} for k, v in self.limiters.items()},
        }

