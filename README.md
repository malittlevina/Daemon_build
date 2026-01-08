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

## Cross-Platform & ThothOS Integration
The daemon is designed to run on any operating system (Linux, macOS, Windows) in a "Guest Mode" with standard capabilities.

However, when running on **ThothOS** (native environment), the daemon detects the native bridge and activates:
- **High-Performance Profile**: Unrestricted resource usage and deeper system integration.
- **ThothBridge**: Direct communication with the OS kernel and registered apps.
- **Native Optimization**: Enhanced self-optimization routines.

To simulate the native environment for testing, set `THOTH_OS_ACTIVE=1`.

## Installation
```bash
git clone https://github.com/andysmomstoys/Daemon_build.git
cd Daemon_build
bash dev/install_mac.sh  # or install_linux.sh
python3 main.py
