# devices/adapters/base_adapter.py
"""
Base Protocol Adapter
=====================
Abstract base class for all protocol adapters.
Defines the interface that all adapters must implement.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional, Callable, Dict, Any
import threading


class AdapterState(Enum):
    """Adapter operational states."""
    UNINITIALIZED = auto()
    INITIALIZING = auto()
    READY = auto()
    SCANNING = auto()
    CONNECTING = auto()
    ERROR = auto()
    DISABLED = auto()


class BaseProtocolAdapter(ABC):
    """
    Abstract base class for protocol adapters.
    All protocol-specific adapters must inherit from this.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.state = AdapterState.UNINITIALIZED
        self._lock = threading.Lock()
        self._scan_thread: Optional[threading.Thread] = None
        self._scan_callback: Optional[Callable] = None
        self._error_callback: Optional[Callable] = None
        self._is_available = False
        
    @property
    def is_available(self) -> bool:
        """Check if the adapter's hardware/drivers are available."""
        return self._is_available
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the adapter and check hardware availability.
        Returns True if successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def start_discovery(self, callback: Callable, duration: float = 10.0) -> bool:
        """
        Start device discovery.
        
        Args:
            callback: Function to call when devices are discovered.
                     Signature: callback(device: Device)
            duration: How long to scan in seconds (0 for continuous)
            
        Returns:
            True if discovery started successfully.
        """
        pass
    
    @abstractmethod
    def stop_discovery(self):
        """Stop ongoing device discovery."""
        pass
    
    @abstractmethod
    def connect(self, device_id: str) -> bool:
        """
        Connect to a specific device.
        
        Args:
            device_id: The unique identifier of the device.
            
        Returns:
            True if connection successful.
        """
        pass
    
    @abstractmethod
    def disconnect(self, device_id: str) -> bool:
        """
        Disconnect from a device.
        
        Args:
            device_id: The unique identifier of the device.
            
        Returns:
            True if disconnection successful.
        """
        pass
    
    @abstractmethod
    def send_data(self, device_id: str, data: bytes) -> bool:
        """
        Send data to a connected device.
        
        Args:
            device_id: The device to send to.
            data: The data to send.
            
        Returns:
            True if data was sent successfully.
        """
        pass
    
    @abstractmethod
    def receive_data(self, device_id: str, timeout: float = 5.0) -> Optional[bytes]:
        """
        Receive data from a connected device.
        
        Args:
            device_id: The device to receive from.
            timeout: How long to wait for data.
            
        Returns:
            The received data, or None if timeout/error.
        """
        pass
    
    @abstractmethod
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a device.
        
        Args:
            device_id: The device to query.
            
        Returns:
            Dictionary of device information.
        """
        pass
    
    def set_error_callback(self, callback: Callable):
        """Set callback for error notifications."""
        self._error_callback = callback
    
    def _report_error(self, error: str):
        """Report an error through the callback."""
        print(f"[{self.name}] Error: {error}")
        if self._error_callback:
            self._error_callback(self.name, error)
    
    def shutdown(self):
        """Cleanup and shutdown the adapter."""
        self.stop_discovery()
        self.state = AdapterState.DISABLED
        print(f"[{self.name}] Shutdown complete.")
    
    def get_status(self) -> dict:
        """Get adapter status summary."""
        return {
            'name': self.name,
            'state': self.state.name,
            'available': self._is_available
        }
