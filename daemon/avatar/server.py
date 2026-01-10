from __future__ import annotations

import asyncio
import json
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

from daemon.avatar.events import AvatarEvent


@dataclass
class AvatarBroadcaster:
    """
    Best-effort WebSocket broadcaster.

    - If `websockets` is installed, hosts a WS server and broadcasts JSON events.
    - If not, it silently becomes a no-op (daemon continues to run).
    """

    host: str = "0.0.0.0"
    port: int = 8766
    _clients: Set[Any] = field(default_factory=set)
    _loop: Optional[asyncio.AbstractEventLoop] = None
    _thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        def run() -> None:
            try:
                import websockets  # type: ignore
            except Exception as e:
                print(f"[Avatar] WebSocket disabled (missing websockets): {e}")
                return

            async def handler(ws):
                self._clients.add(ws)
                try:
                    async for _msg in ws:
                        # Ignore client messages for now.
                        pass
                finally:
                    self._clients.discard(ws)

            async def main():
                self._loop = asyncio.get_running_loop()
                async with websockets.serve(handler, self.host, self.port):
                    print(f"[Avatar] WebSocket listening on ws://{self.host}:{self.port}")
                    while True:
                        await asyncio.sleep(3600)

            asyncio.run(main())

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def publish(self, event: AvatarEvent) -> None:
        if not self._clients or not self._loop:
            return
        payload = json.dumps(event.to_dict(), ensure_ascii=False)

        async def _broadcast():
            dead = []
            for ws in list(self._clients):
                try:
                    await ws.send(payload)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self._clients.discard(ws)

        try:
            asyncio.run_coroutine_threadsafe(_broadcast(), self._loop)
        except Exception:
            return

