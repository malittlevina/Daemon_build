# kernel/boot_loader.py
"""
Boot Loader - Daemon module initialization through the kernel.

The boot loader handles:
- Loading daemon modules in dependency order
- Registering modules with the kernel
- Starting module services
- Boot sequence orchestration
"""

import os
import json
import importlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from kernel.kernel_registry import ModuleType, ModuleState


class BootLoader:
    """
    Loads and initializes daemon modules through the kernel.
    """
    
    # Module definitions: name -> (import_path, class_name, type, dependencies)
    MODULE_DEFINITIONS = {
        "unimind": ("unimind.core", "Unimind", ModuleType.CORE, []),
        "prometheus": ("prometheus.specialties", "PrometheusSpecialties", ModuleType.ENGINE, ["unimind"]),
        "emotion": ("emotion.emotion_engine", "EmotionEngine", ModuleType.ENGINE, []),
        "memory": ("memory_tree.memory_logger", "MemoryLogger", ModuleType.STORAGE, []),
        "rituals": ("rituals.ritual_registry", "RitualRegistry", ModuleType.RITUAL, []),
        "scrolls": ("scrolls.scroll_engine", "ScrollEngine", ModuleType.RITUAL, []),
        "personality": ("introspection.personality_tracker", "PersonalityTracker", ModuleType.ENGINE, ["memory"]),
        "nlu": ("nlu.nlu_engine", "NLUEngine", ModuleType.ENGINE, ["scrolls"]),
        "codex": ("codex.ingestion", None, ModuleType.STORAGE, []),  # Function-based
        "state": ("daemon.state_manager", "StateManager", ModuleType.CORE, []),
    }
    
    # Optional modules that require special conditions
    OPTIONAL_MODULES = {
        "vision": ("sensors.vision", "VisionSensor", ModuleType.SENSOR, []),
        "audio": ("sensors.audio", "AudioSensor", ModuleType.SENSOR, []),
        "voice": ("voice.voice_listener", None, ModuleType.SENSOR, []),  # Thread-based
    }
    
    def __init__(self, kernel):
        """Initialize the boot loader."""
        self.kernel = kernel
        self.config = {}
        self.loaded_modules: Dict[str, Any] = {}
        self.boot_log: List[Tuple[datetime, str, str]] = []
        
    def log(self, level: str, message: str):
        """Log a boot message."""
        self.boot_log.append((datetime.now(), level, message))
        print(f"[BootLoader] [{level}] {message}")
    
    def load_config(self, config_path: str = "config/daemon_config.json") -> Dict[str, Any]:
        """Load boot configuration."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {"modules_to_load": list(self.MODULE_DEFINITIONS.keys())}
        
        self.log("INFO", f"Configuration loaded from {config_path}")
        return self.config
    
    def _resolve_load_order(self, modules: List[str]) -> List[str]:
        """Resolve module load order based on dependencies."""
        resolved = []
        seen = set()
        
        def resolve(name: str):
            if name in seen:
                return
            seen.add(name)
            
            # Get dependencies
            if name in self.MODULE_DEFINITIONS:
                deps = self.MODULE_DEFINITIONS[name][3]
            elif name in self.OPTIONAL_MODULES:
                deps = self.OPTIONAL_MODULES[name][3]
            else:
                deps = []
            
            # Resolve dependencies first
            for dep in deps:
                if dep in modules:
                    resolve(dep)
            
            resolved.append(name)
        
        for module in modules:
            resolve(module)
        
        return resolved
    
    def _load_module(self, name: str, definition: tuple) -> Optional[Any]:
        """Load a single module."""
        import_path, class_name, module_type, deps = definition
        
        try:
            # Import the module
            mod = importlib.import_module(import_path)
            
            if class_name:
                # Get the class
                cls = getattr(mod, class_name)
                
                # Check for special initialization requirements
                if name == "nlu":
                    # NLU needs scrolls engine
                    scrolls = self.loaded_modules.get("scrolls")
                    instance = cls(scrolls) if scrolls else cls(None)
                else:
                    instance = cls()
                
                return instance
            else:
                # Module is function-based, return the module itself
                return mod
                
        except Exception as e:
            self.log("ERROR", f"Failed to load {name}: {e}")
            return None
    
    def load_core_modules(self) -> Dict[str, Any]:
        """Load all core daemon modules."""
        modules_to_load = self.config.get("modules_to_load", list(self.MODULE_DEFINITIONS.keys()))
        
        # Resolve load order
        load_order = self._resolve_load_order(modules_to_load)
        
        self.log("INFO", f"Loading modules in order: {load_order}")
        
        for name in load_order:
            if name in self.MODULE_DEFINITIONS:
                definition = self.MODULE_DEFINITIONS[name]
                instance = self._load_module(name, definition)
                
                if instance:
                    self.loaded_modules[name] = instance
                    
                    # Register with kernel
                    self.kernel.registry.register_module(
                        name=name,
                        instance=instance,
                        module_type=definition[2],
                        dependencies=definition[3]
                    )
                    self.kernel.registry.set_module_state(name, ModuleState.READY)
                    
                    self.log("INFO", f"Loaded module: {name}")
        
        return self.loaded_modules
    
    def load_optional_modules(self) -> Dict[str, Any]:
        """Load optional modules based on configuration."""
        optional = {}
        
        # Voice listener
        if self.config.get("voice_listener_enabled"):
            try:
                from voice.voice_listener import start_voice_listener
                optional["voice_listener"] = start_voice_listener
                self.log("INFO", "Voice listener available")
            except Exception as e:
                self.log("WARN", f"Voice listener not available: {e}")
        
        # Vision sensor
        if self.config.get("camera_sensor_enabled"):
            try:
                from sensors.vision import VisionSensor
                optional["vision"] = VisionSensor()
                self.log("INFO", "Vision sensor available")
            except Exception as e:
                self.log("WARN", f"Vision sensor not available: {e}")
        
        return optional
    
    def start_background_services(self):
        """Start background daemon services."""
        import threading
        
        # Auto-optimization
        if self.config.get("auto_optimization"):
            try:
                from optimizer.auto_upgrade import run_auto_optimization
                self.kernel.process_manager.spawn_and_start(
                    "auto_optimizer",
                    run_auto_optimization,
                    group="background",
                    auto_restart=True
                )
                self.log("INFO", "Auto-optimization started")
            except Exception as e:
                self.log("WARN", f"Auto-optimization not available: {e}")
    
    def ingest_codex_documents(self, path: str = "codex/data/"):
        """Ingest codex documents."""
        try:
            from codex.ingestion import ingest_documents
            ingest_documents(path)
            self.log("INFO", f"Codex documents ingested from {path}")
        except Exception as e:
            self.log("WARN", f"Codex ingestion failed: {e}")
    
    def boot(self) -> bool:
        """
        Execute full boot sequence.
        
        Returns:
            True if boot successful
        """
        self.log("INFO", "=== Boot sequence started ===")
        
        try:
            # Step 1: Load configuration
            self.load_config()
            
            # Step 2: Load core modules
            self.load_core_modules()
            
            # Step 3: Load optional modules
            self.load_optional_modules()
            
            # Step 4: Start background services
            self.start_background_services()
            
            # Step 5: Ingest codex documents
            self.ingest_codex_documents()
            
            self.log("INFO", "=== Boot sequence complete ===")
            return True
            
        except Exception as e:
            self.log("ERROR", f"Boot failed: {e}")
            return False
    
    def get_boot_log(self) -> List[Tuple[datetime, str, str]]:
        """Get the boot log."""
        return self.boot_log
    
    def get_loaded_modules(self) -> Dict[str, Any]:
        """Get all loaded modules."""
        return self.loaded_modules
