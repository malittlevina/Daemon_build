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
from sensors.vision import VisionSensor
from sensors.device_scanner import DeviceScanner
from nlu.nlu_engine import NLUEngine
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
    rituals = RitualRegistry()
    scrolls = ScrollEngine()
    # vision = VisionSensor()
    device_scanner = DeviceScanner()
    
    # Connect Device Scanner to Unimind Event Bus
    def on_new_device(device):
        msg = f"New device detected: {device.get('name') or device.get('ssid') or 'Unknown'}"
        print(f"\n[System Notification] {msg}")
        unimind.emit("device_detected", device)
        unimind.emit("input_received", {"text": msg, "source": "sensors"})

    device_scanner.add_listener(on_new_device)
    device_scanner.start_scanning()
    
    # Initialize Personality with Unimind access if needed
    personality = PersonalityTracker()
    
    # Initialize NLU
    try:
        global nlu
        nlu = NLUEngine(scrolls)
        # Register NLU as a listener to inputs if we wanted fully event-driven architecture
        # unimind.subscribe("user_input", nlu.interpret) 
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    # Initialize ThothBridge
    from bridge.thoth_bridge import ThothBridge
    bridge = ThothBridge(unimind)

    # Load Apps
    import importlib.util
    apps_dir = "apps"
    if os.path.exists(apps_dir):
        for app_name in os.listdir(apps_dir):
            app_path = os.path.join(apps_dir, app_name, "main.py")
            if os.path.exists(app_path):
                try:
                    spec = importlib.util.spec_from_file_location(f"apps.{app_name}", app_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "run"):
                        module.run(bridge)
                        print(f"[Daemon] Loaded app: {app_name}")
                except Exception as e:
                    print(f"[Daemon] Failed to load app {app_name}: {e}")

    print("[Daemon] Starting Prometheus daemon...")

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
            elif user_input.lower() == "devices":
                devices = device_scanner.get_known_devices()
                print(f"[Daemon] Known Devices: {json.dumps(devices, indent=2)}")
            elif user_input.lower().startswith("connect "):
                dev_id = user_input.split(" ", 1)[1]
                success, msg = device_scanner.connect_device(dev_id)
                print(f"[Daemon] Connection Result: {msg}")
            elif user_input.lower().startswith("create scroll "):
                # Format: create scroll <name> : <description>
                try:
                    parts = user_input[14:].split(":", 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        desc = parts[1].strip()
                        from guardian.code_generator import CodeGenerator
                        gen = CodeGenerator()
                        code = gen.propose_scroll_implementation(desc)
                        path = gen.generate_scroll(name, code)
                        # Reload scrolls
                        scrolls._load_library_scrolls()
                        print(f"[Daemon] Created new scroll '{name}' at {path}")
                        print(f"[Daemon] You can now run it by typing: {name}")
                    else:
                        print("[Daemon] Usage: create scroll <name> : <description>")
                except Exception as e:
                    print(f"[Daemon] Error creating scroll: {e}")
            else:
                # Emit user input to the event bus
                unimind.emit("input_received", {"text": user_input, "source": "user"})
                
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