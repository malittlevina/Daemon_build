# daemon/os_adapter.py
"""
OS Compatibility Layer with ThothOS Preference System

This module enables the daemon to run on any operating system while
maintaining a strong preference and priority for ThothOS (our native
symbolic operating system). When running on ThothOS, the daemon unlocks
full capabilities; on other OSes, it operates in compatibility mode.
"""

import os
import platform
import json
from enum import Enum
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass, field


class OSType(Enum):
    """Supported operating system types."""
    THOTH_OS = "thothos"      # Our native symbolic OS - highest priority
    LINUX = "linux"
    MACOS = "darwin"
    WINDOWS = "windows"
    BSD = "bsd"
    UNKNOWN = "unknown"


class CompatibilityMode(Enum):
    """Daemon operating modes based on host OS."""
    NATIVE = "native"           # Full ThothOS integration - all features unlocked
    ENHANCED = "enhanced"       # Linux/macOS - most features available
    STANDARD = "standard"       # Windows/BSD - core features only
    MINIMAL = "minimal"         # Unknown OS - basic operation


@dataclass
class OSCapabilities:
    """Capabilities available on each OS type."""
    symbolic_commands: bool = False      # Native symbolic command execution
    memory_tree_sync: bool = False       # Full memory tree synchronization
    realm_bridging: bool = False         # Storyrealms and XR environment access
    scroll_engine_native: bool = False   # Native scroll execution
    thoth_app_integration: bool = False  # ThothOS native app communication
    voice_native: bool = False           # Native voice subsystem
    sensor_fusion: bool = False          # Multi-sensor fusion capabilities
    self_evolution: bool = False         # Self-modification and evolution
    daemon_persistence: bool = True      # Daemon can persist state
    network_bridge: bool = True          # Network communication
    file_access: bool = True             # Local file system access
    subprocess_exec: bool = True         # Can execute subprocesses


# Define capabilities per OS type
OS_CAPABILITY_MAP: Dict[OSType, OSCapabilities] = {
    OSType.THOTH_OS: OSCapabilities(
        symbolic_commands=True,
        memory_tree_sync=True,
        realm_bridging=True,
        scroll_engine_native=True,
        thoth_app_integration=True,
        voice_native=True,
        sensor_fusion=True,
        self_evolution=True,
        daemon_persistence=True,
        network_bridge=True,
        file_access=True,
        subprocess_exec=True
    ),
    OSType.LINUX: OSCapabilities(
        symbolic_commands=False,
        memory_tree_sync=True,
        realm_bridging=False,
        scroll_engine_native=False,
        thoth_app_integration=False,
        voice_native=False,
        sensor_fusion=True,
        self_evolution=True,
        daemon_persistence=True,
        network_bridge=True,
        file_access=True,
        subprocess_exec=True
    ),
    OSType.MACOS: OSCapabilities(
        symbolic_commands=False,
        memory_tree_sync=True,
        realm_bridging=False,
        scroll_engine_native=False,
        thoth_app_integration=False,
        voice_native=False,
        sensor_fusion=True,
        self_evolution=True,
        daemon_persistence=True,
        network_bridge=True,
        file_access=True,
        subprocess_exec=True
    ),
    OSType.WINDOWS: OSCapabilities(
        symbolic_commands=False,
        memory_tree_sync=True,
        realm_bridging=False,
        scroll_engine_native=False,
        thoth_app_integration=False,
        voice_native=False,
        sensor_fusion=False,
        self_evolution=False,
        daemon_persistence=True,
        network_bridge=True,
        file_access=True,
        subprocess_exec=True
    ),
    OSType.BSD: OSCapabilities(
        symbolic_commands=False,
        memory_tree_sync=True,
        realm_bridging=False,
        scroll_engine_native=False,
        thoth_app_integration=False,
        voice_native=False,
        sensor_fusion=False,
        self_evolution=False,
        daemon_persistence=True,
        network_bridge=True,
        file_access=True,
        subprocess_exec=True
    ),
    OSType.UNKNOWN: OSCapabilities(
        symbolic_commands=False,
        memory_tree_sync=False,
        realm_bridging=False,
        scroll_engine_native=False,
        thoth_app_integration=False,
        voice_native=False,
        sensor_fusion=False,
        self_evolution=False,
        daemon_persistence=True,
        network_bridge=True,
        file_access=True,
        subprocess_exec=False
    )
}


class OSAdapter:
    """
    The OSAdapter is the central compatibility layer that enables the daemon
    to operate across multiple operating systems while maintaining ThothOS
    as the preferred and prioritized environment.
    
    Key Principles:
    1. DETECT: Automatically identify the host operating system
    2. PREFER: Always check for ThothOS presence and prioritize it
    3. ADAPT: Scale capabilities based on host OS features
    4. BRIDGE: Provide consistent interfaces regardless of OS
    """
    
    # ThothOS detection markers
    THOTH_MARKERS = [
        "/etc/thothos-release",
        "/var/lib/thothos/daemon.lock",
        "~/.thothos/identity",
        "/opt/thothos/core"
    ]
    
    THOTH_ENV_VARS = [
        "THOTHOS_VERSION",
        "THOTHOS_DAEMON_ID",
        "THOTHOS_REALM"
    ]
    
    def __init__(self, config_path: str = "config/daemon_config.json"):
        self.config_path = config_path
        self._detected_os: Optional[OSType] = None
        self._mode: Optional[CompatibilityMode] = None
        self._capabilities: Optional[OSCapabilities] = None
        self._thoth_preferred: bool = True
        self._os_handlers: Dict[OSType, Dict[str, Callable]] = {}
        self._preference_score: float = 0.0
        
        # Load configuration
        self._load_config()
        
        # Perform OS detection
        self._detect_os()
        
        # Initialize OS-specific handlers
        self._init_handlers()
        
        print(f"[OSAdapter] Initialized on {self._detected_os.value} in {self._mode.value} mode")
    
    def _load_config(self):
        """Load OS preference configuration."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    os_config = config.get("os_preference", {})
                    self._thoth_preferred = os_config.get("prefer_thothos", True)
        except Exception as e:
            print(f"[OSAdapter] Config load warning: {e}")
            self._thoth_preferred = True
    
    def _detect_os(self):
        """
        Detect the host operating system with ThothOS priority.
        
        Detection order (by priority):
        1. Check for ThothOS markers first (always prioritized)
        2. Fall back to standard OS detection
        """
        # Priority 1: Check for ThothOS
        if self._thoth_preferred and self._is_thothos():
            self._detected_os = OSType.THOTH_OS
            self._mode = CompatibilityMode.NATIVE
            self._preference_score = 1.0
            print("[OSAdapter] 🌟 ThothOS detected - Running in NATIVE mode with full capabilities")
        else:
            # Standard OS detection
            system = platform.system().lower()
            
            if system == "linux":
                self._detected_os = OSType.LINUX
                self._mode = CompatibilityMode.ENHANCED
                self._preference_score = 0.8
            elif system == "darwin":
                self._detected_os = OSType.MACOS
                self._mode = CompatibilityMode.ENHANCED
                self._preference_score = 0.75
            elif system == "windows":
                self._detected_os = OSType.WINDOWS
                self._mode = CompatibilityMode.STANDARD
                self._preference_score = 0.5
            elif "bsd" in system:
                self._detected_os = OSType.BSD
                self._mode = CompatibilityMode.STANDARD
                self._preference_score = 0.5
            else:
                self._detected_os = OSType.UNKNOWN
                self._mode = CompatibilityMode.MINIMAL
                self._preference_score = 0.25
            
            if self._thoth_preferred:
                print(f"[OSAdapter] Running on {self._detected_os.value} - ThothOS preferred but not detected")
                print(f"[OSAdapter] Tip: Install ThothOS to unlock full daemon capabilities")
        
        # Set capabilities based on detected OS
        self._capabilities = OS_CAPABILITY_MAP.get(self._detected_os, OS_CAPABILITY_MAP[OSType.UNKNOWN])
    
    def _is_thothos(self) -> bool:
        """Check if running on ThothOS."""
        # Check environment variables
        for env_var in self.THOTH_ENV_VARS:
            if os.environ.get(env_var):
                return True
        
        # Check filesystem markers
        for marker in self.THOTH_MARKERS:
            expanded = os.path.expanduser(marker)
            if os.path.exists(expanded):
                return True
        
        return False
    
    def _init_handlers(self):
        """Initialize OS-specific command handlers."""
        # ThothOS native handlers
        self._os_handlers[OSType.THOTH_OS] = {
            "execute_symbolic": self._thoth_symbolic_exec,
            "sync_memory": self._thoth_memory_sync,
            "bridge_realm": self._thoth_realm_bridge,
            "notify": self._thoth_notify,
            "persist_state": self._thoth_persist
        }
        
        # Linux handlers
        self._os_handlers[OSType.LINUX] = {
            "execute_symbolic": self._linux_symbolic_fallback,
            "sync_memory": self._linux_memory_sync,
            "bridge_realm": self._noop_handler,
            "notify": self._linux_notify,
            "persist_state": self._generic_persist
        }
        
        # macOS handlers
        self._os_handlers[OSType.MACOS] = {
            "execute_symbolic": self._macos_symbolic_fallback,
            "sync_memory": self._macos_memory_sync,
            "bridge_realm": self._noop_handler,
            "notify": self._macos_notify,
            "persist_state": self._generic_persist
        }
        
        # Windows handlers
        self._os_handlers[OSType.WINDOWS] = {
            "execute_symbolic": self._windows_symbolic_fallback,
            "sync_memory": self._windows_memory_sync,
            "bridge_realm": self._noop_handler,
            "notify": self._windows_notify,
            "persist_state": self._generic_persist
        }
        
        # BSD handlers
        self._os_handlers[OSType.BSD] = {
            "execute_symbolic": self._linux_symbolic_fallback,
            "sync_memory": self._linux_memory_sync,
            "bridge_realm": self._noop_handler,
            "notify": self._linux_notify,
            "persist_state": self._generic_persist
        }
        
        # Unknown OS handlers
        self._os_handlers[OSType.UNKNOWN] = {
            "execute_symbolic": self._noop_handler,
            "sync_memory": self._noop_handler,
            "bridge_realm": self._noop_handler,
            "notify": self._generic_notify,
            "persist_state": self._generic_persist
        }
    
    # ==================== PUBLIC API ====================
    
    @property
    def os_type(self) -> OSType:
        """Get the detected OS type."""
        return self._detected_os
    
    @property
    def mode(self) -> CompatibilityMode:
        """Get the current compatibility mode."""
        return self._mode
    
    @property
    def capabilities(self) -> OSCapabilities:
        """Get available capabilities for current OS."""
        return self._capabilities
    
    @property
    def is_native(self) -> bool:
        """Check if running on ThothOS (native mode)."""
        return self._detected_os == OSType.THOTH_OS
    
    @property
    def preference_score(self) -> float:
        """Get OS preference score (0-1, 1 being ThothOS)."""
        return self._preference_score
    
    def can(self, capability: str) -> bool:
        """Check if a capability is available."""
        return getattr(self._capabilities, capability, False)
    
    def execute(self, action: str, *args, **kwargs) -> Any:
        """
        Execute an action through the appropriate OS handler.
        Automatically routes to the correct handler based on detected OS.
        """
        handlers = self._os_handlers.get(self._detected_os, {})
        handler = handlers.get(action, self._noop_handler)
        return handler(*args, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current OS adapter status."""
        return {
            "os_type": self._detected_os.value,
            "mode": self._mode.value,
            "preference_score": self._preference_score,
            "is_native": self.is_native,
            "thoth_preferred": self._thoth_preferred,
            "capabilities": {
                "symbolic_commands": self._capabilities.symbolic_commands,
                "memory_tree_sync": self._capabilities.memory_tree_sync,
                "realm_bridging": self._capabilities.realm_bridging,
                "scroll_engine_native": self._capabilities.scroll_engine_native,
                "thoth_app_integration": self._capabilities.thoth_app_integration,
                "voice_native": self._capabilities.voice_native,
                "sensor_fusion": self._capabilities.sensor_fusion,
                "self_evolution": self._capabilities.self_evolution
            }
        }
    
    def suggest_upgrade(self) -> Optional[str]:
        """Suggest ThothOS upgrade if not running natively."""
        if self.is_native:
            return None
        
        suggestions = {
            OSType.LINUX: "Your Linux system is compatible! Install ThothOS layer: `curl -sSL install.thothos.dev | bash`",
            OSType.MACOS: "macOS detected. ThothOS can run as a virtualized layer: `brew install thothos-daemon`",
            OSType.WINDOWS: "Windows detected. Consider WSL2 with ThothOS: `wsl --install thothos`",
            OSType.BSD: "BSD system detected. ThothOS ports available: `pkg install thothos-daemon`",
            OSType.UNKNOWN: "Unknown OS. Visit https://thothos.dev/compatibility for installation options."
        }
        return suggestions.get(self._detected_os)
    
    # ==================== THOTHOS NATIVE HANDLERS ====================
    
    def _thoth_symbolic_exec(self, command: str, context: Dict = None) -> Dict:
        """Execute symbolic command natively on ThothOS."""
        print(f"[OSAdapter:ThothOS] Executing symbolic command: {command}")
        return {
            "status": "executed",
            "native": True,
            "command": command,
            "context": context or {}
        }
    
    def _thoth_memory_sync(self, tree_path: str = None) -> bool:
        """Sync memory tree with ThothOS native memory subsystem."""
        print(f"[OSAdapter:ThothOS] Syncing memory tree: {tree_path or 'full'}")
        return True
    
    def _thoth_realm_bridge(self, realm_id: str, action: str) -> Dict:
        """Bridge to ThothOS realm system."""
        print(f"[OSAdapter:ThothOS] Realm bridge: {realm_id} -> {action}")
        return {"realm": realm_id, "action": action, "status": "bridged"}
    
    def _thoth_notify(self, message: str, level: str = "info") -> bool:
        """Send notification through ThothOS notification system."""
        print(f"[OSAdapter:ThothOS] Notification [{level}]: {message}")
        return True
    
    def _thoth_persist(self, data: Dict, namespace: str = "daemon") -> bool:
        """Persist state to ThothOS native storage."""
        print(f"[OSAdapter:ThothOS] Persisting to namespace: {namespace}")
        return True
    
    # ==================== LINUX HANDLERS ====================
    
    def _linux_symbolic_fallback(self, command: str, context: Dict = None) -> Dict:
        """Emulate symbolic command on Linux."""
        print(f"[OSAdapter:Linux] Emulating symbolic command: {command}")
        return {
            "status": "emulated",
            "native": False,
            "command": command,
            "note": "Running in compatibility mode. Install ThothOS for native execution."
        }
    
    def _linux_memory_sync(self, tree_path: str = None) -> bool:
        """Sync memory using Linux filesystem."""
        print(f"[OSAdapter:Linux] Memory sync via filesystem: {tree_path or 'full'}")
        return True
    
    def _linux_notify(self, message: str, level: str = "info") -> bool:
        """Send notification on Linux (notify-send)."""
        try:
            import subprocess
            subprocess.run(["notify-send", f"Daemon [{level}]", message], check=False)
            return True
        except Exception:
            print(f"[OSAdapter:Linux] Fallback notification: {message}")
            return True
    
    # ==================== MACOS HANDLERS ====================
    
    def _macos_symbolic_fallback(self, command: str, context: Dict = None) -> Dict:
        """Emulate symbolic command on macOS."""
        print(f"[OSAdapter:macOS] Emulating symbolic command: {command}")
        return {
            "status": "emulated",
            "native": False,
            "command": command
        }
    
    def _macos_memory_sync(self, tree_path: str = None) -> bool:
        """Sync memory using macOS filesystem."""
        print(f"[OSAdapter:macOS] Memory sync via filesystem: {tree_path or 'full'}")
        return True
    
    def _macos_notify(self, message: str, level: str = "info") -> bool:
        """Send notification on macOS (osascript)."""
        try:
            import subprocess
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "Daemon [{level}]"'
            ], check=False)
            return True
        except Exception:
            print(f"[OSAdapter:macOS] Fallback notification: {message}")
            return True
    
    # ==================== WINDOWS HANDLERS ====================
    
    def _windows_symbolic_fallback(self, command: str, context: Dict = None) -> Dict:
        """Emulate symbolic command on Windows."""
        print(f"[OSAdapter:Windows] Emulating symbolic command: {command}")
        return {
            "status": "emulated",
            "native": False,
            "command": command,
            "note": "Limited symbolic execution on Windows. Consider WSL2 with ThothOS."
        }
    
    def _windows_memory_sync(self, tree_path: str = None) -> bool:
        """Sync memory using Windows filesystem."""
        print(f"[OSAdapter:Windows] Memory sync via filesystem: {tree_path or 'full'}")
        return True
    
    def _windows_notify(self, message: str, level: str = "info") -> bool:
        """Send notification on Windows (toast)."""
        try:
            from ctypes import windll
            windll.user32.MessageBoxW(0, message, f"Daemon [{level}]", 0x40)
            return True
        except Exception:
            print(f"[OSAdapter:Windows] Fallback notification: {message}")
            return True
    
    # ==================== GENERIC/FALLBACK HANDLERS ====================
    
    def _noop_handler(self, *args, **kwargs) -> None:
        """No-operation handler for unsupported features."""
        return None
    
    def _generic_notify(self, message: str, level: str = "info") -> bool:
        """Generic notification fallback."""
        print(f"[OSAdapter:Generic] Notification [{level}]: {message}")
        return True
    
    def _generic_persist(self, data: Dict, namespace: str = "daemon") -> bool:
        """Generic state persistence using JSON files."""
        try:
            persist_path = f"config/{namespace}_state.json"
            os.makedirs(os.path.dirname(persist_path), exist_ok=True)
            with open(persist_path, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[OSAdapter] Persist error: {e}")
            return False


# Singleton instance for global access
_os_adapter_instance: Optional[OSAdapter] = None


def get_os_adapter() -> OSAdapter:
    """Get or create the global OSAdapter instance."""
    global _os_adapter_instance
    if _os_adapter_instance is None:
        _os_adapter_instance = OSAdapter()
    return _os_adapter_instance
