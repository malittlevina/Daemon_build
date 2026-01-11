from __future__ import annotations

import base64
import json
import os
import urllib.request
from typing import Any, Dict, Optional


def _post_json(url: str, payload: Dict[str, Any], timeout_s: int = 10) -> Dict[str, Any]:
    data = json.dumps(payload, default=str).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:  # noqa: S310 (user-controlled URL by design)
        body = resp.read().decode("utf-8")
        return json.loads(body)


def send_event(server_base_url: str, device_id: str, event_type: str, content: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = server_base_url.rstrip("/") + "/ingest/event"
    payload = {"device_id": device_id, "type": event_type, "content": content, "meta": meta or {}}
    return _post_json(url, payload)


def send_clip_metadata(
    server_base_url: str,
    device_id: str,
    clip_name: str,
    mime: str = "application/octet-stream",
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    url = server_base_url.rstrip("/") + "/ingest/clip"
    payload = {"device_id": device_id, "clip_name": clip_name, "mime": mime, "meta": meta or {}}
    return _post_json(url, payload, timeout_s=20)


def send_clip_file(
    server_base_url: str,
    device_id: str,
    file_path: str,
    clip_name: Optional[str] = None,
    mime: str = "application/octet-stream",
    meta: Optional[Dict[str, Any]] = None,
    max_bytes: int = 5_000_000,
) -> Dict[str, Any]:
    """
    Convenience for small clips. For real streaming, you'd ship to object storage and only send metadata here.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    size = os.path.getsize(file_path)
    if size > max_bytes:
        raise ValueError(f"Refusing to upload {size} bytes (max {max_bytes}). Send metadata only.")

    with open(file_path, "rb") as f:
        raw = f.read()
    url = server_base_url.rstrip("/") + "/ingest/clip"
    payload = {
        "device_id": device_id,
        "clip_name": clip_name or os.path.basename(file_path),
        "mime": mime,
        "meta": meta or {},
        "data_b64": base64.b64encode(raw).decode("ascii"),
    }
    return _post_json(url, payload, timeout_s=30)

