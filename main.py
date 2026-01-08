import threading
import subprocess
import json
import time
import os
from datetime import date

# --- Core & Architecture ---
from unimind.core import Unimind
from unimind.drives import DriveSystem
from core.system_health import get_system_health
from core.personality_engine import get_personality_engine

# --- Knowledge & Logic ---
from codex.ingestion import ingest_documents
from codex.curriculum import CurriculumManager
from code_tools.code_master import CodeMaster
from nlu.nlu_engine import NLUEngine

# --- Embodiment (Virtual & Physical) ---
from world_engine.core import WorldEngine  # Used implicitly via bridge but good to have explicit if needed
from storyrealms.storyrealm_bridge import get_engine, step_realm
from sensors.sensor_manager import SensorManager

# --- Expression ---
from avatar.avatar_engine import AvatarEngine
from avatar.ascii_renderer import ASCIIRenderer

# --- Legacy Modules (To be refactored/merged eventually) ---
from prometheus.specialties import PrometheusSpecialties
from emotion.emotion_engine import EmotionEngine
from rituals.ritual_registry import RitualRegistry
from introspection.personality_tracker import PersonalityTracker
from memory_tree.memory_logger import MemoryLogger
from optimizer.auto_upgrade import run_auto_optimization
from scrolls.scroll_engine import ScrollEngine

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

if __name__ == "__main__":
    print("[Daemon] Initializing Unified System...")
    health = get_system_health()
    
    # 1. Initialize Unimind (The Core)
    unimind = Unimind()
    
    # 2. Initialize Subsystems & Register to Unimind
    
    # Motivation
    drives = DriveSystem()
    unimind.register("motivation", drives)
    
    try:
        from cognitive.curiosity import CuriosityModule
        curiosity = CuriosityModule()
        unimind.register("motivation", curiosity)
        print("[System] Curiosity Module Active")
    except Exception as e:
        print(f"[System] Curiosity Init Failed: {e}")
        health.log_error("Curiosity", str(e))
        curiosity = None

    # Logic & Knowledge
    code_master = CodeMaster()
    unimind.register("logic", code_master)
    
    curriculum = CurriculumManager()
    unimind.register("knowledge", curriculum)

    # Expression
    avatar = AvatarEngine()
    renderer = ASCIIRenderer()
    unimind.register("avatar", avatar)

    # Legacy/Support Modules
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
    rituals = RitualRegistry()
    scrolls = ScrollEngine()
    personality_tracker = PersonalityTracker()

    # NLU (The Interface)
    try:
        nlu = NLUEngine(scrolls)
        if hi_tuner:
            nlu.set_tuner(hi_tuner)
        unimind.register("language", nlu)
    except Exception as e:
        print(f"[Daemon Init Error] Failed to initialize NLU: {e}")
        health.log_error("NLU", str(e))
        nlu = None

    # 3. Background Threads (The "Life" of the Daemon)
    
    # Optimizer Thread
    threading.Thread(target=run_auto_optimization, daemon=True, name="Optimizer").start()
    
    # World Engine Thread
    def world_simulation_loop():
        print("[Daemon] World Engine simulation started (background).")
        # Ensure engine is loaded
        _ = get_engine() 
        
        while True:
            try:
                # Run a step every 10 seconds
                step_result = step_realm()
                logs = step_result["logs"]
                
                # Observation & Learning Loop
                if curiosity and logs:
                    for log in logs:
                        # Naive parsing
                        context = "GlobalState"
                        event_type = "Unknown"
                        if "moved to" in log: event_type = "Movement"
                        elif "changed to" in log: event_type = "StateChange"
                        elif "interact" in log: event_type = "Interaction"
                        
                        is_interesting = curiosity.process_observation(context, event_type, log)
                        if is_interesting:
                            # In a real app we might signal this to UI, here we just log
                            pass

                time.sleep(10)
            except Exception as e:
                print(f"[WorldEngine Error] {e}")
                health.log_error("WorldEngine", str(e))
                time.sleep(10)
    
    threading.Thread(target=world_simulation_loop, daemon=True, name="WorldEngine").start()
    unimind.register("world", get_engine()) # Register singleton

    # Sensor Manager Thread
    try:
        sensors = SensorManager(curiosity_module=curiosity)
        sensors.start_background_loop()
        unimind.register("perception", sensors)
    except Exception as e:
        print(f"[Daemon] Failed to start Sensor Manager: {e}")
        health.log_error("Sensors", str(e))
        sensors = None
        
    # Voice Listener (Optional)
    ENABLE_VOICE = False
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True, name="Voice").start()

    # 4. Final Setup
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
            health.log_error("Ollama", str(e))
            return f"[Daemon] Fallback error: {e}"

    # 5. Main Loop
    print("\n[Daemon] System Ready. Type 'help', 'status', or commands.")
    
    while True:
        try:
            # Nightly Routine
            current_hour = time.localtime().tm_hour
            today = date.today()
            if current_hour == 2 and last_run_date != today:
                print("[System] Running Nightly Reflection...")
                unimind.reflect()
                last_run_date = today

            # Render Avatar Face
            # Sync Avatar with Drives/Personality
            dominant_drive = drives.get_most_urgent_drive()
            pers_engine = get_personality_engine()
            
            # Mood mapping
            current_mood = "neutral"
            if dominant_drive.value < 0.3:
                current_mood = pers_engine.mood_modifiers.get(dominant_drive.name, {}).get("low", "neutral")
            elif dominant_drive.value > 0.8:
                current_mood = pers_engine.mood_modifiers.get(dominant_drive.name, {}).get("high", "neutral")
            
            avatar.set_emotion(current_mood)
            avatar.update(0.1)
            
            # Draw
            visual = renderer.render(avatar.get_current_visual_state())
            print(f"\n{visual}")

            # Autonomous Drive Check
            drives.update()
            urgent_drive = drives.get_most_urgent_drive()

            if urgent_drive.is_critical(0.3):
                print(f"\n[Daemon] ⚠️  Critical Drive Alert: {urgent_drive.name} is low.")
                # Auto-action logic...
                if nlu and urgent_drive.recovery_action:
                     # Simulate self-command
                     pass 

            # User Input
            print("[Daemon] > ", end="", flush=True)
            user_input = input().strip()

            if user_input.lower() == "exit":
                print("[Daemon] Shutting down.")
                if sensors: sensors.stop()
                break
            elif user_input.lower() == "status":
                print(health.format_status())
                # Also show Unimind reflection
                unimind.reflect()
            elif user_input == "":
                pass
            else:
                result = None
                if nlu:
                    try:
                        result = nlu.interpret(user_input, context_drives=drives)
                        if result is None or (isinstance(result, str) and result.startswith("[NLUEngine] No known intent")):
                            result = handle_fallback(user_input)
                    except Exception as e:
                        print(f"[Daemon Error] NLU failed: {e}")
                        health.log_error("MainLoop", str(e))
                        result = handle_fallback(user_input)
                else:
                    print("[Daemon Warning] NLU not available.")
                    result = handle_fallback(user_input)

                print(f"[Daemon] {result}")

        except KeyboardInterrupt:
            print("\n[Daemon] Interrupted. Shutting down.")
            break
        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            health.log_error("CriticalLoop", str(loop_error))
            time.sleep(1)
