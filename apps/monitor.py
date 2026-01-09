from core.module import Module
import urwid
import threading
import time

class SystemMonitor(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.thread = None
        self.running = False
        self.loop = None

    def initialize(self):
        self.kernel.log("SystemMonitor", "Initialized (TUI).")

    def start(self):
        # We don't start the TUI automatically as it takes over stdout.
        # It must be invoked via shell command "tui".
        pass

    def stop(self):
        self.running = False
        if self.loop:
            try:
                self.loop.stop()
            except:
                pass

    def launch(self):
        """Launch the TUI interface."""
        self.running = True
        
        # UI Widgets
        header = urwid.Text("ThothOS System Monitor", align='center')
        
        # Stats Widget
        self.stats_text = urwid.Text("Loading stats...")
        stats_box = urwid.LineBox(self.stats_text, title="System Vitality")
        
        # Process List
        self.proc_text = urwid.Text("Loading processes...")
        proc_box = urwid.LineBox(self.proc_text, title="Active Processes")
        
        # Log Window
        self.log_list = urwid.SimpleListWalker([])
        log_box = urwid.LineBox(urwid.ListBox(self.log_list), title="Kernel Logs")
        
        # Layout
        main_layout = urwid.Pile([
            ('fixed', 1, header),
            ('fixed', 10, urwid.Columns([stats_box, proc_box])),
            ('weight', 1, log_box),
            ('fixed', 1, urwid.Text("Press 'q' to exit"))
        ])
        
        # Input Handler
        def unhandled_input(key):
            if key == 'q':
                raise urwid.ExitMainLoop()

        # Update Loop
        def update_ui(loop, user_data):
            if not self.running: return
            
            # Update Stats
            threads = threading.active_count()
            modules = len(self.kernel.modules)
            world = self.kernel.get_module("world")
            entities = len(world.entity_manager.entities) if world else 0
            
            self.stats_text.set_text(
                f"Active Threads: {threads}\n"
                f"Loaded Modules: {modules}\n"
                f"World Entities: {entities}\n"
                f"Kernel Status:  ONLINE"
            )
            
            # Update Processes
            pm = self.kernel.get_module("process_manager")
            if pm:
                procs = pm.list_processes()
                proc_str = "\n".join([f"{p['pid'][:4]} {p['name'][:10]} {p['status']}" for p in procs[:8]])
                self.proc_text.set_text(proc_str)
            
            # Update Logs (Tail last 10 lines from MemoryLogger if possible, or mocked)
            # For now, we rely on the main log file
            try:
                with open("logs/system.log", "r") as f:
                    lines = f.readlines()[-10:]
                    # Clear and rebuild
                    self.log_list[:] = [urwid.Text(l.strip()) for l in lines]
                    self.log_list.set_focus(len(self.log_list) - 1)
            except:
                pass

            loop.set_alarm_in(1, update_ui)

        # Start Loop
        self.loop = urwid.MainLoop(main_layout, unhandled_input=unhandled_input)
        self.loop.set_alarm_in(0, update_ui)
        try:
            self.loop.run()
        except Exception as e:
            print(f"TUI Crash: {e}")
        finally:
            self.running = False
