import threading
from unimind.core import Unimind
from unimind.drives import DriveSystem
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
from storyrealms.storyrealm_bridge import get_engine, step_realm
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
    personality = PersonalityTracker()
    try:
        global nlu
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        nlu = None

    print("[Daemon] Starting Prometheus daemon...")

    # Launch sensors and background modules in threads
    ENABLE_VOICE = False
    # To enable the voice listener, set ENABLE_VOICE = True above.
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()
    # threading.Thread(target=vision.classify_surroundings, daemon=True).start()
    threading.Thread(target=run_auto_optimization, daemon=True).start()

    # --- World Engine Background Thread ---
    def world_simulation_loop():
        print("[Daemon] World Engine simulation started (background).")
        engine = get_engine() # Ensure initialized
        
        # Initialize Cognitive Modules
        try:
            from cognitive.curiosity import CuriosityModule
            curiosity = CuriosityModule()
            print("[Daemon] Cognitive Curiosity Module active.")
        except Exception as e:
            print(f"[Daemon] Failed to load Curiosity Module: {e}")
            curiosity = None
            
    # Initialize Drive System (Background Loop Version)
    drives = DriveSystem()
    unimind.register("motivation", drives)
    
    # Register World Engine (via a wrapper or direct if compatible)
    # The get_engine returns the singleton
    world_engine = get_engine()
    unimind.register("world", world_engine)

    # Initialize Sensor Manager (Physical Embodiment)
    try:
        from sensors.sensor_manager import SensorManager
        sensors = SensorManager(curiosity_module=curiosity)
        sensors.start_background_loop()
        unimind.register("perception", sensors)
    except Exception as e:
        print(f"[Daemon] Failed to start Sensor Manager: {e}")
        sensors = None
    
    # Register Curiosity as motivation/logic
    if curiosity:
        unimind.register("motivation", curiosity)

        # For this prototype, we'll assume the main thread handles the 'Acting' on drives,
        # and this thread just feeds the Curiosity drive.
        # But we actually want the drives to update here too or in main loop.
        # Let's keep Drive updates in the main loop to avoid race conditions on 'nlu'.
            
        while True:
            try:
                # Run a step every 10 seconds
                step_result = step_realm()
                logs = step_result["logs"]
                
                # --- Observation & Learning Loop ---
                if curiosity and logs:
                    for log in logs:
                        # Parse log into structured triplet (Naive parsing for demo)
                        # Log format example: "Entity X moved to Y" or "Weather in Z changed to Rain"
                        
                        context = "GlobalState" # Simplified context
                        event_type = "Unknown"
                        outcome = log
                        
                        if "moved to" in log:
                            event_type = "Movement"
                        elif "changed to" in log:
                            event_type = "StateChange"
                        elif "interact" in log:
                            event_type = "Interaction"
                            
                        # Feed to curiosity module
                        is_interesting = curiosity.process_observation(context, event_type, outcome)
                        
                        if is_interesting:
                            print(f"[Daemon] 💡 The AI found this interesting: {log}")
                            # SIGNAL: We found something interesting!
                            # In a robust system, we'd use a queue. For now, we rely on the log file or shared memory.
                            # But we can try to update the DriveSystem file directly if we assume file-based IPC (slow but safeish)
                            # Or better, let's just use a global flag if possible, or skip for now and handle in main.
                # -----------------------------------

                if logs:
                    if len(logs) > 0:
                        # print(f"\n[WorldEvent] {len(logs)} updates processed.")
                        pass 
                time.sleep(10)
            except Exception as e:
                print(f"[WorldEngine Error] {e}")
                time.sleep(10)
    
    threading.Thread(target=world_simulation_loop, daemon=True).start()
    # ---------------------------------------

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
            
            # --- Autonomous Drive Check ---
            drives.update()
            urgent_drive = drives.get_most_urgent_drive()
            # print(f"[Debug] Drives: {[(k, round(d.value, 2)) for k, d in drives.drives.items()]}")

            if urgent_drive.is_critical(0.3):
                print(f"\n[Daemon] ⚠️  Critical Drive Alert: {urgent_drive.name} is low ({urgent_drive.value:.2f}).")
                print(f"[Daemon] 🤖 Autonomous Agent triggering: {urgent_drive.recovery_action}...")
                
                # Execute recovery action automatically
                if nlu and urgent_drive.recovery_action:
                    try:
                        # Feed the recovery action into NLU/LAM as if the user said it
                        auto_input = urgent_drive.recovery_action
                        result = nlu.interpret(auto_input)
                        print(f"[Daemon] Auto-Action Result: {result}")
                        
                        # Assuming success for now, satisfy the drive partially
                        # In a real system, we'd wait for feedback.
                        drives.satisfy_drive(urgent_drive.name, 0.5)
                        
                    except Exception as e:
                        print(f"[Daemon] Auto-Action Failed: {e}")
            # ------------------------------

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
                        # Pass the drive system context to NLU for personality modulation
                        result = nlu.interpret(user_input, context_drives=drives)
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