python# ThothOS Daemon Build (Prometheus)

This is the official Prometheus daemon build (v2_origin), an intelligent AI agent running on ThothOS. It includes:

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
- ✅ **Storyrealms (World Engine)** (event-sourced realm state + deterministic replay)

## Storyrealms (World Engine)
Storyrealms is the canonical "world engine" subsystem (`storyrealms/`). It provides:
- event-sourced realm state (append-only log + snapshots)
- deterministic replay for debugging/time-travel
- soft integrations into memory logging and scroll triggers

Minimal usage (Python):

```python
from storyrealms import StoryrealmsService

svc = StoryrealmsService()
svc.enter_realm("alpha", actor="user")
svc.emit_event("entity.upsert", {"entity_id": "npc:1", "data": {"name": "Ira"}})
print(svc.query_state())
```

## Installation
```bash
git clone https://github.com/andysmomstoys/Daemon_build.git
cd Daemon_build
bash dev/install_mac.sh  # or install_linux.sh
python3 main.py
