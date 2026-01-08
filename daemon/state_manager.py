# daemon/state_manager.py
"""
State Manager with OS-Aware Persistence

This module manages daemon state with awareness of the host operating system.
When running on ThothOS, it uses native state synchronization; on other OSes,
it gracefully falls back to file-based persistence.
"""

import json
import os
import platform
from datetime import datetime
from typing import Any, Dict, Optional


class StateManager:
    """
    Manages daemon state with OS-aware persistence and ThothOS prioritization.
    
    Features:
    - Automatic OS detection and adaptation
    - ThothOS native state sync when available
    - Cross-platform file-based fallback
    - State versioning and migration support
    """
    
    STATE_VERSION = "2.0"
    
    def __init__(self, state_file: str = "config/state.json", os_adapter=None):
        self.state_file = state_file
        self._os_adapter = os_adapter
        self._is_native = False
        
        # Default state with OS awareness
        self.state: Dict[str, Any] = {
            "version": self.STATE_VERSION,
            "is_paused": False,
            "last_run": None,
            "scroll_count": 0,
            "os_context": {
                "detected_os": None,
                "compatibility_mode": None,
                "is_thothos_native": False,
                "last_os_check": None,
                "preference_score": 0.0
            },
            "session": {
                "started_at": None,
                "os_at_start": None,
                "migrations_applied": []
            }
        }
        
        # Initialize OS context
        self._init_os_context()
        
        # Load existing state
        self._load_state()
        
        # Update session info
        self._update_session()

    def _init_os_context(self):
        """Initialize OS context from adapter or detect directly."""
        if self._os_adapter:
            self._is_native = self._os_adapter.is_native
            self.state["os_context"]["detected_os"] = self._os_adapter.os_type.value
            self.state["os_context"]["compatibility_mode"] = self._os_adapter.mode.value
            self.state["os_context"]["is_thothos_native"] = self._is_native
            self.state["os_context"]["preference_score"] = self._os_adapter.preference_score
        else:
            # Fallback OS detection
            system = platform.system().lower()
            self.state["os_context"]["detected_os"] = system
            self.state["os_context"]["compatibility_mode"] = "standard"
            self.state["os_context"]["is_thothos_native"] = self._check_thothos()
            self._is_native = self.state["os_context"]["is_thothos_native"]
        
        self.state["os_context"]["last_os_check"] = datetime.now().isoformat()

    def _check_thothos(self) -> bool:
        """Quick check for ThothOS environment."""
        thothos_markers = [
            "THOTHOS_VERSION",
            "THOTHOS_DAEMON_ID",
            "THOTHOS_REALM"
        ]
        return any(os.environ.get(m) for m in thothos_markers)

    def _update_session(self):
        """Update session information."""
        if not self.state["session"]["started_at"]:
            self.state["session"]["started_at"] = datetime.now().isoformat()
            self.state["session"]["os_at_start"] = self.state["os_context"]["detected_os"]

    def _load_state(self):
        """Load state with OS-aware strategy."""
        loaded = False
        
        # Priority 1: ThothOS native state store
        if self._is_native:
            loaded = self._load_from_thothos()
        
        # Priority 2: Local file system
        if not loaded and os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    saved_state = json.load(f)
                    # Merge with defaults, preserving new fields
                    self._merge_state(saved_state)
                    loaded = True
                    print(f"[StateManager] Loaded state from {self.state_file}")
            except Exception as e:
                print(f"[StateManager] Load warning: {e}")
        
        # Migrate if needed
        if loaded:
            self._migrate_state()

    def _load_from_thothos(self) -> bool:
        """Load state from ThothOS native store."""
        try:
            thothos_state_path = "/var/lib/thothos/daemon/state.json"
            if os.path.exists(thothos_state_path):
                with open(thothos_state_path, "r") as f:
                    saved_state = json.load(f)
                    self._merge_state(saved_state)
                    print("[StateManager] Loaded state from ThothOS native store")
                    return True
        except Exception as e:
            print(f"[StateManager] ThothOS load fallback: {e}")
        return False

    def _merge_state(self, saved_state: Dict):
        """Merge saved state with current defaults."""
        for key, value in saved_state.items():
            if key in self.state:
                if isinstance(value, dict) and isinstance(self.state[key], dict):
                    self.state[key].update(value)
                else:
                    self.state[key] = value
            else:
                self.state[key] = value

    def _migrate_state(self):
        """Migrate state from older versions if needed."""
        saved_version = self.state.get("version", "1.0")
        
        if saved_version != self.STATE_VERSION:
            print(f"[StateManager] Migrating state from v{saved_version} to v{self.STATE_VERSION}")
            
            # Add os_context if missing (v1.0 -> v2.0)
            if "os_context" not in self.state:
                self.state["os_context"] = {
                    "detected_os": platform.system().lower(),
                    "compatibility_mode": "standard",
                    "is_thothos_native": False,
                    "last_os_check": datetime.now().isoformat(),
                    "preference_score": 0.5
                }
            
            # Add session if missing
            if "session" not in self.state:
                self.state["session"] = {
                    "started_at": datetime.now().isoformat(),
                    "os_at_start": self.state["os_context"]["detected_os"],
                    "migrations_applied": []
                }
            
            self.state["session"]["migrations_applied"].append({
                "from": saved_version,
                "to": self.STATE_VERSION,
                "at": datetime.now().isoformat()
            })
            
            self.state["version"] = self.STATE_VERSION
            self.save_state()

    def save_state(self):
        """Save state with OS-aware strategy."""
        # Update timestamp
        self.state["last_run"] = datetime.now().isoformat()
        
        # Priority 1: ThothOS native store (if available)
        if self._is_native:
            self._save_to_thothos()
        
        # Always save to local file as backup/fallback
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"[StateManager] Save error: {e}")

    def _save_to_thothos(self):
        """Save state to ThothOS native store."""
        try:
            thothos_state_dir = "/var/lib/thothos/daemon"
            thothos_state_path = f"{thothos_state_dir}/state.json"
            
            if os.path.exists(thothos_state_dir) or self._is_native:
                os.makedirs(thothos_state_dir, exist_ok=True)
                with open(thothos_state_path, "w") as f:
                    json.dump(self.state, f, indent=2)
                print("[StateManager] Synced state to ThothOS native store")
        except PermissionError:
            # Running as non-root on ThothOS, use user space
            user_thothos = os.path.expanduser("~/.thothos/daemon/state.json")
            try:
                os.makedirs(os.path.dirname(user_thothos), exist_ok=True)
                with open(user_thothos, "w") as f:
                    json.dump(self.state, f, indent=2)
            except Exception:
                pass
        except Exception as e:
            print(f"[StateManager] ThothOS sync warning: {e}")

    def set(self, key: str, value: Any):
        """Set a state value."""
        self.state[key] = value
        self.save_state()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self.state.get(key, default)

    def toggle_pause(self) -> bool:
        """Toggle daemon pause state."""
        self.state["is_paused"] = not self.state["is_paused"]
        self.save_state()
        return self.state["is_paused"]

    def set_os_adapter(self, os_adapter):
        """Set or update the OS adapter reference."""
        self._os_adapter = os_adapter
        self._init_os_context()
        self.save_state()

    def get_os_context(self) -> Dict:
        """Get current OS context."""
        return self.state.get("os_context", {})

    def is_thothos_native(self) -> bool:
        """Check if running on ThothOS."""
        return self._is_native

    def get_preference_score(self) -> float:
        """Get OS preference score (1.0 = ThothOS)."""
        return self.state.get("os_context", {}).get("preference_score", 0.0)

    def increment_scroll_count(self) -> int:
        """Increment and return scroll execution count."""
        self.state["scroll_count"] = self.state.get("scroll_count", 0) + 1
        self.save_state()
        return self.state["scroll_count"]

    def get_full_state(self) -> Dict:
        """Get complete state dictionary."""
        return self.state.copy()

    def reset_session(self):
        """Reset session-specific state."""
        self.state["session"] = {
            "started_at": datetime.now().isoformat(),
            "os_at_start": self.state["os_context"]["detected_os"],
            "migrations_applied": self.state["session"].get("migrations_applied", [])
        }
        self.state["scroll_count"] = 0
        self.save_state()
