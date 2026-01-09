from __future__ import annotations

import threading
from typing import Optional

from daemon.event_bus import EventBus
from daemon.events import DaemonEvent


def start_mic_listener(bus: EventBus, *, phrase_time_limit: int = 6) -> threading.Thread:
    """
    Microphone adapter using `speech_recognition` if available.
    Publishes `audio_transcript` events (best-effort).
    """

    def run() -> None:
        try:
            import speech_recognition as sr  # type: ignore
        except Exception as e:
            bus.publish(
                DaemonEvent(
                    type="system_event",
                    payload={"component": "mic", "error": f"speech_recognition unavailable: {e}"},
                    source="mic",
                )
            )
            return

        recognizer = sr.Recognizer()
        try:
            mic = sr.Microphone()
        except Exception as e:
            bus.publish(
                DaemonEvent(
                    type="system_event",
                    payload={"component": "mic", "error": f"Microphone init failed: {e}"},
                    source="mic",
                )
            )
            return

        print("[Mic] Listening (Ctrl+C in main to stop daemon).")
        with mic as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
            except Exception:
                pass

        while True:
            try:
                with mic as source:
                    audio = recognizer.listen(source, phrase_time_limit=phrase_time_limit)
                text = recognizer.recognize_google(audio).strip()
                if text:
                    bus.publish(
                        DaemonEvent(
                            type="audio_transcript",
                            payload={"text": text},
                            source="mic",
                            confidence=None,
                        )
                    )
            except Exception as e:
                # Soft-fail: publish system event and keep listening.
                bus.publish(
                    DaemonEvent(
                        type="system_event",
                        payload={"component": "mic", "error": str(e)},
                        source="mic",
                    )
                )

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

