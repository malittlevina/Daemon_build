from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from storyrealms.service import StoryrealmsService


def _json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")


def _read_body(handler: BaseHTTPRequestHandler) -> bytes:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return b""
    return handler.rfile.read(length)


def route_request(
    svc: StoryrealmsService,
    *,
    method: str,
    path: str,
    query: Dict[str, Any],
    body: Optional[Dict[str, Any]],
) -> Tuple[int, Dict[str, str], Dict[str, Any]]:
    """
    Pure routing helper for Storyrealms HTTP API.

    Returns: (status, headers, json_body)
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if method == "OPTIONS":
        return 204, headers, {}

    realm = query.get("realm") or None
    try:
        events_limit = int(query.get("limit") or 50)
    except Exception:
        events_limit = 50

    if method == "GET" and path == "/health":
        return 200, headers, {"status": "ok"}

    if method == "GET" and path == "/realm/state":
        return 200, headers, svc.query_state(realm=realm)

    if method == "GET" and path == "/realm/view":
        return 200, headers, svc.get_view(realm=realm, events_limit=events_limit)

    if method == "GET" and path == "/realm/events":
        return 200, headers, svc.list_events(realm=realm, limit=events_limit)

    if method == "POST" and path == "/realm/event":
        b = body or {}
        event_type = str(b.get("type") or "")
        payload = b.get("payload") or {}
        actor = b.get("actor") or "http"
        meta = b.get("meta") or {"source": "http"}
        if not isinstance(payload, dict):
            return 400, headers, {"error": "payload must be a dict"}
        out = svc.emit_event(event_type, payload, realm=realm, actor=actor, meta=meta)
        return 200, headers, out

    if method == "POST" and path == "/realm/command":
        b = body or {}
        command = str(b.get("command") or "")
        args = b.get("args") or {}
        actor = b.get("actor") or "http"
        meta = b.get("meta") or {"source": "http"}
        if not isinstance(args, dict):
            return 400, headers, {"error": "args must be a dict"}
        out = svc.dispatch_command(command, args=args, realm=realm, actor=actor, meta=meta)
        return 200, headers, out

    return 404, headers, {"error": f"not found: {method} {path}"}


@dataclass(slots=True)
class StoryrealmsHttpApi:
    service: StoryrealmsService

    def handler_class(self):
        svc = self.service

        class Handler(BaseHTTPRequestHandler):
            def _send(self, status: int, headers: Dict[str, str], payload: Dict[str, Any]) -> None:
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.end_headers()
                if status == 204:
                    return
                self.wfile.write(_json_bytes(payload))

            def do_OPTIONS(self):  # noqa: N802
                status, headers, payload = route_request(svc, method="OPTIONS", path=self.path.split("?")[0], query={}, body=None)
                self._send(status, headers, payload)

            def do_GET(self):  # noqa: N802
                parsed = urlparse(self.path)
                qs = {k: v[0] for k, v in parse_qs(parsed.query).items() if v}
                status, headers, payload = route_request(svc, method="GET", path=parsed.path, query=qs, body=None)
                self._send(status, headers, payload)

            def do_POST(self):  # noqa: N802
                parsed = urlparse(self.path)
                qs = {k: v[0] for k, v in parse_qs(parsed.query).items() if v}
                raw = _read_body(self)
                body = None
                if raw:
                    try:
                        body = json.loads(raw.decode("utf-8"))
                    except Exception:
                        status, headers, payload = 400, {"Content-Type": "application/json; charset=utf-8"}, {"error": "invalid json"}
                        self._send(status, headers, payload)
                        return
                status, headers, payload = route_request(svc, method="POST", path=parsed.path, query=qs, body=body)
                self._send(status, headers, payload)

            def log_message(self, fmt, *args):  # noqa: A003
                # Keep daemon output clean; uncomment for debugging.
                return

        return Handler


def start_storyrealms_http_server(
    service: StoryrealmsService,
    *,
    host: str = "127.0.0.1",
    port: int = 7777,
    daemon: bool = True,
) -> HTTPServer:
    """
    Starts the server. If daemon=True, runs in a background thread.
    """
    api = StoryrealmsHttpApi(service)
    httpd = HTTPServer((host, int(port)), api.handler_class())
    if daemon:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
    return httpd

