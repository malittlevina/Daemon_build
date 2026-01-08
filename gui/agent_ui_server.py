from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from core.event_bus import GLOBAL_EVENT_BUS
from gui.context import DaemonUIContext


def _read_body_json(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


class _UIServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, RequestHandlerClass, *, ui_context: DaemonUIContext):
        super().__init__(server_address, RequestHandlerClass)
        self.ui_context = ui_context


class AgentUIHandler(BaseHTTPRequestHandler):
    server: _UIServer  # type: ignore[assignment]

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, status: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 (stdlib naming)
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/contract":
            contract = {
                "version": "0.1",
                "state_endpoint": "/api/state",
                "actions_endpoint": "/api/actions",
                "invoke_endpoint": "/api/action",
                "events_endpoint": "/api/events",
            }
            return self._send_json(contract)

        if path == "/api/state":
            return self._send_json(self.server.ui_context.get_state())

        if path == "/api/actions":
            return self._send_json({"actions": self.server.ui_context.list_actions()})

        if path == "/api/world_model":
            return self._send_json(self.server.ui_context.get_world_model())

        if path == "/api/events":
            return self._handle_sse_events()

        if path == "/" or path == "/index.html":
            return self._serve_static("index.html", "text/html; charset=utf-8")

        if path.startswith("/static/"):
            rel = path[len("/static/") :]
            ctype = "text/plain; charset=utf-8"
            if rel.endswith(".js"):
                ctype = "text/javascript; charset=utf-8"
            elif rel.endswith(".css"):
                ctype = "text/css; charset=utf-8"
            return self._serve_static(rel, ctype)

        return self._send_json({"error": "not_found", "path": path}, status=404)

    def do_POST(self) -> None:  # noqa: N802 (stdlib naming)
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/action":
            try:
                body = _read_body_json(self)
                name = str(body.get("name", "")).strip()
                args = body.get("args") or {}
                result = self.server.ui_context.invoke_action(name, args=args)
                return self._send_json({"ok": True, "result": result})
            except ValueError as e:
                return self._send_json({"ok": False, "error": str(e)}, status=400)
            except Exception as e:
                GLOBAL_EVENT_BUS.publish(
                    "ui.action.error",
                    {"error": str(e)},
                    source="ui",
                    severity="error",
                    tags=["ui"],
                )
                return self._send_json({"ok": False, "error": "action_failed", "detail": str(e)}, status=500)

        return self._send_json({"error": "not_found", "path": path}, status=404)

    def _serve_static(self, filename: str, content_type: str) -> None:
        base_dir = os.path.join(os.path.dirname(__file__), "static")
        full_path = os.path.abspath(os.path.join(base_dir, filename))
        if not full_path.startswith(os.path.abspath(base_dir) + os.sep):
            return self._send_text("forbidden", status=403)
        if not os.path.exists(full_path):
            return self._send_text("not found", status=404)
        with open(full_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_sse_events(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        q = GLOBAL_EVENT_BUS.subscribe(max_queue=200)
        try:
            # Emit a hello + recent history for fast bootstrapping.
            self.wfile.write(b"event: hello\n")
            self.wfile.write(b"data: {\"ok\":true}\n\n")
            self.wfile.flush()

            for evt in GLOBAL_EVENT_BUS.recent(limit=25):
                payload = json.dumps(evt, ensure_ascii=False).encode("utf-8")
                self.wfile.write(b"event: timeline\n")
                self.wfile.write(b"data: " + payload + b"\n\n")
            self.wfile.flush()

            while True:
                try:
                    evt = q.get(timeout=15)
                except Exception:
                    # keep-alive ping
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    continue
                payload = evt.to_json().encode("utf-8")
                self.wfile.write(b"event: timeline\n")
                self.wfile.write(b"data: " + payload + b"\n\n")
                self.wfile.flush()
        except BrokenPipeError:
            pass
        finally:
            GLOBAL_EVENT_BUS.unsubscribe(q)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Silence default HTTP request logs; events are tracked via the bus.
        return


def start_agent_ui_server(
    *,
    ui_context: DaemonUIContext,
    host: str = "127.0.0.1",
    port: int = 8765,
    background: bool = True,
) -> Optional[threading.Thread]:
    server = _UIServer((host, port), AgentUIHandler, ui_context=ui_context)
    GLOBAL_EVENT_BUS.publish(
        "ui.server.start",
        {"host": host, "port": port},
        source="ui",
        tags=["ui"],
    )

    def _serve() -> None:
        try:
            server.serve_forever(poll_interval=0.25)
        finally:
            GLOBAL_EVENT_BUS.publish("ui.server.stop", {}, source="ui", tags=["ui"])

    if background:
        t = threading.Thread(target=_serve, daemon=True)
        t.start()
        return t

    _serve()
    return None

