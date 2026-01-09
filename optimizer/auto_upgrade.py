import subprocess
import shutil
import os
from codex.ingestion import ingest_observation

def run_auto_optimization():
    print("[Optimizer] Running self-optimization...")

    # 1. Dependency Check
    required_tools = ["ruff", "mypy", "pytest"]
    missing = [tool for tool in required_tools if shutil.which(tool) is None]
    
    if missing:
        print(f"[Optimizer] Missing tools: {missing}. Attempting install...")
        try:
            subprocess.run(["pip", "install"] + missing, check=True)
            print("[Optimizer] Tools installed.")
        except Exception as e:
            print(f"[Optimizer] Failed to install tools: {e}")

    # 2. Cleanup
    _cleanup_temps()

    # 3. Linting / Fixes
    try:
        # Check if ruff is available now
        if shutil.which("ruff"):
            result = subprocess.run(["ruff", "check", ".", "--fix"], capture_output=True, text=True)
            lint_output = result.stdout.strip()
            if lint_output:
                print(f"[Optimizer] Ruff Output:\n{lint_output}")
                ingest_observation({"type": "auto_optimization", "message": lint_output})
        else:
            print("[Optimizer] Ruff not available, skipping linting.")

        # Call code_generator to suggest improvements based on recent logs?
        # For now, we just log the run.
        
        print("[Optimizer] Optimization complete.")
        return "[Optimizer] Self-optimization complete."
    except Exception as e:
        print(f"[Optimizer] Optimization failed: {e}")
        return f"[Optimizer] Optimization failed: {e}"

def _cleanup_temps():
    # Remove pycache and temporary logs
    count = 0
    for root, dirs, files in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                count += 1
    if count > 0:
        print(f"[Optimizer] Cleaned up {count} __pycache__ directories.")
