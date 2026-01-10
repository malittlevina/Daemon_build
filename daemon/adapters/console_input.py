from __future__ import annotations

import threading
from typing import Optional

from daemon.event_bus import EventBus
from daemon.events import DaemonEvent


def start_console_input(bus: EventBus, *, prompt: str = "\n[Daemon] Type here (or 'exit'): ") -> threading.Thread:
    """
    Console input adapter that publishes `text_input` events.
    Runs in a background thread so the main loop can remain event-driven.
    """

    def run() -> None:
        while True:
            try:
                text = input(prompt).strip()
            except EOFError:
                bus.publish(DaemonEvent(type="shutdown", payload={"reason": "EOF"}, source="console"))
                return

            if text.lower() == "exit":
                bus.publish(DaemonEvent(type="shutdown", payload={"reason": "user_exit"}, source="console"))
                return

            if not text:
                continue

            bus.publish(DaemonEvent(type="text_input", payload={"text": text}, source="console"))

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

