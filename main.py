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
from storyrealms.ux_console import StoryrealmsConsole
from storyrealms.service import StoryrealmsService
from storyrealms.http_api import start_storyrealms_http_server
from core.kernel import Kernel
from storyrealms.kernel_adapter import StoryrealmsKernelAdapter
from scrolls.kernel_adapter import ScrollsKernelAdapter
from memory_tree.kernel_adapter import MemoryKernelAdapter
from nlu.kernel_adapter import NluKernelAdapter
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
    storyrealms = StoryrealmsService()
    story_ux = StoryrealmsConsole(storyrealms)
    kernel = Kernel()
    kernel.register("storyrealms", StoryrealmsKernelAdapter(storyrealms, story_ux))
    kernel.register("scrolls", ScrollsKernelAdapter(scrolls))
    kernel.register("memory", MemoryKernelAdapter(memory))
    if os.environ.get("STORYREALMS_HTTP") == "1":
        host = os.environ.get("STORYREALMS_HTTP_HOST", "127.0.0.1")
        port = int(os.environ.get("STORYREALMS_HTTP_PORT", "7777"))
        start_storyrealms_http_server(storyrealms, host=host, port=port, daemon=True)
        print(f"[Storyrealms] HTTP API listening on {host}:{port}")
    # vision = VisionSensor()
    personality = PersonalityTracker()
    try:
        global nlu
        nlu = NLUEngine(scrolls, storyrealms=storyrealms)
        kernel.register("nlu", NluKernelAdapter(nlu))
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
                # Kernel is the single routing point.
                try:
                    kr = kernel.handle_text(user_input, actor="cli", source="cli")
                    if kr.text:
                        print(kr.text)
                    elif kr.ok and kr.data:
                        print(f"[Daemon] Result: {kr.data.get('result', kr.data)}")
                    else:
                        # Fall back to legacy behavior for anything kernel doesn't handle.
                        result = None
                        if nlu:
                            result = nlu.interpret(user_input)
                            if result is None or (isinstance(result, str) and result.startswith("[NLUEngine] No known intent")):
                                result = handle_fallback(user_input)
                        else:
                            result = handle_fallback(user_input)
                        print(f"[Daemon] NLU Result: {result}")
                except Exception as e:
                    print(f"[Daemon Kernel Error] {e}")
                    result = handle_fallback(user_input)
                    print(f"[Daemon] NLU Result: {result}")

        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            continue