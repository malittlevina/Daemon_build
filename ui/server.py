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
        
        visual_state = {}
        if avatar:
            visual_state = avatar.get_current_visual_state()

        # Drive Status
        drives = self.unimind.modules.get("motivation", [])
        drive_status = {}
        for d in drives:
            if hasattr(d, "drives"): # DriveSystem
                drive_status = {k: v.value for k, v in d.drives.items()}

        # World State (For Map)
        world = self.unimind.modules.get("world", [None])[0]
        world_data = {}
        if world:
            # We explicitly serialize just what we need to avoid huge payloads
            # Assuming world.state exists
            if hasattr(world, "state"):
                world_data = {
                    "locations": {k: v.to_dict() for k, v in world.state.locations.items()},
                    "entities": {k: v.to_dict() for k, v in world.state.entities.items()},
                    "time": world.state.time
                }

        return jsonify({
            "avatar": visual_state,
            "drives": drive_status,
            "world": world_data
        })

    def interact(self):
        data = request.json
        user_input = data.get("input", "")
        
        nlu = self.unimind.modules.get("language", [None])[0]
        drives = self.unimind.modules.get("motivation", [None])[0] # Assuming first is DriveSystem
        
        response = "NLU not available."
        if nlu:
            try:
                # We need to find the DriveSystem specifically if multiple motivation modules exist
                # But passing the list or first is okay for now if NLU checks type, or we assume order
                # In main.py, DriveSystem is registered first.
                response = nlu.interpret(user_input, context_drives=drives)
            except Exception as e:
                response = f"Error processing command: {e}"
        
        return jsonify({"response": response})

    def receive_telemetry(self):
        data = request.json
        # print(f"[UIServer] Client Telemetry: Screen={data.get('screen')}, FPS={data.get('fps')}")
        # Adapt logic could go here
        return jsonify({"status": "ok"})
