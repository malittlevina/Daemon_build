# apps/sample_app/main.py

def run(bridge):
    """
    Sample ThothOS App
    """
    print("[SampleApp] Initialized.")
    
    def on_command(payload):
        print(f"[SampleApp] Received command: {payload}")
        if payload == "ping":
            bridge.send_command("pong", {"source": "sample_app"})
            
    bridge.register_app("sample_app", on_command)
    
    # Simulate some activity
    bridge.send_command("app_started", {"name": "Sample App"})
