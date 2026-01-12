# daemon/daemon_core.py
"""
Daemon Core
===========
The main daemon class that coordinates all subsystems.
Operates independently and can optionally connect to ThothOS.
"""

import os
import json
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

# Core imports
from unimind.core import Unimind, get_unimind, BrainRegion, SignalType
from unimind.cognition import CognitionPipeline, get_cognition

# State management
from .state_manager import StateManager


@dataclass
class DaemonConfig:
    """Configuration for the daemon."""
    # Identity
    name: str = "Prometheus"
    version: str = "1.0.0"
    
    # Features
    enable_voice: bool = False
    enable_vision: bool = False
    enable_devices: bool = True
    enable_observer: bool = True
    enable_thoth_bridge: bool = False  # ThothOS is optional
    
    # LLM
    use_ollama: bool = True
    ollama_model: str = "llama3"
    
    # Paths
    config_path: str = "config/daemon_config.json"
    state_path: str = "config/state.json"
    
    # Timing
    reflection_hour: int = 2  # 2 AM nightly reflection
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'version': self.version,
            'enable_voice': self.enable_voice,
            'enable_vision': self.enable_vision,
            'enable_devices': self.enable_devices,
            'enable_observer': self.enable_observer,
            'enable_thoth_bridge': self.enable_thoth_bridge,
            'use_ollama': self.use_ollama,
            'ollama_model': self.ollama_model,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DaemonConfig':
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


class Daemon:
    """
    The AI Daemon - a standalone AI companion.
    
    Core Architecture:
    - Unimind: Central cortex and event bus
    - Cognition: LLM/NLU/LAM thought pipeline
    - Observer: Memory and awareness
    - Devices: Wearable and device interfaces
    
    Optional:
    - ThothOS Bridge: Connect to ThothOS kernel (if available)
    """
    
    def __init__(self, config: Optional[DaemonConfig] = None):
        self.config = config or self._load_config()
        
        # Core systems
        self.unimind: Optional[Unimind] = None
        self.cognition: Optional[CognitionPipeline] = None
        self.state_manager: Optional[StateManager] = None
        
        # Optional systems
        self.observer = None
        self.device_bridge = None
        self.thoth_bridge = None
        
        # State
        self.is_running = False
        self.start_time: Optional[float] = None
        
        # Event handlers
        self._input_handlers: List[Callable[[str], Optional[str]]] = []
        
        print(f"[Daemon] {self.config.name} v{self.config.version} created.")
    
    def _load_config(self) -> DaemonConfig:
        """Load configuration from file."""
        config_path = "config/daemon_config.json"
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return DaemonConfig.from_dict(data)
            except Exception as e:
                print(f"[Daemon] Config load error: {e}")
        
        return DaemonConfig()
    
    def initialize(self) -> bool:
        """Initialize all daemon systems."""
        print(f"[Daemon] Initializing {self.config.name}...")
        
        # Initialize state manager
        self.state_manager = StateManager(self.config.state_path)
        
        # Initialize Unimind (central cortex)
        self.unimind = get_unimind()
        self.unimind.start()
        
        # Initialize cognition pipeline
        self.cognition = get_cognition()
        
        # Connect cognition to Unimind regions
        self._setup_brain_regions()
        
        # Initialize Observer (if enabled)
        if self.config.enable_observer:
            self._init_observer()
        
        # Initialize Device Bridge (if enabled)
        if self.config.enable_devices:
            self._init_devices()
        
        # Initialize ThothOS Bridge (if enabled and available)
        if self.config.enable_thoth_bridge:
            self._init_thoth_bridge()
        
        # Register input handlers
        self._register_handlers()
        
        self.start_time = time.time()
        self.is_running = True
        
        print(f"[Daemon] {self.config.name} initialized successfully.")
        return True
    
    def _setup_brain_regions(self):
        """Connect modules to Unimind brain regions."""
        # Language region -> NLU
        def language_handler(signal):
            if signal.signal_type == SignalType.QUERY:
                text = signal.payload.get('text', '')
                intent, conf, entities = self.cognition.nlu.understand(text)
                from unimind.core import Signal
                return Signal(
                    signal_type=SignalType.RESPONSE,
                    source=BrainRegion.LANGUAGE,
                    payload={'intent': intent, 'confidence': conf, 'entities': entities}
                )
            return None
        
        self.unimind.register_handler(BrainRegion.LANGUAGE, language_handler)
        
        # Cortex region -> LLM
        def cortex_handler(signal):
            if signal.signal_type == SignalType.THOUGHT:
                text = signal.payload.get('input', '')
                response = self.cognition.llm.reason(
                    text,
                    signal.payload.get('intent'),
                    signal.payload
                )
                from unimind.core import Signal
                return Signal(
                    signal_type=SignalType.RESPONSE,
                    source=BrainRegion.CORTEX,
                    payload={'response': response}
                )
            return None
        
        self.unimind.register_handler(BrainRegion.CORTEX, cortex_handler)
        
        # Planner region -> LAM
        def planner_handler(signal):
            if signal.signal_type == SignalType.PLAN:
                intent = signal.payload.get('intent')
                entities = signal.payload.get('entities', {})
                actions = self.cognition.lam.plan(intent, entities)
                from unimind.core import Signal
                return Signal(
                    signal_type=SignalType.RESPONSE,
                    source=BrainRegion.PLANNER,
                    payload={'actions': actions}
                )
            return None
        
        self.unimind.register_handler(BrainRegion.PLANNER, planner_handler)
        
        print("[Daemon] Brain regions connected.")
    
    def _init_observer(self):
        """Initialize the Observer module."""
        try:
            from observer.observer_core import get_observer
            from observer.integration import setup_observer_integration
            
            self.observer = get_observer()
            
            # Start background processing
            self.observer.start_background_processing(interval_seconds=3600)
            
            # Register with Unimind
            def memory_handler(signal):
                if signal.signal_type == SignalType.MEMORY_RECALL:
                    query = signal.payload.get('query', '')
                    results = self.observer.search_memories(query)
                    from unimind.core import Signal
                    return Signal(
                        signal_type=SignalType.RESPONSE,
                        source=BrainRegion.MEMORY,
                        payload={'memories': results}
                    )
                elif signal.signal_type == SignalType.OBSERVATION:
                    content = signal.payload.get('input', '')
                    self.observer.note(content)
                return None
            
            self.unimind.register_handler(BrainRegion.MEMORY, memory_handler)
            self.unimind.register_handler(BrainRegion.HIPPOCAMPUS, memory_handler)
            
            print("[Daemon] Observer initialized.")
            
        except Exception as e:
            print(f"[Daemon] Observer init error: {e}")
    
    def _init_devices(self):
        """Initialize device bridge."""
        try:
            from devices.device_bridge import init_device_bridge
            
            self.device_bridge = init_device_bridge()
            
            # Register device events with observer
            if self.observer:
                def on_device_event(event):
                    self.observer.observe(
                        content=f"Device {event.event_type}: {event.device_name}",
                        source="device_bridge",
                        tags=['device', event.protocol]
                    )
                self.device_bridge.subscribe_events(on_device_event)
            
            print("[Daemon] Devices initialized.")
            
        except Exception as e:
            print(f"[Daemon] Devices init error: {e}")
    
    def _init_thoth_bridge(self):
        """Initialize ThothOS bridge (optional)."""
        try:
            from bridge.thoth_bridge import ThothBridge
            
            self.thoth_bridge = ThothBridge()
            print("[Daemon] ThothOS bridge initialized (optional connection).")
            
        except Exception as e:
            print(f"[Daemon] ThothOS bridge not available: {e}")
            print("[Daemon] Continuing in standalone mode.")
    
    def _register_handlers(self):
        """Register input handlers."""
        # Device commands
        try:
            from nlu.device_commands import handle_device_command
            self._input_handlers.append(handle_device_command)
        except ImportError:
            pass
        
        # Observer commands
        try:
            from observer.integration import handle_observer_command
            self._input_handlers.append(handle_observer_command)
        except ImportError:
            pass
    
    def process_input(self, text: str) -> str:
        """
        Process user input through the daemon.
        
        Pipeline:
        1. Check registered handlers (devices, observer, etc.)
        2. Process through Unimind thought pipeline
        3. Return response
        """
        if not text or not text.strip():
            return ""
        
        # Try registered handlers first
        for handler in self._input_handlers:
            try:
                result = handler(text)
                if result:
                    return result
            except Exception as e:
                print(f"[Daemon] Handler error: {e}")
        
        # Process through Unimind
        try:
            response = self.unimind.think(text)
            return response
        except Exception as e:
            print(f"[Daemon] Think error: {e}")
            return f"[{self.config.name}] I encountered an error processing that."
    
    def observe(self, content: str, **kwargs):
        """Record an observation."""
        if self.observer:
            return self.observer.observe(content, **kwargs)
    
    def journal(self, content: str, **kwargs):
        """Write a journal entry."""
        if self.observer:
            return self.observer.journal(content, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get daemon status."""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        status = {
            'name': self.config.name,
            'version': self.config.version,
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'uptime_human': self._format_uptime(uptime),
        }
        
        if self.unimind:
            status['unimind'] = self.unimind.get_status()
        
        if self.observer:
            status['observer'] = self.observer.get_stats()
        
        if self.device_bridge:
            status['devices'] = self.device_bridge.get_status()
        
        status['thoth_connected'] = self.thoth_bridge is not None
        
        return status
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime as human readable."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}h {int((seconds % 3600) / 60)}m"
        else:
            return f"{int(seconds / 86400)}d {int((seconds % 86400) / 3600)}h"
    
    def describe(self) -> str:
        """Get a description of the daemon."""
        status = self.get_status()
        
        lines = [
            f"🤖 {self.config.name} v{self.config.version}",
            "",
            f"Status: {'Running' if status['is_running'] else 'Stopped'}",
            f"Uptime: {status['uptime_human']}",
            "",
        ]
        
        if self.unimind:
            lines.append(self.unimind.describe())
            lines.append("")
        
        if self.observer:
            lines.append(self.observer.describe())
        
        return "\n".join(lines)
    
    def shutdown(self):
        """Shutdown the daemon."""
        print(f"[Daemon] Shutting down {self.config.name}...")
        
        self.is_running = False
        
        # Shutdown systems in reverse order
        if self.device_bridge:
            try:
                self.device_bridge.shutdown()
            except Exception as e:
                print(f"[Daemon] Device bridge shutdown error: {e}")
        
        if self.observer:
            try:
                self.observer.shutdown()
            except Exception as e:
                print(f"[Daemon] Observer shutdown error: {e}")
        
        if self.unimind:
            try:
                self.unimind.shutdown()
            except Exception as e:
                print(f"[Daemon] Unimind shutdown error: {e}")
        
        print(f"[Daemon] {self.config.name} shutdown complete.")


# Global daemon instance
_daemon: Optional[Daemon] = None


def get_daemon() -> Daemon:
    """Get or create the global daemon instance."""
    global _daemon
    if _daemon is None:
        _daemon = Daemon()
    return _daemon


def init_daemon(config: Optional[DaemonConfig] = None) -> Daemon:
    """Initialize and return the global daemon."""
    global _daemon
    _daemon = Daemon(config)
    _daemon.initialize()
    return _daemon
