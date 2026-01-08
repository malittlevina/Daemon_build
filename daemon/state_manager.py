# daemon/state_manager.py
"""
State Manager with OS Awareness

Manages daemon state with cross-platform support while prioritizing
ThothOS native capabilities when available.
"""

import json
import os
import time
from typing import Any, Dict, Optional
from pathlib import Path

from daemon.platform_detector import (
    get_platform_detector,
    detect_platform,
    OSType,
    CapabilityLevel,
)
from daemon.os_adapter import get_os_adapter, BaseOSAdapter


class StateManager:
    """
    Manages daemon state with OS-aware persistence and optimization.
    Automatically adapts to the current operating system while
    preferring ThothOS native features when available.
    """
    
    def __init__(self, state_file: Optional[str] = None):
        # Detect platform and get appropriate adapter
        self.platform = get_platform_detector()
        self.os_profile = self.platform.detect()
        self.adapter = get_os_adapter()
        
        # Determine state file location based on OS
        if state_file:
            self.state_file = Path(state_file)
        else:
            self.state_file = self.adapter.get_data_path() / "state.json"
        
        # Initialize state with OS context
        self.state = self._get_default_state()
        self._load_state()
        
        # Update OS context on initialization
        self._update_os_context()
        
        print(f"[StateManager] Initialized on {self.os_profile.name}")
        print(f"[StateManager] Capability level: {self.os_profile.capability_level.name}")
        if self.os_profile.is_native:
            print("[StateManager] Running in NATIVE ThothOS mode - all features enabled")
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default state with OS-specific defaults."""
        return {
            "is_paused": False,
            "last_run": None,
            "scroll_count": 0,
            "os_context": {
                "os_type": self.os_profile.os_type.name,
                "os_name": self.os_profile.name,
                "os_version": self.os_profile.version,
                "is_native": self.os_profile.is_native,
                "capability_level": self.os_profile.capability_level.name,
                "priority_score": self.os_profile.priority_score,
                "available_features": self.os_profile.available_features,
                "detected_at": time.time(),
            },
            "feature_flags": self._get_os_feature_flags(),
            "performance_mode": self._get_performance_mode(),
        }
    
    def _get_os_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags based on OS capabilities."""
        return {
            "symbolic_kernel": self.platform.has_feature("symbolic_kernel_access"),
            "native_scrolls": self.platform.has_feature("native_scroll_triggers"),
            "deep_memory": self.platform.has_feature("deep_memory_integration"),
            "realtime_emotion": self.platform.has_feature("realtime_emotion_sync"),
            "hardware_sensors": self.platform.has_feature("hardware_sensor_direct"),
            "ritual_hooks": self.platform.has_feature("ritual_system_hooks"),
            "kernel_reflection": self.platform.has_feature("kernel_reflection"),
            "symbolic_ipc": self.platform.has_feature("symbolic_ipc"),
            "daemon_persistence": self.platform.has_feature("daemon_persistence"),
            "hot_reload": self.platform.has_feature("hot_reload"),
        }
    
    def _get_performance_mode(self) -> str:
        """Determine performance mode based on OS."""
        if self.os_profile.is_native:
            return "maximum"  # ThothOS gets maximum performance
        elif self.os_profile.capability_level == CapabilityLevel.ENHANCED:
            return "high"
        elif self.os_profile.capability_level == CapabilityLevel.STANDARD:
            return "balanced"
        else:
            return "conservative"
    
    def _update_os_context(self) -> None:
        """Update OS context in state."""
        self.state["os_context"] = {
            "os_type": self.os_profile.os_type.name,
            "os_name": self.os_profile.name,
            "os_version": self.os_profile.version,
            "is_native": self.os_profile.is_native,
            "capability_level": self.os_profile.capability_level.name,
            "priority_score": self.os_profile.priority_score,
            "available_features": self.os_profile.available_features,
            "detected_at": time.time(),
        }
        self.state["feature_flags"] = self._get_os_feature_flags()
        self.state["performance_mode"] = self._get_performance_mode()
        self.save_state()

    def _load_state(self) -> None:
        """Load state from file, with OS-appropriate path handling."""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    loaded_state = json.load(f)
                    # Merge loaded state with defaults (preserves new fields)
                    self.state.update(loaded_state)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[StateManager] Warning: Could not load state: {e}")

    def save_state(self) -> None:
        """Save state to file, ensuring directory exists."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print(f"[StateManager] Warning: Could not save state: {e}")

    def set(self, key: str, value: Any) -> None:
        """Set a state value."""
        self.state[key] = value
        self.save_state()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value with optional default."""
        return self.state.get(key, default)

    def toggle_pause(self) -> bool:
        """Toggle the paused state."""
        self.state["is_paused"] = not self.state["is_paused"]
        self.save_state()
        return self.state["is_paused"]
    
    # ===== OS-Aware Methods =====
    
    def is_native_os(self) -> bool:
        """Check if running on native ThothOS."""
        return self.os_profile.is_native
    
    def get_os_type(self) -> OSType:
        """Get the current OS type."""
        return self.os_profile.os_type
    
    def get_capability_level(self) -> CapabilityLevel:
        """Get the current capability level."""
        return self.os_profile.capability_level
    
    def has_feature(self, feature: str) -> bool:
        """Check if a feature is available on the current OS."""
        return self.state.get("feature_flags", {}).get(feature, False)
    
    def get_os_priority(self) -> int:
        """Get the priority score for the current OS."""
        return self.os_profile.priority_score
    
    def get_performance_mode(self) -> str:
        """Get the current performance mode."""
        return self.state.get("performance_mode", "balanced")
    
    def should_use_native_feature(self, feature: str) -> bool:
        """
        Determine if a native feature should be used.
        Prioritizes ThothOS features when available.
        """
        if self.is_native_os():
            return True  # Always use native features on ThothOS
        return self.has_feature(feature)
    
    def get_os_adapter(self) -> BaseOSAdapter:
        """Get the OS adapter for platform-specific operations."""
        return self.adapter
    
    def get_config_path(self) -> Path:
        """Get the OS-appropriate config path."""
        return self.adapter.get_config_path()
    
    def get_data_path(self) -> Path:
        """Get the OS-appropriate data path."""
        return self.adapter.get_data_path()
    
    def get_log_path(self) -> Path:
        """Get the OS-appropriate log path."""
        return self.adapter.get_log_path()
    
    def log_os_info(self) -> None:
        """Log detailed OS information."""
        print(f"[StateManager] === OS Information ===")
        print(f"[StateManager] Type: {self.os_profile.os_type.name}")
        print(f"[StateManager] Name: {self.os_profile.name}")
        print(f"[StateManager] Version: {self.os_profile.version}")
        print(f"[StateManager] Architecture: {self.os_profile.architecture}")
        print(f"[StateManager] Native ThothOS: {self.os_profile.is_native}")
        print(f"[StateManager] Priority Score: {self.os_profile.priority_score}/100")
        print(f"[StateManager] Capability Level: {self.os_profile.capability_level.name}")
        print(f"[StateManager] Performance Mode: {self.get_performance_mode()}")
        print(f"[StateManager] Available Features: {len(self.os_profile.available_features)}")
        if self.os_profile.limitations:
            print(f"[StateManager] Limitations: {', '.join(self.os_profile.limitations)}")
