from core.module import Module

class Shell(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.prompt = "[guest@thoth ~]$ "

    def initialize(self):
        self.kernel.log("Shell", "Initialized.")

    def start(self):
        # Update prompt based on user
        self.update_prompt()

    def stop(self):
        pass

    def update_prompt(self):
        users = self.kernel.get_module("users")
        if users:
            current = users.get_current_user()
            user = current["username"]
            role = current["role"]
            symbol = "#" if role == "superuser" else "$"
            self.prompt = f"[{user}@thoth ~]{symbol} "

    def process_input(self, user_input):
        if not user_input:
            return

        # 1. Handle Built-in Shell Commands
        parts = user_input.split()
        command = parts[0].lower()

        if command == "login":
            self._handle_login(parts)
            return
        elif command == "logout":
            users = self.kernel.get_module("users")
            if users: 
                users.logout()
                self.update_prompt()
            return
        elif command == "whoami":
            users = self.kernel.get_module("users")
            print(users.get_current_user() if users else "System")
            return
        elif command == "help":
            print("Available commands: login, logout, whoami, exit, [any natural language request]")
            return

        # 2. Dispatch to NLU/Kernel if not a shell command
        nlu = self.kernel.get_module("nlu")
        result = None
        
        if nlu:
            try:
                # NLU interpretation
                result = nlu.interpret(user_input)
                # Fallback handled inside NLU now
            except Exception as e:
                self.kernel.log("Shell", f"NLU Error: {e}", level="error")
                result = "System Error"
        
        # 3. Publish Event
        self.kernel.dispatch("user_input", {"text": user_input, "result": result})
        print(f"[Shell] Output: {result}")

    def _handle_login(self, parts):
        if len(parts) < 3:
            print("Usage: login <username> <password>")
            return
        
        users = self.kernel.get_module("users")
        if users:
            session = users.login(parts[1], parts[2])
            if session:
                self.update_prompt()
                print(f"Welcome, {session['username']}.")
            else:
                print("Access Denied.")
