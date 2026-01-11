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

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

# Flag to enable XR subsystem
ENABLE_XR = True  # Set to True to enable AR/VR/XR capabilities

if __name__ == "__main__":
    unimind = Unimind()
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
    rituals = RitualRegistry()
    scrolls = ScrollEngine()
    # vision = VisionSensor()
    personality = PersonalityTracker()
    
    # Initialize XR subsystem
    xr_engine = None
    xr_overlay_manager = None
    xr_anchor_system = None
    xr_gesture_interface = None
    xr_training_module = None
    
    if ENABLE_XR:
        try:
            from xr.xr_engine import XREngine
            from xr.ar_overlay import AROverlayManager
            from xr.spatial_anchor import SpatialAnchorSystem
            from xr.gesture_interface import GestureInterface
            from xr.xr_training import XRTrainingModule
            
            # Initialize XR components
            xr_engine = XREngine()
            xr_overlay_manager = AROverlayManager(xr_engine=xr_engine)
            xr_anchor_system = SpatialAnchorSystem(xr_engine=xr_engine)
            xr_gesture_interface = GestureInterface(
                xr_engine=xr_engine,
                overlay_manager=xr_overlay_manager
            )
            xr_training_module = XRTrainingModule(
                xr_engine=xr_engine,
                overlay_manager=xr_overlay_manager,
                anchor_system=xr_anchor_system,
                gesture_interface=xr_gesture_interface
            )
            
            # Register XR subsystems with scroll engine
            scrolls.set_xr_subsystems(
                xr_engine=xr_engine,
                overlay_manager=xr_overlay_manager,
                anchor_system=xr_anchor_system,
                training_module=xr_training_module
            )
            
            print("[Daemon] XR subsystem initialized successfully.")
            print(f"[Daemon] XR capabilities: {list(prom.get_xr_capabilities().keys())}")
            
        except Exception as e:
            print(f"[Daemon Warning] Failed to initialize XR subsystem: {e}")
            ENABLE_XR = False
    
    try:
        global nlu
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    print("[Daemon] Starting Prometheus daemon...")
    if ENABLE_XR:
        print("[Daemon] AR/XR capabilities are ENABLED")

    # Launch sensors and background modules in threads
    ENABLE_VOICE = False
    # To enable the voice listener, set ENABLE_VOICE = True above.
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()
    # threading.Thread(target=vision.classify_surroundings, daemon=True).start()
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