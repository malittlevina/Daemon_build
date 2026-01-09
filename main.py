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

    from core.registry import Registry
    kernel.register_module("registry", Registry(kernel))

    from core.users import UserManager
    kernel.register_module("users", UserManager(kernel))

    from core.shell import Shell
    kernel.register_module("shell", Shell(kernel))

    from apps.browser import Browser
    kernel.register_module("browser", Browser(kernel))

    from apps.ide import IDE
    kernel.register_module("ide", IDE(kernel))

    from apps.calculator import Calculator
    kernel.register_module("calculator", Calculator(kernel))

    from world_engine.world import WorldEngine
    kernel.register_module("world", WorldEngine(kernel))

    from memory_tree.graph import KnowledgeGraph
    kernel.register_module("knowledge_graph", KnowledgeGraph(kernel))

    from core.packager import PackageManager
    kernel.register_module("packager", PackageManager(kernel))

    from core.vfs import VFS
    kernel.register_module("vfs", VFS(kernel))

    from core.process import ProcessManager
    kernel.register_module("process_manager", ProcessManager(kernel))

    from core.network import NetworkManager
    kernel.register_module("network", NetworkManager(kernel))

    from core.homeostasis import Homeostasis
    kernel.register_module("homeostasis", Homeostasis(kernel))

    from apps.holodeck import Holodeck
    kernel.register_module("holodeck", Holodeck(kernel))

    from apps.bard import Bard
    kernel.register_module("bard", Bard(kernel))

    from core.dreamer import Dreamer
    kernel.register_module("dreamer", Dreamer(kernel))

    from core.clipboard import Clipboard
    kernel.register_module("clipboard", Clipboard(kernel))

    from core.notifications import NotificationManager
    kernel.register_module("notifications", NotificationManager(kernel))

    from core.view import ViewManager
    kernel.register_module("view", ViewManager(kernel))

    from apps.architect import Architect
    kernel.register_module("architect", Architect(kernel))

    from apps.sims import SimController
    kernel.register_module("sims", SimController(kernel))

    from world_engine.spatial_map import SpatialMap
    kernel.register_module("spatial_map", SpatialMap(kernel))

    from bridge.xr_server import XRServer
    kernel.register_module("xr_server", XRServer(kernel))

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
    shell = kernel.get_module("shell")
    
    while True:
        try:
            # Shell prompt handled by Shell module logic usually, but here we drive it
            # To emulate full shell control, we let Shell print prompt.
            if shell:
                # Use shell's prompt
                print(f"\n{shell.prompt}", end="", flush=True)
            else:
                print("\n[Daemon] Enter a command or type 'exit': ", end="", flush=True)

            try:
                user_input = input().strip()
            except EOFError:
                break 

            if user_input.lower() == "exit":
                print("[Daemon] Shutting down.")
                break
            
            # Delegate processing to Shell Module
            if shell:
                shell.process_input(user_input)
            else:
                # Fallback Legacy Logic
                if user_input == "":
                    personality.log_state()
                    unimind.reflect()
                else:
                   # ... existing fallback code ...
                   pass

        except KeyboardInterrupt:
            print("\n[Daemon] Interrupted. Shutting down.")
            break
        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            time.sleep(1)
            continue

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
