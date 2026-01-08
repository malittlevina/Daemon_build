# bridge/thoth_bridge.py
"""
ThothBridge - OS-Aware Communication Bridge

This module provides the communication layer between the daemon and ThothOS.
It operates in two modes:
1. NATIVE MODE: Full ThothOS integration with native IPC and symbolic commands
2. COMPATIBILITY MODE: Emulated functionality for non-ThothOS environments

The bridge always prefers ThothOS but gracefully degrades on other OSes.
"""

from typing import Dict, Any, Callable, Optional, List
from enum import Enum
import json
import os


class BridgeMode(Enum):
    """Operating mode for the ThothBridge."""
    NATIVE = "native"           # Running on ThothOS - full capabilities
    EMULATED = "emulated"       # Running on other OS - emulated features
    DISCONNECTED = "disconnected"  # No OS adapter available


class ThothBridge:
    """
    The ThothBridge connects the daemon to ThothOS native applications and services.
    
    When running on ThothOS:
    - Uses native IPC for app communication
    - Accesses symbolic command execution
    - Syncs with ThothOS system services
    
    When running on other OSes:
    - Emulates ThothOS app behavior locally
    - Provides compatibility shims
    - Queues commands for when ThothOS becomes available
    """
    
    def __init__(self, os_adapter=None):
        self.registered_apps: Dict[str, Callable] = {}
        self.emulated_apps: Dict[str, Dict] = {}
        self._os_adapter = os_adapter
        self._mode: BridgeMode = BridgeMode.DISCONNECTED
        self._command_queue: List[Dict] = []
        self._native_socket = None
        
        # Initialize based on OS adapter
        self._init_bridge()
    
    def _init_bridge(self):
        """Initialize bridge based on available OS context."""
        if self._os_adapter and self._os_adapter.is_native:
            self._mode = BridgeMode.NATIVE
            self._connect_native()
            print("[ThothBridge] 🌟 Connected to ThothOS in NATIVE mode")
        elif self._os_adapter:
            self._mode = BridgeMode.EMULATED
            self._init_emulation()
            print(f"[ThothBridge] Running in EMULATED mode on {self._os_adapter.os_type.value}")
            print("[ThothBridge] Tip: Install ThothOS for native app integration")
        else:
            self._mode = BridgeMode.EMULATED
            self._init_emulation()
            print("[ThothBridge] Running in EMULATED mode (no OS adapter)")
    
    def _connect_native(self):
        """Connect to ThothOS native IPC."""
        try:
            # ThothOS uses a Unix socket for daemon IPC
            socket_path = os.environ.get("THOTHOS_DAEMON_SOCKET", "/var/run/thothos/daemon.sock")
            if os.path.exists(socket_path):
                print(f"[ThothBridge] Native socket found: {socket_path}")
                # In production, would establish socket connection here
                self._native_socket = socket_path
        except Exception as e:
            print(f"[ThothBridge] Native connection warning: {e}")
            self._mode = BridgeMode.EMULATED
    
    def _init_emulation(self):
        """Initialize emulated app environment."""
        # Pre-register core ThothOS apps for emulation
        self.emulated_apps = {
            "system": {
                "name": "System Manager",
                "emulated": True,
                "handlers": {}
            },
            "memory": {
                "name": "Memory Tree",
                "emulated": True,
                "handlers": {}
            },
            "scrolls": {
                "name": "Scroll Engine",
                "emulated": True,
                "handlers": {}
            },
            "codex": {
                "name": "Codex Knowledge Base",
                "emulated": True,
                "handlers": {}
            }
        }
    
    def set_os_adapter(self, os_adapter):
        """Set or update the OS adapter and reinitialize."""
        self._os_adapter = os_adapter
        self._init_bridge()
    
    @property
    def mode(self) -> BridgeMode:
        """Get current bridge operating mode."""
        return self._mode
    
    @property
    def is_native(self) -> bool:
        """Check if running in native ThothOS mode."""
        return self._mode == BridgeMode.NATIVE
    
    def register_app(self, app_name: str, handler: Callable, metadata: Dict = None):
        """
        Register an application with the bridge.
        
        In native mode: Registers with ThothOS app registry
        In emulated mode: Stores handler locally
        """
        self.registered_apps[app_name] = handler
        
        if self._mode == BridgeMode.NATIVE:
            self._register_native_app(app_name, metadata)
        else:
            # Store in emulated registry
            self.emulated_apps[app_name] = {
                "name": app_name,
                "emulated": True,
                "handlers": {"default": handler},
                "metadata": metadata or {}
            }
        
        print(f"[ThothBridge] App registered: {app_name} (mode: {self._mode.value})")
    
    def _register_native_app(self, app_name: str, metadata: Dict = None):
        """Register app with ThothOS native registry."""
        if self._native_socket:
            # Would send registration message to ThothOS
            print(f"[ThothBridge] Native registration: {app_name}")
    
    def invoke_app(self, app_name: str, payload: Any = None) -> Optional[Any]:
        """
        Invoke a registered application.
        
        Returns the result of the app handler, or None if app not found.
        """
        if self._mode == BridgeMode.NATIVE:
            return self._invoke_native_app(app_name, payload)
        else:
            return self._invoke_emulated_app(app_name, payload)
    
    def _invoke_native_app(self, app_name: str, payload: Any) -> Optional[Any]:
        """Invoke app through ThothOS native IPC."""
        if app_name in self.registered_apps:
            print(f"[ThothBridge] Native invoke: {app_name}")
            try:
                return self.registered_apps[app_name](payload)
            except Exception as e:
                print(f"[ThothBridge] Native invoke error: {e}")
                return None
        else:
            # Try ThothOS system apps
            print(f"[ThothBridge] Requesting ThothOS system app: {app_name}")
            # Would send IPC message to ThothOS
            return {"status": "requested", "app": app_name}
    
    def _invoke_emulated_app(self, app_name: str, payload: Any) -> Optional[Any]:
        """Invoke app in emulated mode."""
        if app_name in self.registered_apps:
            print(f"[ThothBridge] Emulated invoke: {app_name}")
            try:
                return self.registered_apps[app_name](payload)
            except Exception as e:
                print(f"[ThothBridge] Emulated invoke error: {e}")
                return None
        elif app_name in self.emulated_apps:
            print(f"[ThothBridge] Invoking emulated system app: {app_name}")
            return {"status": "emulated", "app": app_name, "payload": payload}
        else:
            print(f"[ThothBridge] App '{app_name}' not found.")
            return None

    def send_command(self, command: str, metadata: Dict = None) -> Dict:
        """
        Send a command to ThothOS.
        
        In native mode: Executes immediately via IPC
        In emulated mode: Queues command and returns emulated response
        """
        metadata = metadata or {}
        
        if self._mode == BridgeMode.NATIVE:
            return self._send_native_command(command, metadata)
        else:
            return self._send_emulated_command(command, metadata)
    
    def _send_native_command(self, command: str, metadata: Dict) -> Dict:
        """Send command via ThothOS native IPC."""
        print(f"[ThothBridge] Native command: {command}")
        print(f"  Metadata: {metadata}")
        
        # Would send via socket in production
        return {
            "status": "executed",
            "native": True,
            "command": command,
            "metadata": metadata
        }
    
    def _send_emulated_command(self, command: str, metadata: Dict) -> Dict:
        """Emulate command execution and queue for ThothOS sync."""
        print(f"[ThothBridge] Emulated command: {command}")
        print(f"  Metadata: {metadata}")
        
        # Queue for potential future ThothOS sync
        self._command_queue.append({
            "command": command,
            "metadata": metadata,
            "status": "queued"
        })
        
        return {
            "status": "emulated",
            "native": False,
            "command": command,
            "metadata": metadata,
            "note": "Command queued for ThothOS sync when available"
        }

    def receive_status(self) -> Dict:
        """
        Receive current ThothOS status.
        
        In native mode: Gets real status from ThothOS
        In emulated mode: Returns simulated status
        """
        base_status = {
            "mode": self._mode.value,
            "is_native": self.is_native,
            "registered_apps": list(self.registered_apps.keys()),
            "queued_commands": len(self._command_queue)
        }
        
        if self._mode == BridgeMode.NATIVE:
            # Would query ThothOS for real status
            base_status.update({
                "status": "active",
                "uptime": self._get_uptime(),
                "modules": ["daemon", "codex", "scroll_engine", "memory_tree"],
                "os": "thothos",
                "native_socket": self._native_socket
            })
        else:
            base_status.update({
                "status": "emulated",
                "uptime": self._get_uptime(),
                "modules": ["daemon", "codex", "scroll_engine"],
                "os": self._os_adapter.os_type.value if self._os_adapter else "unknown",
                "emulated_apps": list(self.emulated_apps.keys())
            })
        
        return base_status
    
    def _get_uptime(self) -> str:
        """Get daemon uptime (placeholder)."""
        return "active"
    
    def sync_to_thothos(self) -> Dict:
        """
        Sync queued commands when ThothOS becomes available.
        
        This is called when the OS adapter detects ThothOS connection.
        """
        if not self._command_queue:
            return {"synced": 0, "status": "empty"}
        
        if self._mode == BridgeMode.NATIVE:
            synced = 0
            for cmd in self._command_queue:
                result = self._send_native_command(cmd["command"], cmd["metadata"])
                if result.get("status") == "executed":
                    synced += 1
            
            self._command_queue.clear()
            return {"synced": synced, "status": "complete"}
        else:
            return {
                "synced": 0,
                "status": "pending",
                "queued": len(self._command_queue),
                "note": "ThothOS not available - commands remain queued"
            }
    
    def get_preference_info(self) -> Dict:
        """Get information about ThothOS preference status."""
        info = {
            "prefers_thothos": True,
            "current_mode": self._mode.value,
            "is_native": self.is_native,
            "queued_for_sync": len(self._command_queue)
        }
        
        if self._os_adapter:
            info["os_type"] = self._os_adapter.os_type.value
            info["preference_score"] = self._os_adapter.preference_score
            info["upgrade_suggestion"] = self._os_adapter.suggest_upgrade()
        
        return info
    
    def on_thothos_detected(self):
        """Called when ThothOS becomes available (e.g., via virtualization or mount)."""
        print("[ThothBridge] ThothOS detected! Upgrading to native mode...")
        self._mode = BridgeMode.NATIVE
        self._connect_native()
        self.sync_to_thothos()
