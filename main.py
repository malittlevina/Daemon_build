import threading
from unimind.core import Unimind
from unimind.bootstrap import attach_default_subsystems
from prometheus.specialties import PrometheusSpecialties
from codex.ingestion import ingest_documents
from emotion.emotion_engine import EmotionEngine
from rituals.ritual_registry import RitualRegistry
from introspection.personality_tracker import PersonalityTracker
from memory_tree.memory_logger import MemoryLogger
from optimizer.auto_upgrade import run_auto_optimization
from scrolls.scroll_engine import ScrollEngine
## from sensors.vision import VisionSensor
from nlu.nlu_engine import NLUEngine
from guardian.ethical_core import EthicalCore
from lam import symbolic_state as lam_state_module
from lam import lam_planner as lam_planner_module
from daemon.event_bus import EventBus
from daemon.events import DaemonEvent
from daemon.action_router import ActionRouter
from daemon.adapters.console_input import start_console_input
from daemon.adapters.textbox_server import start_textbox_server
from daemon.adapters.mic_adapter import start_mic_listener
from daemon.adapters.camera_adapter import start_camera_watcher
import subprocess
import json
import time
import os
from datetime import date

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

if __name__ == "__main__":
    unimind = Unimind()
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
    ethics = EthicalCore()
    rituals = RitualRegistry()
    scrolls = ScrollEngine()
    # vision = VisionSensor()
    personality = PersonalityTracker()
    try:
        global nlu
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    # Wire Unimind to connected subsystems (agent-native orchestration)
    attach_default_subsystems(
        unimind,
        emotion_engine=emotions,
        memory_logger=memory,
        ethical_core=ethics,
        lam_state_module=lam_state_module,
        lam_planner_module=lam_planner_module,
    )

    print("[Daemon] Starting Prometheus daemon...")

    # Launch sensors and background modules in threads
    ENABLE_VOICE = False
    # To enable the voice listener, set ENABLE_VOICE = True above.
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()
    # threading.Thread(target=vision.classify_surroundings, daemon=True).start()
    threading.Thread(target=run_auto_optimization, daemon=True).start()

    # Event-driven IO: console + textbox + mic + camera
    bus = EventBus()
    router = ActionRouter(scroll_engine=scrolls)

    ENABLE_TEXTBOX = True
    ENABLE_MIC = False
    ENABLE_CAMERA = False

    start_console_input(bus)
    if ENABLE_TEXTBOX:
        start_textbox_server(bus, host="0.0.0.0", port=8765)
    if ENABLE_MIC:
        start_mic_listener(bus)
    if ENABLE_CAMERA:
        start_camera_watcher(bus)

    # Load Codex documents
    ingest_documents("codex/data/")

    os.makedirs("logs", exist_ok=True)
    last_run_date = None

    def handle_fallback(text):
        if not USE_OLLAMA:
            return "[Daemon] No known intent."
        try:
            response = subprocess.run(
                ["ollama", "run", "llama3"],
                input=text,
                text=True,
                capture_output=True
            )
            if response.returncode == 0:
                output = response.stdout
                return output if output else "[Daemon] No response from Ollama."
            else:
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
                with open("logs/improvement_history.log", "a") as log_file:
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
                                or (isinstance(nlu_intent, str) and nlu_intent.startswith("[NLUEngine] No known intent"))
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