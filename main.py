"""
Daemon entrypoint.

`main.py` is intentionally *not* the Unimind kernel. The kernel lives in `unimind/`.
This file only launches the daemon application loop (I/O + routing).
"""

from daemon.app import run_daemon


if __name__ == "__main__":
    run_daemon(
        use_ollama=False,
        enable_textbox=True,
        enable_mic=False,
        enable_camera=False,
    )