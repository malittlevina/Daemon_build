import sys
import os
import time
import json
import threading

# Add workspace to path
sys.path.append(os.getcwd())

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "PASS": "\033[92m",
        "FAIL": "\033[91m",
        "WARN": "\033[93m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}[{status}] {msg}{colors['RESET']}")

def run_checks():
    log("Starting Comprehensive Debug Suite...", "INFO")
    
    results = {"PASS": 0, "FAIL": 0}

    def check(name, func):
        try:
            func()
            log(f"{name}: OK", "PASS")
            results["PASS"] += 1
        except Exception as e:
            log(f"{name}: FAILED - {str(e)}", "FAIL")
            results["FAIL"] += 1

    # 1. Dependency Check
    def check_dependencies():
        import flask
        import flask_cors
        import psutil
        import websockets
        import numpy
        import cv2
    check("Dependency Import", check_dependencies)

    # 2. Config Check
    def check_config():
        from config.system_config.json import load # Error expected if logic manual
        # Actually just check file existence
        if not os.path.exists("config/system_config.json"):
            raise FileNotFoundError("config/system_config.json missing")
    check("Configuration File", lambda: open("config/system_config.json"))

    # 3. Core Unimind
    def check_unimind():
        from unimind.core import Unimind
        u = Unimind()
        if not u.modules: raise ValueError("Unimind initialized empty")
    check("Unimind Core", check_unimind)

    # 4. World Engine
    def check_world():
        from world_engine.core import WorldEngine
        w = WorldEngine(enable_server=False) # Disable server to avoid port conflict
        w.step()
        if w.state.time <= 0: raise ValueError("World time did not advance")
    check("World Engine Simulation", check_world)

    # 5. Knowledge/Codex
    def check_codex():
        from codex.lexicon import Lexicon
        from codex.curriculum import CurriculumManager
        l = Lexicon()
        l.define("debug_test", "A test entry", "noun")
        if not l.lookup("debug_test"): raise ValueError("Lexicon write/read failed")
        
        c = CurriculumManager()
        if "MasterCoding" not in c.packs: raise ValueError("Bootstrap curriculum missing")
    check("Codex (Lexicon & Curriculum)", check_codex)

    # 6. Brain (Neural Net)
    def check_brain():
        from cognitive.brain.neural_net import NeuralNet
        import numpy as np
        nn = NeuralNet(10, 5, 2)
        res = nn.forward(np.random.rand(1, 10))
        if res.shape != (1, 2): raise ValueError(f"Output shape mismatch: {res.shape}")
    check("Neural Net (NumPy)", check_brain)

    # 7. NLU & Personality
    def check_nlu():
        from nlu.nlu_engine import NLUEngine
        from unimind.drives import DriveSystem
        drives = DriveSystem()
        nlu = NLUEngine()
        response = nlu.interpret("hello", context_drives=drives)
        if not response: raise ValueError("NLU returned empty response")
    check("NLU & Personality", check_nlu)

    # 8. Sensor Manager (Instantiate only)
    def check_sensors():
        from sensors.sensor_manager import SensorManager
        s = SensorManager()
        # Don't start loop, just check init
        if not hasattr(s, 'vision'): raise ValueError("SensorManager missing vision")
    check("Sensor Manager Init", check_sensors)

    # 9. Avatar
    def check_avatar():
        from avatar.avatar_engine import AvatarEngine
        from avatar.ascii_renderer import ASCIIRenderer
        eng = AvatarEngine()
        ren = ASCIIRenderer()
        vis = ren.render(eng.get_current_visual_state())
        if "---" not in vis: raise ValueError("Avatar render failed")
    check("Avatar System", check_avatar)

    log(f"\nDebug Complete. Passed: {results['PASS']}, Failed: {results['FAIL']}", "INFO")
    if results['FAIL'] > 0:
        log("System is NOT healthy. Check logs above.", "WARN")
    else:
        log("System is fully operational.", "PASS")

if __name__ == "__main__":
    run_checks()
