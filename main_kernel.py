#!/usr/bin/env python3
"""
ThothOS Prometheus Daemon - Kernel-Powered Entry Point

This is the enhanced main entry point that boots the ThothKernel
and orchestrates all subsystems through the unified architecture.
"""

import threading
import time
import os
from datetime import date

# Kernel imports
from kernel.kernel_core import ThothKernel, get_kernel
from kernel.message_bus import MessagePriority

# Core subsystem imports
from unimind.core import Unimind
from bridge.thoth_bridge import ThothBridge
from lam.lam_planner import LAMPlanner
from lam.symbolic_state import get_current_state, update_state_with_input

# Existing module imports (for backward compatibility)
from prometheus.specialties import PrometheusSpecialties
from codex.ingestion import ingest_documents
from emotion.emotion_engine import EmotionEngine
from rituals.ritual_registry import RitualRegistry
from introspection.personality_tracker import PersonalityTracker
from memory_tree.memory_logger import MemoryLogger
from optimizer.auto_upgrade import run_auto_optimization
from scrolls.scroll_engine import ScrollEngine
from nlu.nlu_engine import NLUEngine

# Configuration
USE_OLLAMA = False  # Set to True to enable Ollama fallback
ENABLE_VOICE = False  # Set to True to enable voice listener


class PrometheusWrapper:
    """Wrapper to make existing modules kernel-compatible."""
    
    def __init__(self, name: str, instance):
        self.module_name = name
        self.dependencies = []
        self._instance = instance
        self._kernel = None
    
    def initialize(self, kernel) -> bool:
        self._kernel = kernel
        return True
    
    def start(self) -> bool:
        return True
    
    def stop(self) -> bool:
        return True
    
    def health_check(self):
        return {"status": "healthy", "wrapped": True}
    
    def __getattr__(self, name):
        return getattr(self._instance, name)


def boot_prometheus_daemon():
    """
    Boot the Prometheus daemon with the ThothKernel.
    
    This initializes all subsystems through the kernel and
    starts the main interaction loop.
    """
    print("=" * 60)
    print("  ThothOS Prometheus Daemon")
    print("  Kernel-Powered Architecture v2.0")
    print("=" * 60)
    print()
    
    # Initialize the kernel
    kernel = ThothKernel(config={
        "max_workers": 4,
        "health_check_interval": 60
    })
    
    # Create and register core modules
    print("[Boot] Initializing core modules...")
    
    # Native kernel modules
    unimind = Unimind()
    thoth_bridge = ThothBridge()
    lam_planner = LAMPlanner()
    
    kernel.register_module(unimind, "unimind")
    kernel.register_module(thoth_bridge, "thoth_bridge")
    kernel.register_module(lam_planner, "lam_planner")
    
    # Wrap existing modules for kernel compatibility
    scroll_engine = ScrollEngine()
    emotion_engine = EmotionEngine()
    memory_logger = MemoryLogger()
    rituals = RitualRegistry()
    personality = PersonalityTracker()
    prom = PrometheusSpecialties()
    
    kernel.register_module(PrometheusWrapper("scroll_engine", scroll_engine), "scroll_engine")
    kernel.register_module(PrometheusWrapper("emotion_engine", emotion_engine), "emotion_engine")
    kernel.register_module(PrometheusWrapper("memory_logger", memory_logger), "memory_logger")
    kernel.register_module(PrometheusWrapper("rituals", rituals), "rituals")
    kernel.register_module(PrometheusWrapper("personality", personality), "personality")
    kernel.register_module(PrometheusWrapper("prometheus", prom), "prometheus")
    
    # Initialize NLU with scroll engine
    try:
        nlu = NLUEngine(scroll_engine)
        kernel.register_module(PrometheusWrapper("nlu", nlu), "nlu")
    except Exception as e:
        print(f"[Boot] Warning: NLU initialization failed: {e}")
        nlu = None
    
    # Boot the kernel
    print("[Boot] Starting kernel...")
    if not kernel.boot():
        print("[Boot] ERROR: Kernel boot failed!")
        return
    
    # Start background services
    print("[Boot] Starting background services...")
    
    if ENABLE_VOICE:
        from voice.voice_listener import start_voice_listener
        threading.Thread(target=start_voice_listener, daemon=True).start()
    
    # Schedule auto-optimization
    kernel.schedule_task(
        run_auto_optimization,
        name="auto_optimization",
        interval_seconds=3600,  # Every hour
        source_module="optimizer"
    )
    
    # Load Codex documents
    print("[Boot] Loading Codex knowledge base...")
    try:
        ingest_documents("codex/data/")
    except Exception as e:
        print(f"[Boot] Codex loading warning: {e}")
    
    os.makedirs("logs", exist_ok=True)
    
    # Register ThothBridge apps
    print("[Boot] Registering ThothOS apps...")
    
    thoth_bridge.register_app("scroll", lambda payload: scroll_engine.invoke(
        payload.get("name", ""), 
        *payload.get("args", []),
        **payload.get("kwargs", {})
    ) if payload else "No scroll specified")
    
    thoth_bridge.register_app("reflect", lambda _: unimind.reflect())
    
    thoth_bridge.register_app("plan", lambda payload: lam_planner.create_plan(
        payload.get("goal", ""),
        payload.get("context", {})
    ).plan_id if payload else "No goal specified")
    
    # Subscribe to kernel events for logging
    def log_event(message):
        memory_logger.log_event(
            message.topic,
            str(message.payload),
            {"source": message.source}
        )
    
    kernel.subscribe("state.*", log_event)
    kernel.subscribe("error.*", log_event)
    
    print()
    print("[Daemon] Prometheus daemon ready.")
    print("[Daemon] Type 'help' for available commands, 'exit' to quit.")
    print()
    
    # Main interaction loop
    last_run_date = None
    
    while True:
        try:
            # Nightly reflection at 2 AM
            current_hour = time.localtime().tm_hour
            today = date.today()
            if current_hour == 2 and last_run_date != today:
                print("[Daemon] Triggering nightly reflection...")
                kernel.publish("daemon.nightly_reflection", {}, "daemon")
                unimind.reflect()
                from code_tools import code_generator
                code_generator.propose_improvements("Nightly system reflection and improvement")
                last_run_date = today
            
            # Get user input
            print("\n[Daemon] Enter a command: ", end="", flush=True)
            user_input = input().strip()
            
            if not user_input:
                # Empty input - quick status
                status = kernel.get_status()
                print(f"[Status] Kernel: {status['state']} | Modules: {len(status['modules'])} active")
                continue
            
            if user_input.lower() == "exit":
                print("[Daemon] Shutting down...")
                kernel.shutdown()
                break
            
            if user_input.lower() == "help":
                print_help()
                continue
            
            if user_input.lower() == "status":
                print_status(kernel)
                continue
            
            if user_input.lower() == "reflect":
                reflection = unimind.reflect()
                print(f"\n[Reflection]\n{format_dict(reflection)}")
                continue
            
            if user_input.lower().startswith("plan "):
                goal = user_input[5:].strip()
                plan = lam_planner.create_plan(goal)
                print(f"\n[Plan Created] ID: {plan.plan_id}")
                print(f"Actions: {len(plan.actions)}")
                for action in plan.actions:
                    print(f"  - {action.name}: {action.description}")
                continue
            
            if user_input.lower().startswith("execute "):
                plan_id = user_input[8:].strip()
                result = lam_planner.execute_plan(plan_id, async_mode=False)
                print(f"\n[Execution Result]\n{format_dict(result)}")
                continue
            
            if user_input.lower() == "apps":
                apps = thoth_bridge.list_apps()
                print("\n[Registered Apps]")
                for app in apps:
                    print(f"  - {app['name']}: {app['state']}")
                continue
            
            # Process through NLU and symbolic state
            update_state_with_input(user_input, source="user")
            
            result = None
            if nlu:
                try:
                    result = nlu.interpret(user_input)
                    if result is None or (isinstance(result, str) and "No known intent" in result):
                        # Try LAM planner
                        result = lam_planner.plan_next_action(user_input, get_current_state())
                except Exception as e:
                    print(f"[Error] NLU failed: {e}")
                    result = lam_planner.plan_next_action(user_input, get_current_state())
            else:
                result = lam_planner.plan_next_action(user_input, get_current_state())
            
            # Also get Unimind reasoning
            thought_result = unimind.think(user_input)
            
            print(f"\n[Response] {result}")
            if thought_result.get("confidence", 0) > 0.5:
                print(f"[Reasoning] {thought_result.get('conclusion', '')}")
            
            # Log to memory
            memory_logger.log_event("interaction", user_input, {"response": str(result)})
            
        except KeyboardInterrupt:
            print("\n[Daemon] Interrupted. Shutting down...")
            kernel.shutdown()
            break
        except Exception as e:
            print(f"[Error] {e}")
            continue


def print_help():
    """Print available commands."""
    print("""
╔══════════════════════════════════════════════════════════╗
║                 Prometheus Daemon Commands                ║
╠══════════════════════════════════════════════════════════╣
║  help          - Show this help message                   ║
║  status        - Show kernel and module status            ║
║  reflect       - Trigger system reflection                ║
║  plan <goal>   - Create an execution plan for a goal      ║
║  execute <id>  - Execute a plan by ID                     ║
║  apps          - List registered ThothOS apps             ║
║  exit          - Shutdown the daemon                      ║
╠══════════════════════════════════════════════════════════╣
║  Natural language commands are also supported:            ║
║  - "study python"        - Activate learning protocol     ║
║  - "optimize self"       - Run self-optimization          ║
║  - "run task X"          - Execute a task                 ║
║  - "reflect on X"        - Trigger introspection          ║
╚══════════════════════════════════════════════════════════╝
""")


def print_status(kernel):
    """Print detailed status."""
    status = kernel.get_status()
    print(f"""
╔══════════════════════════════════════════════════════════╗
║                    Kernel Status                          ║
╠══════════════════════════════════════════════════════════╣
║  State: {status['state']:<48} ║
║  Uptime: {format_uptime(status.get('uptime_seconds', 0)):<47} ║
╠══════════════════════════════════════════════════════════╣
║  Modules:                                                 ║""")
    
    for name, info in status['modules'].items():
        state_str = f"{name}: {info['state']}"
        print(f"║    {state_str:<52} ║")
    
    print(f"""╠══════════════════════════════════════════════════════════╣
║  Message Bus: {status['message_bus']['total_subscribers']} subscribers, {status['message_bus']['queue_size']} queued       ║
║  Scheduler: {status['scheduler']['active_workers']}/{status['scheduler']['max_workers']} workers, {status['scheduler']['pending_count']} pending        ║
╚══════════════════════════════════════════════════════════╝""")


def format_uptime(seconds):
    """Format uptime in human-readable form."""
    if seconds is None:
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}h {minutes}m {secs}s"


def format_dict(d, indent=2):
    """Format a dict for display."""
    import json
    return json.dumps(d, indent=indent, default=str)


if __name__ == "__main__":
    boot_prometheus_daemon()
