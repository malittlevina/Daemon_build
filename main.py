import threading
import time
import os
import sys
from datetime import date

# Kernel Architecture
from core.kernel import Kernel

# Modules
from unimind.core import Unimind
from prometheus.specialties import PrometheusSpecialties
from emotion.emotion_engine import EmotionEngine
from memory_tree.memory_logger import MemoryLogger
from rituals.ritual_registry import RitualRegistry
from scrolls.scroll_engine import ScrollEngine
from introspection.personality_tracker import PersonalityTracker
from nlu.nlu_engine import NLUEngine

# Legacy/Utility imports (managed by modules internally or kept for specific uses)
from codex.ingestion import ingest_documents
from optimizer.auto_upgrade import run_auto_optimization

# Flags
USE_OLLAMA = False
ENABLE_VOICE = False

def handle_fallback(text):
    if not USE_OLLAMA:
        return "[Daemon] No known intent."
    try:
        import subprocess
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

def main():
    print("[Daemon] Booting Kernel...")
    kernel = Kernel()

    # Register Core Modules
    kernel.register_module("unimind", Unimind(kernel))
    kernel.register_module("prometheus", PrometheusSpecialties(kernel))
    kernel.register_module("emotion", EmotionEngine(kernel))
    kernel.register_module("memory", MemoryLogger(kernel))
    kernel.register_module("scrolls", ScrollEngine(kernel)) # Rituals depends on Scrolls
    kernel.register_module("rituals", RitualRegistry(kernel))
    kernel.register_module("personality", PersonalityTracker(kernel))
    kernel.register_module("nlu", NLUEngine(kernel))
    
    from daemon.state_manager import StateManager
    kernel.register_module("state", StateManager(kernel))

    from lam.symbolic_state import SymbolicLayer
    kernel.register_module("symbolic", SymbolicLayer(kernel))

    from core.scheduler import Scheduler
    scheduler = Scheduler(kernel)
    kernel.register_module("scheduler", scheduler)

    from guardian.ethical_core import Guardian
    kernel.register_module("guardian", Guardian(kernel))

    from bridge.thoth_bridge import ThothBridge
    kernel.register_module("bridge", ThothBridge(kernel))

    from core.interface import Interface
    kernel.register_module("interface", Interface(kernel, port=9999))

    # Initialize System
    kernel.initialize()

    # Define and Schedule Tasks
    def nightly_reflection_task():
        kernel.log("Scheduler", "Executing nightly reflection...")
        unimind = kernel.get_module("unimind")
        if unimind:
            unimind.reflect()
        
        with open("logs/improvement_history.log", "a") as log_file:
            log_file.write(f"{time.asctime()} - Nightly reflection triggered via Scheduler\n")
            
    scheduler.schedule_daily(2, 0, "nightly_reflection", nightly_reflection_task)
    
    kernel.start()

    print("[Daemon] Prometheus daemon active.")

    # Access Modules for Main Loop
    nlu = kernel.get_module("nlu")
    unimind = kernel.get_module("unimind")
    personality = kernel.get_module("personality")
    # memory = kernel.get_module("memory") # Used implicitly via events

    # Launch background threads (managed here or within modules? 
    # Ideally modules should manage their threads in start(), but adapting legacy)
    
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()

    threading.Thread(target=run_auto_optimization, daemon=True).start()

    # Load Codex documents (Legacy static call)
    try:
        ingest_documents("codex/data/")
    except Exception as e:
        print(f"[Daemon Warning] Codex ingestion skipped: {e}")

    os.makedirs("logs", exist_ok=True)
    last_run_date = None

    # Main Interaction Loop
    while True:
        try:
            # Scheduler handles nightly tasks now (once enabled fully)
            
            print("\n[Daemon] Enter a command or type 'exit': ", end="", flush=True)
            try:
                user_input = input().strip()
            except EOFError:
                break # Handle non-interactive mode gracefully

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
                
                # Dispatch input event to kernel for other observers
                kernel.dispatch("user_input", {"text": user_input, "result": result})

        except KeyboardInterrupt:
            print("\n[Daemon] Interrupted. Shutting down.")
            break
        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            # Prevent infinite fast loop on error
            time.sleep(1)
            continue

    kernel.stop()

if __name__ == "__main__":
    main()
