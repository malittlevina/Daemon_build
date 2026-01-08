# daemon/os_adapter.py
"""
OS Adapter Layer

Provides OS-specific implementations and abstractions that allow the daemon
to run uniformly across different operating systems while leveraging
native capabilities when available (especially on ThothOS).
"""

import os
import sys
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from daemon.platform_detector import (
    get_platform_detector,
    OSType,
    CapabilityLevel,
    OSProfile,
)


class BaseOSAdapter(ABC):
    """
    Abstract base class for OS-specific adapters.
    Each OS implements this interface to provide platform-specific functionality.
    """
    
    def __init__(self, profile: OSProfile):
        self.profile = profile
        self._initialized = False
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the adapter for the current OS."""
        pass
    
    @abstractmethod
    def get_config_path(self) -> Path:
        """Get the OS-appropriate configuration directory."""
        pass
    
    @abstractmethod
    def get_data_path(self) -> Path:
        """Get the OS-appropriate data directory."""
        pass
    
    @abstractmethod
    def get_log_path(self) -> Path:
        """Get the OS-appropriate log directory."""
        pass
    
    @abstractmethod
    def get_cache_path(self) -> Path:
        """Get the OS-appropriate cache directory."""
        pass
    
    @abstractmethod
    def register_daemon_service(self) -> bool:
        """Register the daemon as a system service."""
        pass
    
    @abstractmethod
    def get_process_priority(self) -> str:
        """Get the recommended process priority for this OS."""
        pass
    
    @abstractmethod
    def setup_ipc_channel(self) -> Any:
        """Set up inter-process communication for this OS."""
        pass
    
    def get_path_separator(self) -> str:
        """Get the path separator for this OS."""
        return os.sep
    
    def normalize_path(self, path: str) -> str:
        """Normalize a path for this OS."""
        return str(Path(path).resolve())
    
    def is_admin(self) -> bool:
        """Check if running with elevated privileges."""
        try:
            return os.geteuid() == 0
        except AttributeError:
            # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0


class ThothOSAdapter(BaseOSAdapter):
    """
    Native ThothOS adapter with full symbolic integration.
    This is the preferred and optimized path.
    """
    
    def initialize(self) -> bool:
        print("[ThothOS Adapter] Initializing native symbolic integration...")
        self._initialized = True
        # Native ThothOS gets full kernel access
        self._connect_symbolic_kernel()
        return True
    
    def _connect_symbolic_kernel(self) -> None:
        """Connect to the ThothOS symbolic kernel."""
        kernel_socket = "/run/thothos/kernel.sock"
        if os.path.exists(kernel_socket):
            print("[ThothOS Adapter] Connected to symbolic kernel")
        else:
            print("[ThothOS Adapter] Kernel socket not found, using userspace mode")
    
    def get_config_path(self) -> Path:
        return Path("/etc/thothos/daemon")
    
    def get_data_path(self) -> Path:
        return Path("/var/lib/thothos/daemon")
    
    def get_log_path(self) -> Path:
        return Path("/var/log/thothos")
    
    def get_cache_path(self) -> Path:
        return Path("/var/cache/thothos")
    
    def register_daemon_service(self) -> bool:
        """Register as a native ThothOS service with full integration."""
        print("[ThothOS Adapter] Registering native daemon service...")
        # ThothOS has native daemon management
        return True
    
    def get_process_priority(self) -> str:
        """ThothOS daemons run with elevated priority."""
        return "realtime"
    
    def setup_ipc_channel(self) -> Any:
        """Set up native symbolic IPC."""
        return {"type": "symbolic_ipc", "socket": "/run/thothos/daemon.sock"}
    
    def invoke_kernel_ritual(self, ritual_name: str, params: Dict) -> Any:
        """Invoke a kernel-level ritual (ThothOS exclusive)."""
        print(f"[ThothOS Adapter] Invoking kernel ritual: {ritual_name}")
        return {"status": "invoked", "ritual": ritual_name}
    
    def access_symbolic_memory(self, address: str) -> Any:
        """Direct access to symbolic memory (ThothOS exclusive)."""
        print(f"[ThothOS Adapter] Accessing symbolic memory: {address}")
        return {"address": address, "access": "granted"}


class LinuxAdapter(BaseOSAdapter):
    """
    Linux adapter with strong compatibility.
    Supports most features with near-native performance.
    """
    
    def initialize(self) -> bool:
        print("[Linux Adapter] Initializing Linux compatibility layer...")
        self._initialized = True
        return True
    
    def get_config_path(self) -> Path:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        return Path(xdg_config) / "prometheus-daemon"
    
    def get_data_path(self) -> Path:
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        return Path(xdg_data) / "prometheus-daemon"
    
    def get_log_path(self) -> Path:
        return Path(os.path.expanduser("~/.local/share/prometheus-daemon/logs"))
    
    def get_cache_path(self) -> Path:
        xdg_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
        return Path(xdg_cache) / "prometheus-daemon"
    
    def register_daemon_service(self) -> bool:
        """Register as a systemd service."""
        print("[Linux Adapter] Registering systemd service...")
        service_path = Path.home() / ".config/systemd/user/prometheus-daemon.service"
        # Service registration logic would go here
        return True
    
    def get_process_priority(self) -> str:
        return "high"
    
    def setup_ipc_channel(self) -> Any:
        """Set up Unix domain socket IPC."""
        socket_path = self.get_data_path() / "daemon.sock"
        return {"type": "unix_socket", "socket": str(socket_path)}


class MacOSAdapter(BaseOSAdapter):
    """
    macOS adapter with Darwin-specific optimizations.
    """
    
    def initialize(self) -> bool:
        print("[macOS Adapter] Initializing macOS compatibility layer...")
        self._initialized = True
        return True
    
    def get_config_path(self) -> Path:
        return Path.home() / "Library/Application Support/Prometheus Daemon"
    
    def get_data_path(self) -> Path:
        return Path.home() / "Library/Application Support/Prometheus Daemon/Data"
    
    def get_log_path(self) -> Path:
        return Path.home() / "Library/Logs/Prometheus Daemon"
    
    def get_cache_path(self) -> Path:
        return Path.home() / "Library/Caches/Prometheus Daemon"
    
    def register_daemon_service(self) -> bool:
        """Register as a launchd service."""
        print("[macOS Adapter] Registering launchd service...")
        plist_path = Path.home() / "Library/LaunchAgents/com.prometheus.daemon.plist"
        # Launchd registration logic would go here
        return True
    
    def get_process_priority(self) -> str:
        return "normal"
    
    def setup_ipc_channel(self) -> Any:
        """Set up Unix domain socket IPC."""
        socket_path = self.get_data_path() / "daemon.sock"
        return {"type": "unix_socket", "socket": str(socket_path)}


class WindowsAdapter(BaseOSAdapter):
    """
    Windows adapter with compatibility layer.
    Provides functional but limited feature set.
    """
    
    def initialize(self) -> bool:
        print("[Windows Adapter] Initializing Windows compatibility layer...")
        self._initialized = True
        return True
    
    def get_config_path(self) -> Path:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(appdata) / "Prometheus Daemon"
    
    def get_data_path(self) -> Path:
        localappdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(localappdata) / "Prometheus Daemon/Data"
    
    def get_log_path(self) -> Path:
        localappdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(localappdata) / "Prometheus Daemon/Logs"
    
    def get_cache_path(self) -> Path:
        localappdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        return Path(localappdata) / "Prometheus Daemon/Cache"
    
    def register_daemon_service(self) -> bool:
        """Register as a Windows service."""
        print("[Windows Adapter] Registering Windows service...")
        # Windows service registration logic would go here
        return True
    
    def get_process_priority(self) -> str:
        return "normal"
    
    def setup_ipc_channel(self) -> Any:
        """Set up named pipe IPC for Windows."""
        pipe_name = r"\\.\pipe\prometheus-daemon"
        return {"type": "named_pipe", "pipe": pipe_name}
    
    def get_path_separator(self) -> str:
        return "\\"


class FallbackAdapter(BaseOSAdapter):
    """
    Generic fallback adapter for unknown or unsupported systems.
    Provides minimal but functional operation.
    """
    
    def initialize(self) -> bool:
        print("[Fallback Adapter] Initializing generic compatibility layer...")
        print("[Fallback Adapter] WARNING: Running in fallback mode with limited features")
        self._initialized = True
        return True
    
    def get_config_path(self) -> Path:
        return Path.home() / ".prometheus-daemon"
    
    def get_data_path(self) -> Path:
        return Path.home() / ".prometheus-daemon/data"
    
    def get_log_path(self) -> Path:
        return Path.home() / ".prometheus-daemon/logs"
    
    def get_cache_path(self) -> Path:
        return Path.home() / ".prometheus-daemon/cache"
    
    def register_daemon_service(self) -> bool:
        print("[Fallback Adapter] Service registration not available on this platform")
        return False
    
    def get_process_priority(self) -> str:
        return "normal"
    
    def setup_ipc_channel(self) -> Any:
        """Set up file-based IPC as fallback."""
        ipc_file = self.get_data_path() / "ipc_queue"
        return {"type": "file_ipc", "path": str(ipc_file)}


class OSAdapterFactory:
    """
    Factory for creating the appropriate OS adapter based on detected platform.
    """
    
    _adapters = {
        OSType.THOTHOS: ThothOSAdapter,
        OSType.LINUX: LinuxAdapter,
        OSType.MACOS: MacOSAdapter,
        OSType.WINDOWS: WindowsAdapter,
        OSType.BSD: LinuxAdapter,  # BSD uses Linux-compatible adapter
        OSType.UNKNOWN: FallbackAdapter,
    }
    
    @classmethod
    def create(cls, profile: Optional[OSProfile] = None) -> BaseOSAdapter:
        """
        Create the appropriate adapter for the current or specified platform.
        """
        if profile is None:
            profile = get_platform_detector().detect()
        
        adapter_class = cls._adapters.get(profile.os_type, FallbackAdapter)
        adapter = adapter_class(profile)
        
        # Initialize the adapter
        adapter.initialize()
        
        # Ensure directories exist
        cls._ensure_directories(adapter)
        
        return adapter
    
    @classmethod
    def _ensure_directories(cls, adapter: BaseOSAdapter) -> None:
        """Ensure all required directories exist."""
        directories = [
            adapter.get_config_path(),
            adapter.get_data_path(),
            adapter.get_log_path(),
            adapter.get_cache_path(),
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                print(f"[OS Adapter] Warning: Cannot create directory {directory}")
            except Exception as e:
                print(f"[OS Adapter] Warning: Error creating directory {directory}: {e}")


# Global adapter instance
_adapter: Optional[BaseOSAdapter] = None


def get_os_adapter() -> BaseOSAdapter:
    """Get or create the global OS adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = OSAdapterFactory.create()
    return _adapter


def is_thothos_native() -> bool:
    """Check if running on native ThothOS with full capabilities."""
    return isinstance(get_os_adapter(), ThothOSAdapter)


def get_capability_multiplier() -> float:
    """
    Get a multiplier for feature scaling based on OS capability.
    ThothOS = 1.0, Linux = 0.85, macOS = 0.75, Windows = 0.6, Unknown = 0.3
    """
    adapter = get_os_adapter()
    profile = adapter.profile
    return profile.priority_score / 100.0
