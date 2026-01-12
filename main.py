#!/usr/bin/env python3
"""
Prometheus Daemon - AI Companion
================================
The main entry point for the Prometheus AI daemon.
Operates independently and can optionally connect to ThothOS.

Architecture:
- Unimind: Central cortex and event bus
- Cognition: LLM/NLU/LAM thought pipeline  
- Observer: Memory garden and mind palace
- Devices: Wearables and companion devices
- Bridge: Optional ThothOS connection
"""

import threading
import subprocess
import json
import time
import os
from datetime import date

# Import daemon core
from daemon.daemon_core import Daemon, DaemonConfig, init_daemon

# Legacy imports for backwards compatibility
from unimind.core import Unimind
from prometheus.specialties import PrometheusSpecialties
from codex.ingestion import ingest_documents
from emotion.emotion_engine import EmotionEngine
from rituals.ritual_registry import RitualRegistry
from introspection.personality_tracker import PersonalityTracker
from memory_tree.memory_logger import MemoryLogger
from optimizer.auto_upgrade import run_auto_optimization
from scrolls.scroll_engine import ScrollEngine
from nlu.nlu_engine import NLUEngine
from nlu.device_commands import handle_device_command
from observer.integration import handle_observer_command


def load_config() -> dict:
    """Load daemon configuration."""
    config_path = "config/daemon_config.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Main] Config error: {e}")
    return {}


def main():
    """Main entry point for the daemon."""
    print("=" * 50)
    print("  Prometheus Daemon - AI Companion")
    print("=" * 50)
    print()
    
    # Load configuration
    config = load_config()
    
    # Create daemon config
    daemon_config = DaemonConfig(
        name=config.get('name', 'Prometheus'),
        version=config.get('version', '1.0.0'),
        enable_voice=config.get('voice_listener_enabled', False),
        enable_vision=config.get('camera_sensor_enabled', False),
        enable_devices=config.get('device_discovery_enabled', True),
        enable_observer=config.get('observer_enabled', True),
        enable_thoth_bridge=config.get('thoth_bridge', {}).get('enabled', False),
        use_ollama=config.get('cognition', {}).get('use_ollama', True),
        ollama_model=config.get('cognition', {}).get('ollama_model', 'llama3'),
    )
    
    # Initialize daemon
    daemon = init_daemon(daemon_config)
    
    # Additional initialization
    prom = PrometheusSpecialties()
    emotions = EmotionEngine()
    rituals = RitualRegistry()
    scrolls = ScrollEngine()
    personality = PersonalityTracker()
    
    # Initialize NLU with scroll engine
    try:
        nlu = NLUEngine(scrolls)
    except Exception as e:
        print(f"[Main] NLU init error: {e}")
        nlu = None
    
    # Start background optimization
    if config.get('auto_optimization', True):
        threading.Thread(target=run_auto_optimization, daemon=True).start()
    
    # Load Codex documents
    ingest_documents("codex/data/")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    print()
    print(daemon.describe())
    print()
    print("[Daemon] Ready. Type 'help' for commands or 'exit' to quit.")
    print()
    
    # Track nightly reflection
    last_run_date = None
    
    # Main loop
    while daemon.is_running:
        try:
            # Nightly reflection at 2 AM
            current_hour = time.localtime().tm_hour
            today = date.today()
            if current_hour == 2 and last_run_date != today:
                print("[Daemon] Running nightly reflection...")
                if daemon.unimind:
                    daemon.unimind.reflect()
                if daemon.observer:
                    daemon.observer.tend_garden()
                with open("logs/improvement_history.log", "a") as log_file:
                    log_file.write(f"{time.asctime()} - Nightly reflection triggered\n")
                last_run_date = today
            
            # Get user input
            try:
                user_input = input("[You] ").strip()
            except EOFError:
                break
            
            # Handle exit
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("[Daemon] Goodbye! Take care.")
                break
            
            # Handle empty input
            if not user_input:
                continue
            
            # Process input through daemon
            response = daemon.process_input(user_input)
            
            # If no response from daemon handlers, try NLU
            if not response or response.startswith("[Unimind] Processed:"):
                if nlu:
                    try:
                        nlu_response = nlu.interpret(user_input)
                        if nlu_response and not nlu_response.startswith("[NLUEngine] No known intent"):
                            response = nlu_response
                    except Exception as e:
                        print(f"[Daemon] NLU error: {e}")
            
            # Print response
            if response:
                print(f"[{daemon_config.name}] {response}")
            print()
            
        except KeyboardInterrupt:
            print("\n[Daemon] Interrupted. Shutting down...")
            break
        except Exception as e:
            print(f"[Daemon] Error: {e}")
            continue
    
    # Shutdown
    daemon.shutdown()
    print("[Daemon] Shutdown complete.")


if __name__ == "__main__":
    main()
