from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from daemon.event_bus import EventBus
from daemon.events import DaemonEvent


_HTML = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Unimind Textbox</title>
    <style>
      body { font-family: sans-serif; max-width: 900px; margin: 2rem auto; }
      textarea { width: 100%; height: 10rem; font-size: 16px; }
      button { margin-top: 0.5rem; padding: 0.5rem 1rem; font-size: 16px; }
      .hint { color: #555; margin-top: 1rem; }
    </style>
  </head>
  <body>
    <h2>Unimind Textbox</h2>
    <form method="POST" action="/submit">
      <textarea name="text" placeholder="Type here..."></textarea>
      <br/>
      <button type="submit">Send</button>
    </form>
    <div class="hint">This posts text into the daemon event bus.</div>
  </body>
</html>
"""


def start_textbox_server(bus: EventBus, host: str = "0.0.0.0", port: int = 8765) -> threading.Thread:
    """
    Simple web textbox (no dependencies). Visit http://<host>:<port> in a browser.
    """

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):  # noqa: N802
            if self.path == "/" or self.path.startswith("/?"):
                self._send(200, _HTML)
            else:
                self._send(404, "Not found", content_type="text/plain; charset=utf-8")

        def do_POST(self):  # noqa: N802
            if self.path != "/submit":
                self._send(404, "Not found", content_type="text/plain; charset=utf-8")
                return
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            data = parse_qs(raw)
            text = (data.get("text") or [""])[0].strip()
            if text:
                bus.publish(DaemonEvent(type="text_input", payload={"text": text}, source="textbox"))
            self._send(200, _HTML)

        def log_message(self, format, *args):  # noqa: A003
            # Silence default HTTP logging.
            return

    def run() -> None:
        httpd = ThreadingHTTPServer((host, port), Handler)
        print(f"[Textbox] Listening on http://{host}:{port}")
        httpd.serve_forever()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return t

