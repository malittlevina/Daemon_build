from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import logging

# Disable Flask logging noise
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class UIServer:
    def __init__(self, unimind_ref, host="0.0.0.0", port=5000):
        self.app = Flask(__name__, template_folder="templates", static_folder="static")
        CORS(self.app)
        self.host = host
        self.port = port
        self.unimind = unimind
        self.daemon_thread = None

        # API Routes
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/api/status", "status", self.get_status)
        self.app.add_url_rule("/api/interact", "interact", self.interact, methods=["POST"])
        self.app.add_url_rule("/api/client_telemetry", "telemetry", self.receive_telemetry, methods=["POST"])

    def start(self):
        self.daemon_thread = threading.Thread(target=self._run, daemon=True)
        self.daemon_thread.start()
        print(f"[UIServer] Web Interface running at http://localhost:{self.port}")

    def _run(self):
        self.app.run(host=self.host, port=self.port, use_reloader=False)

    def index(self):
        return render_template("index.html")

    def get_status(self):
        # Gather state from Unimind
        avatar = self.unimind.modules.get("avatar", [None])[0]
        renderer = None # Need renderer instance or move render logic to AvatarEngine
        
        # Quick hack to get renderer if not in unimind explicitly
        # Ideally Unimind would have a centralized 'get_visual()' method
        visual_state = {}
        if avatar:
            visual_state = avatar.get_current_visual_state()

        drives = self.unimind.modules.get("motivation", [])
        drive_status = {}
        for d in drives:
            if hasattr(d, "drives"): # DriveSystem
                drive_status = {k: v.value for k, v in d.drives.items()}

        return jsonify({
            "avatar": visual_state,
            "drives": drive_status,
            "logs": ["Daemon is running..."] # We'd need to hook into a log buffer
        })

    def interact(self, user_input=None):
        # In a real app, this would push to the NLU queue
        # For now, we mock it or need a direct reference to NLU
        # We'll just return a mock since NLU isn't passed to UIServer yet
        return jsonify({"response": "Command received via UI (Backend integration pending)."})

    def receive_telemetry(self):
        data = request.json
        print(f"[UIServer] Client Telemetry: Screen={data.get('screen')}, FPS={data.get('fps')}")
        # Adapt logic could go here
        return jsonify({"status": "ok"})
