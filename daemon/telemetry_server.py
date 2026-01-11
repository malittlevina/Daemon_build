from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple


def _utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json_body(handler: BaseHTTPRequestHandler) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except Exception:
        length = 0
    if length <= 0:
        return None, "Empty body"
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8")), None
    except Exception as e:
        return None, f"Invalid JSON: {e}"


class TelemetryHandler(BaseHTTPRequestHandler):
    """
    Minimal home-server ingest endpoints (no external deps):

    - POST /ingest/event  (JSON)
      { "device_id": "...", "type": "...", "content": ..., "ts": "...optional..." }

    - POST /ingest/clip (JSON, metadata-only; content optional base64)
      { "device_id": "...", "clip_name": "...", "mime": "...", "data_b64": "...optional...", "meta": {...} }
    """

    server_version = "DaemonTelemetry/0.1"

    def _send(self, code: int, payload: Dict[str, Any]) -> None:
        out = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_GET(self):  # noqa: N802
        if self.path == "/health":
            return self._send(200, {"ok": True})
        return self._send(404, {"ok": False, "error": "Not found"})

    def do_POST(self):  # noqa: N802
        if self.path not in ("/ingest/event", "/ingest/clip"):
            return self._send(404, {"ok": False, "error": "Not found"})

        body, err = _read_json_body(self)
        if err:
            return self._send(400, {"ok": False, "error": err})

        # Where to store (home-server side)
        base_dir = getattr(self.server, "storage_dir", "memory_tree")  # type: ignore[attr-defined]
        inbox_dir = os.path.join(base_dir, "inbox")
        clips_dir = os.path.join(base_dir, "clips")
        os.makedirs(inbox_dir, exist_ok=True)
        os.makedirs(clips_dir, exist_ok=True)

        device_id = str(body.get("device_id", "unknown")).strip() or "unknown"
        now = _utc_iso()

        if self.path == "/ingest/event":
            event = {
                "ts": body.get("ts") or now,
                "device_id": device_id,
                "type": body.get("type", "event"),
                "content": body.get("content"),
                "meta": body.get("meta", {}),
            }
            day = event["ts"][:10]
            out_path = os.path.join(inbox_dir, f"{day}.jsonl")
            with open(out_path, "a") as f:
                f.write(json.dumps(event, default=str) + "\n")
            return self._send(200, {"ok": True, "stored": out_path})

        # /ingest/clip (metadata first; optional base64 payload)
        clip_name = str(body.get("clip_name", f"clip-{int(time.time())}")).strip()
        mime = str(body.get("mime", "application/octet-stream"))
        meta = body.get("meta", {})

        clip_record = {
            "ts": now,
            "device_id": device_id,
            "clip_name": clip_name,
            "mime": mime,
            "meta": meta,
        }

        # Store metadata (always)
        day = now[:10]
        meta_path = os.path.join(clips_dir, f"{day}.jsonl")
        with open(meta_path, "a") as f:
            f.write(json.dumps(clip_record, default=str) + "\n")

        # Optional: store content if provided (kept simple, best-effort)
        data_b64 = body.get("data_b64")
        if data_b64:
            try:
                import base64

                raw = base64.b64decode(data_b64)
                safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in clip_name)[:120]
                blob_path = os.path.join(clips_dir, f"{day}__{device_id}__{safe}.bin")
                with open(blob_path, "wb") as bf:
                    bf.write(raw)
                clip_record["blob_path"] = blob_path
            except Exception as e:
                clip_record["blob_error"] = str(e)

        return self._send(200, {"ok": True, "stored_meta": meta_path, "clip": clip_record})


def run_telemetry_server(host: str = "0.0.0.0", port: int = 8787, storage_dir: str = "memory_tree") -> None:
    httpd = HTTPServer((host, int(port)), TelemetryHandler)
    httpd.storage_dir = storage_dir  # type: ignore[attr-defined]
    print(f"[Daemon][Telemetry] Listening on http://{host}:{port} (storage={storage_dir})")
    httpd.serve_forever()


if __name__ == "__main__":
    run_telemetry_server()

