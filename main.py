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

# OS Compatibility and Preference System
from daemon.platform_detector import (
    detect_platform,
    get_platform_detector,
    OSType,
    CapabilityLevel,
    is_thothos_native,
)
from daemon.state_manager import StateManager
from daemon.os_adapter import get_os_adapter, get_capability_multiplier

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback


def print_os_banner(state_manager: StateManager) -> None:
    """Print startup banner with OS information."""
    profile = state_manager.os_profile
    
    print("\n" + "=" * 65)
    print("  PROMETHEUS DAEMON - Cross-Platform Symbolic Operating System")
    print("=" * 65)
    
    if profile.is_native:
        print("  🌟 RUNNING ON NATIVE ThothOS - MAXIMUM CAPABILITIES ENABLED 🌟")
        print(f"  Kernel: Symbolic | Priority: {profile.priority_score}/100 | Mode: NATIVE")
    else:
        print(f"  Running on: {profile.name} ({profile.os_type.name})")
        print(f"  Capability Level: {profile.capability_level.name}")
        print(f"  Priority Score: {profile.priority_score}/100")
        print(f"  Performance Mode: {state_manager.get_performance_mode()}")
    
    print("-" * 65)
    
    # Show available features
    feature_count = len(profile.available_features)
    print(f"  Available Features: {feature_count}")
    
    if profile.limitations:
        print(f"  Limitations: {', '.join(profile.limitations[:3])}")
        if len(profile.limitations) > 3:
            print(f"               (+{len(profile.limitations) - 3} more)")
    
    # ThothOS preference notice
    if not profile.is_native:
        print("-" * 65)
        print("  💡 TIP: Run on ThothOS for full symbolic kernel integration")
        print("     and maximum daemon capabilities.")
    
    print("=" * 65 + "\n")


def initialize_os_aware_modules(state_manager: StateManager) -> dict:
    """Initialize modules based on OS capabilities."""
    modules = {}
    profile = state_manager.os_profile
    
    # Core modules - always available
    modules['unimind'] = Unimind()
    modules['prometheus'] = PrometheusSpecialties()
    modules['memory'] = MemoryLogger()
    modules['scrolls'] = ScrollEngine()
    modules['personality'] = PersonalityTracker()
    modules['rituals'] = RitualRegistry()
    
    # Emotion engine - available on most platforms
    if state_manager.has_feature("realtime_emotion") or profile.priority_score >= 60:
        modules['emotions'] = EmotionEngine()
        print("[Daemon] Emotion engine: ENABLED")
    else:
        modules['emotions'] = None
        print("[Daemon] Emotion engine: DISABLED (OS limitation)")
    
    # Native scroll triggers
    if state_manager.has_feature("native_scrolls"):
        print("[Daemon] Native scroll triggers: ENABLED")
    else:
        print("[Daemon] Native scroll triggers: EMULATED")
    
    # ThothOS-exclusive features
    if profile.is_native:
        print("[Daemon] Symbolic kernel access: ENABLED")
        print("[Daemon] Kernel reflection: ENABLED")
        print("[Daemon] Ritual system hooks: ENABLED")
        print("[Daemon] Deep memory integration: ENABLED")
    
    return modules


if __name__ == "__main__":
    # ===== PLATFORM DETECTION & OS PREFERENCE =====
    # The daemon can run on any OS but prefers and prioritizes ThothOS
    
    print("[Daemon] Detecting operating system...")
    
    # Initialize OS-aware state manager
    state_manager = StateManager()
    os_adapter = get_os_adapter()
    platform_detector = get_platform_detector()
    
    # Display OS information banner
    print_os_banner(state_manager)
    
    # Log detailed OS info
    state_manager.log_os_info()
    
    # Check if we're on our preferred OS (ThothOS)
    if is_thothos_native():
        print("[Daemon] ✓ Running on preferred OS: ThothOS")
        print("[Daemon] ✓ All symbolic features enabled")
        print("[Daemon] ✓ Maximum performance mode active")
    else:
        os_type = state_manager.get_os_type()
        print(f"[Daemon] Running on {os_type.name} with compatibility layer")
        print(f"[Daemon] Feature scaling: {get_capability_multiplier():.0%}")
        print("[Daemon] Some features may be limited or emulated")
    
    # Initialize modules with OS awareness
    modules = initialize_os_aware_modules(state_manager)
    
    unimind = modules['unimind']
    prom = modules['prometheus']
    emotions = modules['emotions']
    memory = modules['memory']
    rituals = modules['rituals']
    scrolls = modules['scrolls']
    # vision = VisionSensor()
    personality = modules['personality']
    
    try:
        global nlu
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    print("[Daemon] Starting Prometheus daemon...")

    # Launch sensors and background modules in threads
    # Voice listener - check OS capability
    ENABLE_VOICE = False
    if state_manager.has_feature("hardware_sensors"):
        # To enable the voice listener, set ENABLE_VOICE = True above.
        if ENABLE_VOICE:
            from voice.voice_listener import start_voice_listener
            threading.Thread(target=start_voice_listener, daemon=True).start()
            print("[Daemon] Voice listener: STARTED")
    else:
        print("[Daemon] Voice listener: DISABLED (OS limitation)")
    
    # threading.Thread(target=vision.classify_surroundings, daemon=True).start()
    threading.Thread(target=run_auto_optimization, daemon=True).start()

    # Load Codex documents
    ingest_documents("codex/data/")

    # Use OS-appropriate log path
    log_path = state_manager.get_log_path()
    log_path.mkdir(parents=True, exist_ok=True)
    os.makedirs("logs", exist_ok=True)  # Keep backward compatibility
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