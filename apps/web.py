from core.module import Module
from flask import Flask, jsonify
import threading
import logging

# Suppress Flask CLI logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class WebPortal(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.app = Flask(__name__)
        self.port = 8080
        self.thread = None

        # Define Routes
        @self.app.route('/')
        def index():
            return """
            <html>
            <head><title>ThothOS Portal</title>
            <style>
                body { font-family: monospace; background: #111; color: #0f0; padding: 20px; }
                .box { border: 1px solid #333; padding: 10px; margin-bottom: 10px; }
                h1 { color: #fff; }
            </style>
            </head>
            <body>
                <h1>ThothOS Dashboard</h1>
                <div class="box" id="status">Loading...</div>
                <div class="box" id="logs">Loading...</div>
                <script>
                    setInterval(() => {
                        fetch('/api/status').then(r => r.json()).then(data => {
                            let html = `<b>Status:</b> ${data.kernel_status}<br>`;
                            html += `<b>Modules:</b> ${data.module_count}<br>`;
                            html += `<b>Threads:</b> ${data.thread_count}<br>`;
                            html += `<b>World Entities:</b> ${data.world_entities}<br>`;
                            document.getElementById('status').innerHTML = html;
                        });
                        fetch('/api/logs').then(r => r.json()).then(data => {
                            document.getElementById('logs').innerHTML = data.logs.join("<br>");
                        });
                    }, 1000);
                </script>
            </body>
            </html>
            """

        @self.app.route('/api/status')
        def api_status():
            world = self.kernel.get_module("world")
            count = len(world.entity_manager.entities) if world else 0
            return jsonify({
                "kernel_status": "ONLINE",
                "module_count": len(self.kernel.modules),
                "thread_count": threading.active_count(),
                "world_entities": count
            })

        @self.app.route('/api/logs')
        def api_logs():
            try:
                with open("logs/system.log", "r") as f:
                    lines = f.readlines()[-10:]
                return jsonify({"logs": [l.strip() for l in lines]})
            except:
                return jsonify({"logs": ["Log unavailable"]})

    def initialize(self):
        self.kernel.log("WebPortal", f"Initialized. Dashboard at http://localhost:{self.port}")

    def start(self):
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def stop(self):
        pass

    def _run_server(self):
        self.app.run(host="0.0.0.0", port=self.port, debug=False, use_reloader=False)
