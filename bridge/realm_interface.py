from __future__ import annotations

from typing import Any, Dict, Optional

from storyrealms.service import StoryrealmsService

class RealmInterface:
    def __init__(self):
        self.connected = False
        self.current_realm = "default"
        self._engine = StoryrealmsService()
        print("[RealmInterface] Initialized.")

    def enter_realm(self, realm_name: str):
        self.connected = True
        self.current_realm = realm_name
        print(f"[RealmInterface] Entering realm: {realm_name}")
        # Connect to Storyrealms engine (world runtime)
        self._engine.enter_realm(realm_name, actor="RealmInterface")

    def send_command(self, command):
        if self.connected:
            print(f"[RealmInterface] Sending command to realm '{self.current_realm}': {command}")
            if isinstance(command, str):
                self._engine.dispatch_command(command, realm=self.current_realm, actor="RealmInterface")
            elif isinstance(command, dict):
                cmd = str(command.get("command") or "command")
                args = command.get("args")
                if not isinstance(args, dict):
                    args = {"value": args}
                self._engine.dispatch_command(cmd, args=args, realm=self.current_realm, actor="RealmInterface")
            else:
                self._engine.dispatch_command("command", args={"value": command}, realm=self.current_realm, actor="RealmInterface")
        else:
            print("[RealmInterface] No realm connected. Command not sent.")

    def send_event(self, event_type: str, data: dict):
        if self.connected:
            print(f"[RealmInterface] Event: {event_type} | Data: {data}")
            self._engine.emit_event(event_type, payload=data, realm=self.current_realm, actor="RealmInterface")
        else:
            print("[RealmInterface] No realm connected. Event ignored.")

    def get_current_state(self):
        if not self.connected:
            return {"realm": self.current_realm, "status": "disconnected", "state": None}
        state = self._engine.query_state(realm=self.current_realm)
        return {"realm": self.current_realm, "status": "stable", "state": state.get("state")}
