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
import uuid
from datetime import date
from daemon.state_manager import StateManager
from core.event_bus import GLOBAL_EVENT_BUS
from core.event_sinks import start_jsonl_event_sink
from kernel.kernel import Kernel
from kernel.actions import ActionSpec
from kernel.adapters import RitualsService, StateService, UnimindService
from kernel.identity import Principal
from kernel.services import ServiceInfo

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback

if __name__ == "__main__":
    unimind = Unimind()
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    memory = MemoryLogger()
    state = StateManager()
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
    GLOBAL_EVENT_BUS.publish("daemon.start", {"name": "Prometheus"}, source="daemon", tags=["daemon"])

    # Kernel boot (service registry + actions + policy/caps + scheduler + IPC)
    kernel = Kernel(event_bus=GLOBAL_EVENT_BUS)

    kernel.register_service(ServiceInfo(name="unimind", kind="agent", provides=["reflect"]), UnimindService(unimind))
    kernel.register_service(ServiceInfo(name="rituals", kind="registry", provides=["cast"]), RitualsService(rituals))
    kernel.register_service(ServiceInfo(name="state", kind="state", provides=["get", "set"]), StateService(state))

    ui_principal = Principal(id="ui", kind="ui", roles=["ui"])
    # Bootstrap caps for the local UI (tighten later with sessions/approvals).
    kernel.caps.grant(ui_principal, "daemon.control", "unimind.control", "rituals.cast")

    kernel.register_action(
        ActionSpec(
            name="daemon.toggle_pause",
            description="Toggle daemon paused state",
            required_caps=["daemon.control"],
            tags=["daemon", "state"],
            fn=lambda args, principal: {"paused": bool(state.toggle_pause())},
        )
    )
    kernel.register_action(
        ActionSpec(
            name="unimind.reflect",
            description="Run Unimind reflection loop",
            required_caps=["unimind.control"],
            tags=["unimind"],
            fn=lambda args, principal: (unimind.reflect() or {"ok": True}),
        )
    )
    kernel.register_action(
        ActionSpec(
            name="ritual.cast",
            description="Cast a ritual by name",
            args_schema={"ritual_name": "string", "context": "object (optional)"},
            required_caps=["rituals.cast"],
            tags=["rituals"],
            fn=lambda args, principal: {"result": rituals.cast_ritual(str(args.get("ritual_name", "")).strip(), context=args.get("context") or {})},
        )
    )

    # Launch sensors and background modules in threads
    ENABLE_VOICE = False
    # To enable the voice listener, set ENABLE_VOICE = True above.
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()
    # threading.Thread(target=vision.classify_surroundings, daemon=True).start()
    threading.Thread(target=run_auto_optimization, daemon=True).start()

    # Optional event persistence (timeline replay/training)
    ENABLE_EVENT_LOG = os.getenv("ENABLE_EVENT_LOG", "0") in ("1", "true", "True", "yes", "YES")
    if ENABLE_EVENT_LOG:
        try:
            start_jsonl_event_sink(GLOBAL_EVENT_BUS, path=os.getenv("EVENT_LOG_PATH", "logs/agent_ui_events.jsonl"))
            print("[EventLog] Writing JSONL to logs/agent_ui_events.jsonl")
        except Exception as e:
            print(f"[EventLog] Failed to start: {e}")
            GLOBAL_EVENT_BUS.publish("event_log.error", {"error": str(e)}, source="daemon", severity="error", tags=["daemon"])

    # Optional AI-first GUI contract server (state/actions/events)
    ENABLE_AGENT_UI = os.getenv("ENABLE_AGENT_UI", "0") in ("1", "true", "True", "yes", "YES")
    if ENABLE_AGENT_UI:
        try:
            from gui.context import DaemonUIContext
            from gui.agent_ui_server import start_agent_ui_server

            ui_context = DaemonUIContext(unimind=unimind, rituals=rituals, state=state, kernel=kernel)
            start_agent_ui_server(ui_context=ui_context, host="127.0.0.1", port=8765, background=True)
            print("[AgentUI] Running at http://127.0.0.1:8765")
        except Exception as e:
            print(f"[AgentUI] Failed to start: {e}")
            GLOBAL_EVENT_BUS.publish("ui.server.error", {"error": str(e)}, source="ui", severity="error", tags=["ui"])

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
                GLOBAL_EVENT_BUS.publish("daemon.stop", {}, source="daemon", tags=["daemon"])
                break
            elif user_input == "":
                personality.log_state()
                GLOBAL_EVENT_BUS.publish("daemon.reflect.tick", {}, source="daemon", tags=["daemon", "unimind"])
                unimind.reflect()
            else:
                trace_id = str(uuid.uuid4())
                result = None
                if nlu:
                    try:
                        GLOBAL_EVENT_BUS.publish(
                            "daemon.input",
                            {"text": user_input, "trace_id": trace_id},
                            source="daemon",
                            tags=["input", f"trace:{trace_id}"],
                        )
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
                GLOBAL_EVENT_BUS.publish(
                    "daemon.output",
                    {"result": result, "trace_id": trace_id},
                    source="daemon",
                    tags=["output"] + ([f"trace:{trace_id}"] if trace_id else []),
                )
                # Kernel tick (timers/cron hooks)
                kernel.tick()

        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            GLOBAL_EVENT_BUS.publish("daemon.loop.error", {"error": str(loop_error)}, source="daemon", severity="error", tags=["daemon"])
            continue