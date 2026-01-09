import threading
import time
import os
from datetime import date

from core.kernel import get_kernel
from nlu.nlu_engine import NLUEngine
from storyrealms.storyrealm_bridge import get_bridge 
from unimind.core import Unimind
from prometheus.specialties import PrometheusSpecialties
from emotion.emotion_engine import EmotionEngine
from memory_tree.memory_logger import MemoryLogger
from scrolls.scroll_engine import ScrollEngine
from introspection.personality_tracker import PersonalityTracker

# --- Legacy imports for background tasks ---
from codex.ingestion import ingest_documents
from optimizer.auto_upgrade import run_auto_optimization

def main():
    # Initialize Kernel
    kernel = get_kernel()
    
    # Initialize Subsystems
    print("[Launcher] Booting subsystems...")
    
    # 1. Unimind (Logic) - Initialize FIRST so NLU can find it
    unimind = Unimind()
    kernel.register_module("unimind", unimind)
    
    # 2. NLU
    scrolls = ScrollEngine()
    nlu = NLUEngine(scrolls)
    kernel.register_module("nlu", nlu)
    
    # 3. Emotions & Personality
    emotions = EmotionEngine()
    personality = PersonalityTracker()
    kernel.register_module("emotions", emotions)
    
    # Start Kernel
    kernel.start()
    
    # Main Input Loop
    print("\n[Prometheus] System Online. Awaiting Input.")
    
    while True:
        try:
            print("\n> ", end="", flush=True)
            user_input = input().strip()
            
            if user_input.lower() in ["exit", "quit", "shutdown"]:
                kernel.stop()
                break
                
            if user_input:
                response = kernel.dispatch_input(user_input)
                print(f"[Prometheus]: {response}")
            else:
                pass
                
        except KeyboardInterrupt:
            kernel.stop()
            break
        except Exception as e:
            print(f"[Critical Error] {e}")

if __name__ == "__main__":
    main()
