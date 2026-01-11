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
- ✅ **Robotics Control (Simulation-first)** (safe-by-default driver interface)

## Robotics (long-term hardware goal, usable today in simulation)
Robotics control is implemented as a modular subsystem (`robotics/`) with a driver interface.
Right now it runs in **simulation mode** so you can develop command routing before you build hardware.

### Commands (in the daemon CLI)
- `robot status`
- `robot arm` (required before motion/follow)
- `robot follow me`
- `robot move forward 0.5`
- `robot stop`

Driver selection lives in `config/robotics.json` (currently only `simulation` is implemented).

## Installation
```bash
git clone https://github.com/andysmomstoys/Daemon_build.git
cd Daemon_build
bash dev/install_mac.sh  # or install_linux.sh
python3 main.py
