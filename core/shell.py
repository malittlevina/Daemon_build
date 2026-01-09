from core.module import Module
import threading # Required for shell monitor command
import sys
import shlex

# ANSI Colors
C_RESET = "\033[0m"
C_GREEN = "\033[92m"
C_BLUE = "\033[94m"
C_RED = "\033[91m"
C_CYAN = "\033[96m"
C_YELLOW = "\033[93m"

class Shell(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.prompt = f"{C_GREEN}[guest@thoth ~]${C_RESET} "
        self.command_history = []

    def initialize(self):
        self.kernel.log("Shell", "Initialized.")

    def start(self):
        self.update_prompt()

    def stop(self):
        pass

    def update_prompt(self):
        users = self.kernel.get_module("users")
        if users:
            current = users.get_current_user()
            user = current["username"]
            role = current["role"]
            color = C_RED if role == "superuser" else C_GREEN
            symbol = "#" if role == "superuser" else "$"
            self.prompt = f"{color}[{user}@thoth ~]{symbol}{C_RESET} "

    def process_input(self, user_input):
        if not user_input.strip():
            return

        self.command_history.append(user_input)
        
        # Parse logic
        try:
            parts = shlex.split(user_input)
        except ValueError:
            print(f"{C_RED}Syntax Error: Unbalanced quotes.{C_RESET}")
            return

        command = parts[0].lower()

        # Built-ins
        if command == "login":
            self._handle_login(parts)
        elif command == "logout":
            users = self.kernel.get_module("users")
            if users: 
                users.logout()
                self.update_prompt()
        elif command == "whoami":
            users = self.kernel.get_module("users")
            print(users.get_current_user() if users else "System")
        elif command == "help":
            self._print_help()
        elif command == "clear":
            print("\033[H\033[J", end="") # ANSI clear screen
        elif command == "ps":
            self._list_processes()
        elif command == "ls":
            self._list_files(parts)
        elif command == "cat":
            self._read_file(parts)
        elif command == "monitor":
            self._show_monitor()
        elif command == "tui":
            monitor = self.kernel.get_module("monitor")
            if monitor:
                monitor.launch()
            else:
                print(f"{C_RED}System Monitor module not loaded.{C_RESET}")
        else:
            # Fallback to NLU
            self._dispatch_nlu(user_input)

    def _print_help(self):
        print(f"\n{C_CYAN}--- ThothOS Commands ---{C_RESET}")
        print(f" {C_YELLOW}login{C_RESET} <user> <pass>  : Authenticate")
        print(f" {C_YELLOW}logout{C_RESET}              : End session")
        print(f" {C_YELLOW}ps{C_RESET}                  : List processes")
        print(f" {C_YELLOW}ls{C_RESET} [path]           : List files")
        print(f" {C_YELLOW}cat{C_RESET} <file>          : Read file")
        print(f" {C_YELLOW}monitor{C_RESET}             : System status")
        print(f" {C_YELLOW}clear{C_RESET}               : Clear screen")
        print(f" {C_YELLOW}[text]{C_RESET}              : Speak to Daemon (NLU)")

    def _list_processes(self):
        pm = self.kernel.get_module("process_manager")
        if pm:
            procs = pm.list_processes()
            print(f"\n{C_BLUE}PID      User     Status    Runtime  Name{C_RESET}")
            for p in procs:
                status_col = C_GREEN if p["status"] == "running" else C_RED
                print(f"{p['pid']} {p['user']:<8} {status_col}{p['status']:<9}{C_RESET} {p['runtime']:<8} {p['name']}")
        else:
            print("Process Manager not found.")

    def _list_files(self, parts):
        vfs = self.kernel.get_module("vfs")
        path = parts[1] if len(parts) > 1 else "/"
        if vfs:
            res = vfs.list_dir(path)
            if isinstance(res, list):
                print(f"{C_BLUE}Contents of {path}:{C_RESET}")
                for item in res:
                    print(f"  {item}")
            else:
                print(f"{C_RED}{res}{C_RESET}")

    def _read_file(self, parts):
        if len(parts) < 2:
            print("Usage: cat <file>")
            return
        vfs = self.kernel.get_module("vfs")
        if vfs:
            content = vfs.read_file(parts[1])
            print(content)

    def _show_monitor(self):
        # Simple text dump for now
        print(f"\n{C_CYAN}--- System Monitor ---{C_RESET}")
        
        # Threads
        print(f"Active Threads: {threading.active_count()}")
        
        # Modules
        print(f"Loaded Modules: {len(self.kernel.modules)}")
        
        # Network
        net = self.kernel.get_module("network")
        if net:
            status = net.get_status()
            print(f"Network: {status['active_connections']} connections")

        # World
        world = self.kernel.get_module("world")
        if world:
            count = len(world.entity_manager.entities)
            print(f"World Entities: {count}")

    def _dispatch_nlu(self, text):
        nlu = self.kernel.get_module("nlu")
        if nlu:
            print(f"{C_BLUE}Thinking...{C_RESET}")
            result = nlu.interpret(text)
            print(f"{C_CYAN}[Daemon]{C_RESET}: {result}")
            self.kernel.dispatch("user_input", {"text": text, "result": result})
        else:
            print(f"{C_RED}NLU Offline.{C_RESET}")

    def _handle_login(self, parts):
        if len(parts) < 3:
            print("Usage: login <username> <password>")
            return
        
        users = self.kernel.get_module("users")
        if users:
            session = users.login(parts[1], parts[2])
            if session:
                self.update_prompt()
                print(f"{C_GREEN}Welcome, {session['username']}.{C_RESET}")
            else:
                print(f"{C_RED}Access Denied.{C_RESET}")
