from __future__ import annotations

import os
import subprocess
import threading
import time
from datetime import date
from typing import Optional

from codex.ingestion import ingest_documents
from daemon.action_router import ActionRouter
from daemon.adapters.camera_adapter import start_camera_watcher
from daemon.adapters.console_input import start_console_input
from daemon.adapters.mic_adapter import start_mic_listener
from daemon.adapters.textbox_server import start_textbox_server
from daemon.event_bus import EventBus
from emotion.emotion_engine import EmotionEngine
from guardian.ethical_core import EthicalCore
from introspection.personality_tracker import PersonalityTracker
from memory_tree.memory_logger import MemoryLogger
from nlu.nlu_engine import NLUEngine
from optimizer.auto_upgrade import run_auto_optimization
from prometheus.specialties import PrometheusSpecialties
from rituals.ritual_registry import RitualRegistry
from scrolls.scroll_engine import ScrollEngine
from unimind.bootstrap import attach_default_subsystems
from unimind.core import Unimind
from lam import symbolic_state as lam_state_module
from lam import lam_planner as lam_planner_module


def run_daemon(
    *,
    use_ollama: bool = False,
    enable_textbox: bool = True,
    textbox_host: str = "0.0.0.0",
    textbox_port: int = 8765,
    enable_mic: bool = False,
    enable_camera: bool = False,
) -> None:
    """
    Daemon entrypoint: I/O + event loop + action routing.

    The Unimind kernel remains in `unimind/`.
    """

    unimind = Unimind()
    _prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
    ethics = EthicalCore()
    _rituals = RitualRegistry()
    scrolls = ScrollEngine()
    _personality = PersonalityTracker()

    try:
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    attach_default_subsystems(
        unimind,
        emotion_engine=emotions,
        memory_logger=memory,
        ethical_core=ethics,
        lam_state_module=lam_state_module,
        lam_planner_module=lam_planner_module,
    )

    print("[Daemon] Starting Prometheus daemon...")

    # Background modules
    threading.Thread(target=run_auto_optimization, daemon=True).start()

    # Event-driven IO
    bus = EventBus()
    router = ActionRouter(scroll_engine=scrolls)

    start_console_input(bus)
    if enable_textbox:
        start_textbox_server(bus, host=textbox_host, port=textbox_port)
    if enable_mic:
        start_mic_listener(bus)
    if enable_camera:
        start_camera_watcher(bus)

    # Load Codex documents
    ingest_documents("codex/data/")

    os.makedirs("logs", exist_ok=True)
    last_run_date: Optional[date] = None

    def handle_fallback(text: str) -> str:
        if not use_ollama:
            return "[Daemon] No known intent."
        try:
            response = subprocess.run(
                ["ollama", "run", "llama3"],
                input=text,
                text=True,
                capture_output=True,
            )
            if response.returncode == 0:
                output = response.stdout
                return output if output else "[Daemon] No response from Ollama."
            return f"[Daemon] Ollama error: {response.stderr}"
        except Exception as e:
            return f"[Daemon] Fallback error: {e}"

    while True:
        try:
            # Nightly reflection & self-improvement at 2 AM
            current_hour = time.localtime().tm_hour
            today = date.today()
            if current_hour == 2 and last_run_date != today:
                from code_tools import code_generator

                unimind.reflect()
                code_generator.propose_improvements("Nightly system reflection and improvement")
                with open("logs/improvement_history.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"{time.asctime()} - Nightly reflection and improvement triggered\n")
                last_run_date = today

            event = bus.get(timeout=0.25)
            if event is None:
                continue

            if event.type == "shutdown":
                print(f"[Daemon] Shutting down: {event.payload}")
                break

            nlu_intent = None
            if event.type in {"text_input", "audio_transcript"}:
                text = str((event.payload or {}).get("text") or "")
                if text:
                    if nlu:
                        try:
                            nlu_intent = nlu.interpret(text)
                            if (
                                nlu_intent is None
                                or (
                                    isinstance(nlu_intent, str)
                                    and nlu_intent.startswith("[NLUEngine] No known intent")
                                )
                            ):
                                nlu_intent = handle_fallback(text)
                        except Exception as e:
                            print(f"[Daemon Error] NLU failed: {e}")
                            nlu_intent = handle_fallback(text)
                    else:
                        nlu_intent = handle_fallback(text)

            # Unimind ingest + planning
            try:
                plan, trace = unimind.ingest_event(event.to_dict(), nlu_intent=nlu_intent)
                utterance = (trace.notes or {}).get("utterance_plan", {}) if trace else {}
                if isinstance(utterance, dict) and utterance.get("text"):
                    print(utterance["text"])
                else:
                    print(f"[Unimind] Plan: {plan.action}")
                    print(f"[Unimind] Rationale: {plan.rationale}")

                outcome = router.route(plan, trace=trace.__dict__ if trace else None)
                if outcome.get("executed"):
                    print(f"[Router] {outcome.get('result')}")
            except Exception as e:
                print(f"[Daemon] Unimind ingest error: {e}")

        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            continue

