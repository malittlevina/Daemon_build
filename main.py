import threading
from unimind.core import Unimind
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
import subprocess
import time
import os
from pathlib import Path
from datetime import date

from core.runtime_context import detect_runtime_context
from daemon.runtime_config import load_daemon_config

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

if __name__ == "__main__":
    config = load_daemon_config("config/daemon_config.json")
    ctx = detect_runtime_context(project_root=Path(__file__).resolve().parent, config=config)

    os_pref = config.get("os_preference", {}) if isinstance(config, dict) else {}
    allow_full_non_preferred = bool(os_pref.get("allow_full_features_on_non_preferred_os", False))

    effective = dict(config)
    if ctx.compatibility_mode and not allow_full_non_preferred:
        # Prefer ThothOS: keep daemon runnable everywhere by default,
        # while reserving heavier integrations (sensors/auto-optimization)
        # for native ThothOS unless explicitly allowed.
        effective["voice_listener_enabled"] = False
        effective["camera_sensor_enabled"] = False
        effective["auto_optimization"] = False

    print(
        "[Daemon] Runtime context: "
        f"os={ctx.host_os} arch={ctx.host_arch} "
        f"thothos={ctx.is_thothos} "
        f"mode={'compatibility' if ctx.compatibility_mode else 'native'} "
        f"reason={ctx.thothos_detection_reason}"
    )

    unimind = Unimind(runtime_context=ctx)
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
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

    print("[Daemon] Starting Prometheus daemon...")

    # Launch sensors and background modules in threads
    if effective.get("voice_listener_enabled", False):
        try:
            from voice.voice_listener import start_voice_listener

            threading.Thread(target=start_voice_listener, daemon=True).start()
        except Exception as e:
            print(f"[Daemon Warning] Voice listener unavailable: {e}")

    if effective.get("camera_sensor_enabled", False):
        try:
            from sensors.vision import VisionSensor

            vision = VisionSensor()
            threading.Thread(target=vision.classify_surroundings, daemon=True).start()
        except Exception as e:
            print(f"[Daemon Warning] Camera sensor unavailable: {e}")

    if effective.get("auto_optimization", False):
        threading.Thread(target=run_auto_optimization, daemon=True).start()

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

            print("\n[Daemon] Enter a command or type 'exit': ", end="", flush=True)
            user_input = input().strip()

            if user_input.lower() == "exit":
                print("[Daemon] Shutting down.")
                break
            elif user_input == "":
                personality.log_state()
                unimind.reflect()
            else:
                result = None
                if nlu:
                    try:
                        result = nlu.interpret(user_input)
                        if result is None or (isinstance(result, str) and result.startswith("[NLUEngine] No known intent")):
                            result = handle_fallback(user_input)
                    except Exception as e:
                        print(f"[Daemon Error] NLU failed: {e}")
                        result = handle_fallback(user_input)
                else:
                    print("[Daemon Warning] NLU not available. Using fallback response.")
                    result = handle_fallback(user_input)

                print(f"[Daemon] NLU Result: {result}")

        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            continue