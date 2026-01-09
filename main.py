#!/usr/bin/env python3
"""
ThothOS Daemon - Prometheus Build (v2_origin)

A symbolic AI operating system with kernel-based architecture.
"""

import threading
import time
import os
import json
from datetime import date

# Kernel imports
from kernel import Kernel
from kernel.boot_loader import BootLoader
from kernel.kernel_registry import ModuleType

# Flag to control use of Ollama fallback
USE_OLLAMA = False  # Set to True to enable Ollama fallback


def handle_fallback(text: str) -> str:
    """Handle fallback for unknown intents."""
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


def nightly_reflection(kernel: Kernel, boot_loader: BootLoader):
    """Perform nightly reflection and self-improvement."""
    from code_tools import code_generator
    
    unimind = boot_loader.loaded_modules.get("unimind")
    if unimind:
        unimind.reflect()
    
    code_generator.propose_improvements("Nightly system reflection and improvement")
    
    with open("logs/improvement_history.log", "a") as log_file:
        log_file.write(f"{time.asctime()} - Nightly reflection and improvement triggered\n")


def daemon_loop(kernel: Kernel, boot_loader: BootLoader):
    """Main daemon interaction loop."""
    last_run_date = None
    nlu = boot_loader.loaded_modules.get("nlu")
    personality = boot_loader.loaded_modules.get("personality")
    unimind = boot_loader.loaded_modules.get("unimind")
    
    print("\n[Daemon] Prometheus is ready. Type 'exit' to quit, 'status' for kernel status.")
    
    while True:
        try:
            # Nightly reflection at 2 AM
            current_hour = time.localtime().tm_hour
            today = date.today()
            if current_hour == 2 and last_run_date != today:
                nightly_reflection(kernel, boot_loader)
                last_run_date = today
            
            print("\n[Daemon] > ", end="", flush=True)
            user_input = input().strip()
            
            if user_input.lower() == "exit":
                print("[Daemon] Shutting down...")
                kernel.shutdown()
                break
                
            elif user_input.lower() == "status":
                status = kernel.get_status()
                print("\n=== Kernel Status ===")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                print()
                
            elif user_input.lower() == "modules":
                modules = kernel.registry.get_all_modules()
                print("\n=== Registered Modules ===")
                for name, info in modules.items():
                    print(f"  {name}: {info.state.name} ({info.module_type.name})")
                print()
                
            elif user_input.lower() == "help":
                print("\n=== Daemon Commands ===")
                print("  status   - Show kernel status")
                print("  modules  - List registered modules")
                print("  memory   - Show memory statistics")
                print("  tasks    - Show scheduled tasks")
                print("  help     - Show this help")
                print("  exit     - Shutdown daemon")
                print()
                
            elif user_input.lower() == "memory":
                stats = kernel.memory_manager.get_stats()
                print("\n=== Memory Statistics ===")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
                
            elif user_input.lower() == "tasks":
                stats = kernel.scheduler.get_stats()
                print("\n=== Scheduler Statistics ===")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                print()
                
            elif user_input == "":
                if personality:
                    personality.log_state()
                if unimind:
                    unimind.reflect()
                    
            else:
                # Process through NLU
                result = None
                if nlu:
                    try:
                        result = nlu.interpret(user_input)
                        if result is None or (isinstance(result, str) and 
                                              result.startswith("[NLUEngine] No known intent")):
                            result = handle_fallback(user_input)
                    except Exception as e:
                        print(f"[Daemon Error] NLU failed: {e}")
                        result = handle_fallback(user_input)
                else:
                    print("[Daemon Warning] NLU not available. Using fallback response.")
                    result = handle_fallback(user_input)
                
                print(f"[Daemon] {result}")
                
                # Log to memory
                kernel.memory_manager.store(
                    f"interaction_{time.time()}",
                    {"input": user_input, "output": result},
                    namespace="context",
                    tags={"interaction", "user_input"}
                )
                
        except KeyboardInterrupt:
            print("\n[Daemon] Caught interrupt, shutting down...")
            kernel.shutdown()
            break
            
        except Exception as loop_error:
            print(f"[Daemon Critical Loop Error] {loop_error}")
            continue


def main():
    """Main entry point for the daemon."""
    print("=" * 60)
    print("  ThothOS Daemon - Prometheus Build")
    print("  Symbolic AI Operating System (Kernel Edition)")
    print("=" * 60)
    print()
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Initialize kernel
    print("[Daemon] Initializing kernel...")
    kernel = Kernel()
    
    # Boot the kernel
    if not kernel.boot():
        print("[Daemon] Kernel boot failed!")
        return
    
    # Initialize boot loader
    boot_loader = BootLoader(kernel)
    
    # Register boot hook to load modules
    def boot_modules(k):
        boot_loader.boot()
    
    kernel.register_boot_hook(boot_modules)
    
    # Execute module loading
    boot_loader.boot()
    
    # Start memory GC
    kernel.memory_manager.start_gc(interval=120)  # Every 2 minutes
    
    print(f"\n[Daemon] Kernel booted. Uptime: {kernel.get_uptime():.2f}s")
    print(f"[Daemon] Loaded {kernel.registry.count()} modules")
    
    # Run daemon loop (blocking)
    daemon_loop(kernel, boot_loader)
    
    print("[Daemon] Goodbye!")


if __name__ == "__main__":
    main()
