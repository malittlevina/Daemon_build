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
import json
import time
import os
from datetime import date
from daemon.os_policy import build_configured_profile_and_config

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

if __name__ == "__main__":
    runtime_profile, daemon_config = build_configured_profile_and_config("config/daemon_config.json")

    # Expose runtime mode for subsystems that want to branch without importing daemon modules.
    os.environ["PROMETHEUS_RUNTIME_MODE"] = runtime_profile.mode
    os.environ["PROMETHEUS_PREFERRED_OS_ID"] = runtime_profile.symbolic_os.os_id

    unimind = Unimind()
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
    print(
        "[Daemon] Runtime profile:",
        f"mode={runtime_profile.mode},",
        f"host={runtime_profile.host.system} {runtime_profile.host.release},",
        f"symbolic_os_native={runtime_profile.symbolic_os.is_native} ({runtime_profile.symbolic_os.confidence}),",
        f"markers={list(runtime_profile.symbolic_os.markers)}",
    )
    for warning in daemon_config.get("runtime_warnings", []) or []:
        print(f"[Daemon][Runtime Warning] {warning}")

    # Launch sensors and background modules in threads
    if daemon_config.get("voice_listener_enabled", False):
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()
    # threading.Thread(target=vision.classify_surroundings, daemon=True).start()
    if daemon_config.get("auto_optimization", False):
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