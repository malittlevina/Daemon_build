import time
import sys
import os
from datetime import date

# Core Architecture
from core.kernel import Kernel
from core.boot import load_kernel_services
from daemon.boot import load_daemon_services
from codex.ingestion import ingest_documents

def main():
    print("[System] Powering on...")
    
    # 1. Boot Kernel (The Bare Metal)
    kernel = Kernel()
    load_kernel_services(kernel)
    
    # 2. Boot Daemon (The Intelligence)
    load_daemon_services(kernel)
    
    # 3. Initialize & Start
    kernel.initialize()
    
    # Legacy: Scheduled Tasks setup (moved here or kept in modules)
    # The Scheduler module now handles tasks, but we can register specific ones here
    scheduler = kernel.get_module("scheduler")
    if scheduler:
        def nightly_reflection_task():
            kernel.log("Scheduler", "Executing nightly reflection...")
            unimind = kernel.get_module("unimind")
            if unimind: unimind.reflect()
            with open("logs/improvement_history.log", "a") as log_file:
                log_file.write(f"{time.asctime()} - Nightly reflection triggered via Scheduler\n")
        
        scheduler.schedule_daily(2, 0, "nightly_reflection", nightly_reflection_task)

    # 4. Start Services
    kernel.start()
    
    # 5. Load Static Knowledge
    try:
        ingest_documents("codex/data/")
    except Exception as e:
        kernel.log("Boot", f"Codex ingestion skipped: {e}", level="warning")

    print("[System] Prometheus Daemon Active.")

    # 6. Main Interaction Loop (Shell)
    shell = kernel.get_module("shell")
    
    while True:
        try:
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
                print("[System] Shutting down.")
                break
            
            # Delegate processing to Shell Module
            if shell:
                shell.process_input(user_input)
            else:
                pass # Fallback if shell missing

        except KeyboardInterrupt:
            print("\n[System] Interrupted. Shutting down.")
            break
        except Exception as loop_error:
            print(f"[System Critical Loop Error] {loop_error}")
            time.sleep(1)
            continue

    kernel.stop()

if __name__ == "__main__":
    main()
