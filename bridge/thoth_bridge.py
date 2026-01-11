# bridge/thoth_bridge.py
"""
ThothBridge - Connection layer between Daemon and ThothOS

This bridge enables the daemon to:
- Register and invoke native ThothOS applications
- Send commands to the OS layer
- Receive system status and events
- Coordinate with other ThothOS services
"""

from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
import queue
import json


class AppState(Enum):
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    SUSPENDED = "suspended"
    ERROR = "error"


@dataclass
class ThothApp:
    """Represents a registered ThothOS application."""
    name: str
    handler: Callable
    state: AppState = AppState.REGISTERED
    permissions: List[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    invocation_count: int = 0
    last_invoked: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ThothBridge:
    """
    Bridge between the Prometheus daemon and ThothOS native layer.
    
    Features:
    - App registration and lifecycle management
    - Command protocol for OS-level operations
    - Event streaming from ThothOS
    - Resource coordination
    - Inter-app communication
    """
    
    module_name = "thoth_bridge"
    dependencies = []
    
    def __init__(self):
        self._kernel = None
        self.registered_apps: Dict[str, ThothApp] = {}
        self._command_queue: queue.Queue = queue.Queue()
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()
        
        # System status cache
        self._system_status = {
            "status": "active",
            "uptime": "0m",
            "modules": [],
            "last_updated": None
        }
        
        # Connection state
        self._connected = False
        self._connection_thread: Optional[threading.Thread] = None
        
        print("[ThothBridge] Connecting daemon to native ThothOS layer.")
    
    def initialize(self, kernel) -> bool:
        """Initialize with kernel reference."""
        self._kernel = kernel
        
        # Subscribe to kernel events
        if kernel:
            kernel.subscribe("app.request", self._handle_app_request)
            kernel.subscribe("system.command", self._handle_system_command)
        
        self._connected = True
        print("[ThothBridge] Initialized and connected to kernel.")
        return True
    
    def start(self) -> bool:
        """Start the bridge services."""
        # Start command processing
        self._connection_thread = threading.Thread(
            target=self._process_commands,
            daemon=True
        )
        self._connection_thread.start()
        return True
    
    def stop(self) -> bool:
        """Stop the bridge."""
        self._connected = False
        return True
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "status": "healthy" if self._connected else "disconnected",
            "registered_apps": len(self.registered_apps),
            "command_queue_size": self._command_queue.qsize()
        }
    
    # =========== App Management ===========
    
    def register_app(
        self,
        app_name: str,
        handler: Callable,
        permissions: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Register a ThothOS application.
        
        Args:
            app_name: Unique application identifier
            handler: Callable to invoke when app is called
            permissions: Required permissions for this app
            metadata: Additional app configuration
            
        Returns:
            True if registration successful
        """
        with self._lock:
            if app_name in self.registered_apps:
                print(f"[ThothBridge] Warning: Replacing existing app '{app_name}'")
            
            app = ThothApp(
                name=app_name,
                handler=handler,
                permissions=permissions or [],
                metadata=metadata or {}
            )
            self.registered_apps[app_name] = app
            
        print(f"[ThothBridge] App registered: {app_name}")
        
        # Notify kernel
        if self._kernel:
            self._kernel.publish(
                "thoth.app.registered",
                {"app_name": app_name, "permissions": permissions or []},
                "thoth_bridge"
            )
        
        return True
    
    def unregister_app(self, app_name: str) -> bool:
        """Remove an app registration."""
        with self._lock:
            if app_name in self.registered_apps:
                del self.registered_apps[app_name]
                print(f"[ThothBridge] App unregistered: {app_name}")
                return True
            return False
    
    def invoke_app(
        self,
        app_name: str,
        payload: Any = None,
        async_mode: bool = False
    ) -> Any:
        """
        Invoke a registered application.
        
        Args:
            app_name: Name of app to invoke
            payload: Data to pass to the app
            async_mode: If True, return immediately (task ID)
            
        Returns:
            App result or task ID if async
        """
        with self._lock:
            app = self.registered_apps.get(app_name)
        
        if not app:
            print(f"[ThothBridge] App '{app_name}' not found.")
            return {"error": f"App not found: {app_name}"}
        
        print(f"[ThothBridge] Invoking app: {app_name}")
        
        def execute():
            try:
                app.state = AppState.RUNNING
                app.invocation_count += 1
                app.last_invoked = datetime.utcnow()
                
                result = app.handler(payload)
                
                app.state = AppState.READY
                return result
                
            except Exception as e:
                app.state = AppState.ERROR
                print(f"[ThothBridge] App '{app_name}' error: {e}")
                return {"error": str(e)}
        
        if async_mode and self._kernel:
            # Schedule async execution
            task_id = self._kernel.schedule_task(
                execute,
                name=f"app.{app_name}",
                source_module="thoth_bridge"
            )
            return {"task_id": task_id, "status": "scheduled"}
        else:
            return execute()
    
    def get_app_info(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered app."""
        with self._lock:
            app = self.registered_apps.get(app_name)
            if not app:
                return None
            
            return {
                "name": app.name,
                "state": app.state.value,
                "permissions": app.permissions,
                "invocation_count": app.invocation_count,
                "last_invoked": app.last_invoked.isoformat() if app.last_invoked else None,
                "metadata": app.metadata
            }
    
    def list_apps(self) -> List[Dict[str, Any]]:
        """List all registered apps."""
        with self._lock:
            return [
                self.get_app_info(name)
                for name in self.registered_apps.keys()
            ]
    
    # =========== Command Protocol ===========
    
    def send_command(
        self,
        command: str,
        metadata: Dict[str, Any] = None,
        priority: int = 1
    ) -> str:
        """
        Send a command to ThothOS.
        
        Args:
            command: Command string
            metadata: Additional command data
            priority: Command priority (0=highest)
            
        Returns:
            Command ID for tracking
        """
        import uuid
        command_id = str(uuid.uuid4())
        
        command_packet = {
            "id": command_id,
            "command": command,
            "metadata": metadata or {},
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"[ThothBridge] Command sent: {command}")
        print(f"  Metadata: {metadata}")
        
        self._command_queue.put((priority, command_packet))
        
        # Notify kernel
        if self._kernel:
            self._kernel.publish(
                "thoth.command.sent",
                command_packet,
                "thoth_bridge"
            )
        
        return command_id
    
    def _process_commands(self):
        """Process queued commands."""
        while self._connected:
            try:
                priority, command = self._command_queue.get(timeout=1.0)
                self._execute_command(command)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ThothBridge] Command processing error: {e}")
    
    def _execute_command(self, command: Dict[str, Any]):
        """Execute a ThothOS command."""
        cmd = command.get("command", "")
        metadata = command.get("metadata", {})
        
        # Built-in command handlers
        if cmd == "status":
            self._update_status()
        elif cmd == "reload":
            self._reload_apps()
        elif cmd == "broadcast":
            self._broadcast_event(metadata.get("event"), metadata.get("data"))
        else:
            # Forward to kernel for handling
            if self._kernel:
                self._kernel.publish(
                    f"thoth.command.{cmd}",
                    metadata,
                    "thoth_bridge"
                )
    
    # =========== Status & Events ===========
    
    def receive_status(self) -> Dict[str, Any]:
        """Get current ThothOS status."""
        self._update_status()
        return self._system_status
    
    def _update_status(self):
        """Update cached system status."""
        with self._lock:
            self._system_status = {
                "status": "active" if self._connected else "disconnected",
                "uptime": self._calculate_uptime(),
                "modules": list(self.registered_apps.keys()),
                "app_count": len(self.registered_apps),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Add kernel info if available
            if self._kernel:
                kernel_status = self._kernel.get_status()
                self._system_status["kernel_state"] = kernel_status.get("state")
                self._system_status["kernel_uptime"] = kernel_status.get("uptime_seconds")
    
    def _calculate_uptime(self) -> str:
        """Calculate uptime string."""
        if not self._kernel or not self._kernel.boot_time:
            return "0m"
        
        delta = datetime.utcnow() - self._kernel.boot_time
        minutes = int(delta.total_seconds() / 60)
        hours = minutes // 60
        
        if hours > 0:
            return f"{hours}h {minutes % 60}m"
        return f"{minutes}m"
    
    def on_event(self, event_type: str, handler: Callable):
        """Register a handler for ThothOS events."""
        with self._lock:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(handler)
    
    def _broadcast_event(self, event_type: str, data: Any):
        """Broadcast an event to registered handlers."""
        with self._lock:
            handlers = self._event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"[ThothBridge] Event handler error: {e}")
        
        # Also publish to kernel
        if self._kernel:
            self._kernel.publish(f"thoth.event.{event_type}", data, "thoth_bridge")
    
    def _reload_apps(self):
        """Reload all registered apps."""
        print("[ThothBridge] Reloading apps...")
        with self._lock:
            for app_name, app in self.registered_apps.items():
                app.state = AppState.INITIALIZING
                try:
                    # Re-initialize app if it has an init method
                    if hasattr(app.handler, 'initialize'):
                        app.handler.initialize()
                    app.state = AppState.READY
                except Exception as e:
                    app.state = AppState.ERROR
                    print(f"[ThothBridge] Failed to reload '{app_name}': {e}")
    
    # =========== Event Handlers ===========
    
    def _handle_app_request(self, message):
        """Handle app invocation request from kernel."""
        app_name = message.payload.get("app_name")
        payload = message.payload.get("payload")
        
        result = self.invoke_app(app_name, payload)
        
        # Respond via message bus
        if self._kernel and message.correlation_id:
            self._kernel.message_bus.respond(message.correlation_id, result)
    
    def _handle_system_command(self, message):
        """Handle system command from kernel."""
        command = message.payload.get("command")
        metadata = message.payload.get("metadata", {})
        
        self.send_command(command, metadata)
    
    # =========== Reflection ===========
    
    def reflect(self) -> Dict[str, Any]:
        """Provide reflection data for system analysis."""
        return {
            "connected": self._connected,
            "app_count": len(self.registered_apps),
            "apps": [
                {
                    "name": app.name,
                    "state": app.state.value,
                    "invocations": app.invocation_count
                }
                for app in self.registered_apps.values()
            ],
            "command_queue_depth": self._command_queue.qsize()
        }
