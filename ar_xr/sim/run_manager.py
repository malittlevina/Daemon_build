from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class SimRunPaths:
    run_id: str
    run_dir: str


def make_run_dir(base_dir: str = "sandbox/ar_xr_runs", run_id: Optional[str] = None) -> SimRunPaths:
    rid = run_id or f"simrun-{int(time.time())}"
    run_dir = os.path.join(base_dir, rid)
    os.makedirs(run_dir, exist_ok=True)
    return SimRunPaths(run_id=rid, run_dir=run_dir)


def delete_run_dir(run_dir: str) -> None:
    # Only allow deleting within sandbox/ar_xr_runs to avoid accidents.
    norm = os.path.normpath(run_dir)
    if "sandbox/ar_xr_runs" not in norm.replace("\\", "/"):
        raise ValueError(f"Refusing to delete non-run directory: {run_dir}")
    if os.path.exists(run_dir):
        shutil.rmtree(run_dir)

