# ThothOS Daemon Build (Prometheus)

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

## Installation
```bash
git clone https://github.com/andysmomstoys/Daemon_build.git
cd Daemon_build
bash dev/install_mac.sh  # or install_linux.sh
python3 main.py
```

## OS Compatibility + ThothOS Preference
The daemon is designed to run on **any OS** in a safe compatibility mode, but it will **prefer/prioritize ThothOS** when detected.

- **ThothOS detection**: any of the following markers will enable native mode:
  - env var: `THOTHOS` / `THOTH_OS` / `THOTHOS_NATIVE`
  - repo file: `.thothos` or `config/thothos.json`
  - system path: `/etc/thothos-release` or `/etc/thothos/thothos.json`
- **Compatibility mode (non-ThothOS)**: by default, heavier integrations (voice/camera/auto-optimization) are disabled to keep the daemon portable.
- **Override**: set `config/daemon_config.json` → `os_preference.allow_full_features_on_non_preferred_os=true` to force full features on other OSes.
