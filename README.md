python# ThothOS Daemon Build

This is the daemon build (v2_origin), an intelligent AI agent running on ThothOS.

Note: "Prometheus" can be used as the *persona/name* of a specific daemon instance, but the codebase uses "daemon" for system identity to avoid confusion.

## Memory-first “home hub” workflow (devices → home server → sort my day)

This repo now supports a simple pattern:

- **Devices stream events** (and optionally small clips) to your **home daemon server**
- The home server stores them under `memory_tree/`
- At end of day, you run **`sort my day`** to generate a daily digest in `memory_tree/daily/YYYY-MM-DD.md`

### Run the home ingest server

Run this on your home server:

```bash
python3 -m daemon.telemetry_server
```

Health check: `GET /health` on port `8787`.

### Send events from a device

From any device that can reach the server:

```python
from daemon.device_client import send_event

send_event(
    "http://YOUR_HOME_SERVER:8787",
    device_id="phone",
    event_type="note",
    content={"text": "Met Alex for coffee, discussed XR comfort."},
)
```

### End-of-day: “sort my day”

In the daemon CLI, run:

```text
sort my day
```

This generates a digest markdown file like:
- `memory_tree/daily/2026-01-11.md`

### End-of-day: “Memory Garden” (mind palace view)

To render your day as a “memory garden” (themes/plots with memory “seeds”), run:

```text
memory garden
```

This generates:
- `memory_tree/garden/YYYY-MM-DD.md` (human-readable map)
- `memory_tree/garden/YYYY-MM-DD.json` (structured map)

### Interactive Memory Garden (walk / inspect / tag / promote)

The garden also supports an interactive “walk around” workflow (stateful session stored at `memory_tree/garden/session.json`):

```text
garden open
garden plots
garden walk XR Grove
garden seeds 5
garden inspect XR Grove 0
garden tag XR Grove 0 important
garden promote XR Grove 0 daily
garden status
```

Promoted items are appended to `memory_tree/long_term/<category>.jsonl` and also ingested into Codex via `ingest_observation(...)` for later retrieval.

## Core Features
- ✅ **Unimind Reasoning Engine** (brain-based symbolic core)
- ✅ **Voice Listener** (real-time symbolic command parsing)
- ✅ **Scroll Engine** (ritual triggers and symbolic routines)
- ✅ **Emotion Engine** (emotional modeling for interactions)
- ✅ **Prometheus Specialties** (multi-domain skill sets)
- ✅ **Sensor Input** (camera vision + voice ambient tone)
- ✅ **Memory Tree Logger** (life memory timeline system)
- ✅ **Reflection Journal** (self-coding + evolution logs)
- ✅ **Codex Ingestion** (PDF/web summarization knowledge)
- ✅ **Multi-language Code Execution** (Python, Rust, Julia)

## Installation
```bash
git clone https://github.com/andysmomstoys/Daemon_build.git
cd Daemon_build
bash dev/install_mac.sh  # or install_linux.sh
python3 main.py
