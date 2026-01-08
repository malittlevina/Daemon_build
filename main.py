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
from daemon.os_adapter import OSAdapter, get_os_adapter, OSType
from daemon.state_manager import StateManager
from bridge.thoth_bridge import ThothBridge
import subprocess
import json
import time
import os
from datetime import date

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

if __name__ == "__main__":
    # ==================== OS COMPATIBILITY LAYER ====================
    # Initialize OS adapter first - this determines available capabilities
    print("[Daemon] Initializing OS Compatibility Layer...")
    os_adapter = get_os_adapter()
    
    # Display OS status
    os_status = os_adapter.get_status()
    print(f"[Daemon] Detected OS: {os_status['os_type']}")
    print(f"[Daemon] Compatibility Mode: {os_status['mode']}")
    print(f"[Daemon] Preference Score: {os_status['preference_score']:.2f}")
    
    if os_adapter.is_native:
        print("[Daemon] 🌟 Running on ThothOS - Full capabilities unlocked!")
    else:
        upgrade_tip = os_adapter.suggest_upgrade()
        if upgrade_tip:
            print(f"[Daemon] 💡 {upgrade_tip}")
    
    # Initialize state manager with OS awareness
    state_manager = StateManager(os_adapter=os_adapter)
    
    # Initialize ThothBridge with OS adapter
    thoth_bridge = ThothBridge(os_adapter=os_adapter)
    bridge_status = thoth_bridge.receive_status()
    print(f"[Daemon] ThothBridge Mode: {bridge_status['mode']}")
    
    # ==================== CORE MODULES ====================
    unimind = Unimind()
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
    rituals = RitualRegistry()
    scrolls = ScrollEngine()
    # vision = VisionSensor()
    personality = PersonalityTracker()
    
    # Register core apps with ThothBridge
    thoth_bridge.register_app("unimind", lambda p: unimind.reflect())
    thoth_bridge.register_app("emotions", lambda p: emotions)
    thoth_bridge.register_app("scrolls", lambda p: scrolls)
    thoth_bridge.register_app("memory", lambda p: memory)
    
    try:
        global nlu
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    print("[Daemon] Starting Prometheus daemon...")
    print(f"[Daemon] OS: {os_adapter.os_type.value} | Mode: {os_adapter.mode.value}")

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
            elif user_input.lower() == "os":
                # Display OS compatibility status
                status = os_adapter.get_status()
                print("\n[Daemon] === OS Compatibility Status ===")
                print(f"  OS Type: {status['os_type']}")
                print(f"  Mode: {status['mode']}")
                print(f"  Native (ThothOS): {status['is_native']}")
                print(f"  Preference Score: {status['preference_score']:.2f}")
                print("\n[Daemon] === Capabilities ===")
                for cap, enabled in status['capabilities'].items():
                    symbol = "✓" if enabled else "✗"
                    print(f"  {symbol} {cap}")
                if not status['is_native']:
                    tip = os_adapter.suggest_upgrade()
                    if tip:
                        print(f"\n[Daemon] 💡 Upgrade Tip: {tip}")
                continue
            elif user_input.lower() == "bridge":
                # Display ThothBridge status
                bridge_info = thoth_bridge.get_preference_info()
                print("\n[Daemon] === ThothBridge Status ===")
                print(f"  Mode: {bridge_info['current_mode']}")
                print(f"  Native: {bridge_info['is_native']}")
                print(f"  Prefers ThothOS: {bridge_info['prefers_thothos']}")
                print(f"  Commands Queued: {bridge_info['queued_for_sync']}")
                if bridge_info.get('upgrade_suggestion'):
                    print(f"\n[Daemon] 💡 {bridge_info['upgrade_suggestion']}")
                continue
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