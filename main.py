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

# Robotics control module (optional - runs in simulation if no hardware)
try:
    from robotics.robot_core import RobotCore
    from scrolls.robot_scrolls import RobotScrolls
    ROBOTICS_AVAILABLE = True
except ImportError:
    ROBOTICS_AVAILABLE = False
    print("[Daemon] Robotics module not available")

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

# Flag to enable robotics control (simulation mode by default)
ENABLE_ROBOTICS = True  # Set to True to enable robotics subsystem
ROBOTICS_SIMULATION = True  # Set to False when using real hardware

if __name__ == "__main__":
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

    # Initialize robotics subsystem if enabled
    robot = None
    if ENABLE_ROBOTICS and ROBOTICS_AVAILABLE:
        try:
            robot = RobotCore(simulation_mode=ROBOTICS_SIMULATION)
            if robot.start():
                print(f"[Daemon] Robotics initialized ({'simulation' if ROBOTICS_SIMULATION else 'hardware'} mode)")
                # Register robot callbacks for daemon integration
                robot.register_callback("error", lambda data: print(f"[Robot Error] {data.get('message')}"))
            else:
                print("[Daemon] Failed to start robotics subsystem")
                robot = None
        except Exception as e:
            print(f"[Daemon] Robotics initialization error: {e}")
            robot = None

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
                if robot:
                    print("[Daemon] Stopping robotics subsystem...")
                    robot.stop()
                break
            elif user_input == "":
                personality.log_state()
                unimind.reflect()
            # Handle robot-specific commands directly
            elif user_input.lower().startswith("robot ") and robot:
                robot_cmd = user_input[6:].strip().lower()
                try:
                    if robot_cmd == "status":
                        status = robot.get_status()
                        print(f"[Robot] Status: {json.dumps(status, indent=2)}")
                    elif robot_cmd == "follow":
                        result = robot.execute_command("follow")
                        print(f"[Robot] {result}")
                    elif robot_cmd == "stop" or robot_cmd == "halt":
                        result = robot.execute_command("idle")
                        print(f"[Robot] {result}")
                    elif robot_cmd.startswith("perch"):
                        location = robot_cmd.split()[-1] if len(robot_cmd.split()) > 1 else "shoulder"
                        result = robot.execute_command("perch", location=location)
                        print(f"[Robot] {result}")
                    elif robot_cmd.startswith("go ") or robot_cmd.startswith("navigate "):
                        target = robot_cmd.split(maxsplit=1)[-1]
                        result = robot.execute_command("navigate", target=target)
                        print(f"[Robot] {result}")
                    elif robot_cmd == "home":
                        result = robot.execute_command("navigate", target="home")
                        print(f"[Robot] {result}")
                    elif robot_cmd.startswith("gesture ") or robot_cmd.startswith("wave") or robot_cmd.startswith("nod"):
                        gesture = robot_cmd.split()[-1] if " " in robot_cmd else robot_cmd
                        result = robot.execute_command("gesture", name=gesture)
                        print(f"[Robot] {result}")
                    elif robot_cmd == "calibrate":
                        result = robot.execute_command("calibrate")
                        print(f"[Robot] {result}")
                    else:
                        print(f"[Robot] Unknown command: {robot_cmd}")
                        print("[Robot] Available: status, follow, stop, perch, go <target>, home, gesture <name>, calibrate")
                except Exception as e:
                    print(f"[Robot Error] Command failed: {e}")
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