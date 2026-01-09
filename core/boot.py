from core.registry import Registry
from core.users import UserManager
from core.vfs import VFS
from core.process import ProcessManager
from core.network import NetworkManager
from core.scheduler import Scheduler
from core.packager import PackageManager
from core.clipboard import Clipboard
from core.notifications import NotificationManager
from core.view import ViewManager
from core.interface import Interface
from bridge.thoth_bridge import ThothBridge
from bridge.xr_server import XRServer

def load_kernel_services(kernel):
    """
    Registers the low-level infrastructure services.
    These are required for the OS to function as a computer.
    """
    kernel.log("Boot", "Loading Kernel Services...")
    
    # 1. Hardware Abstraction / Core
    kernel.register_module("registry", Registry(kernel))
    kernel.register_module("vfs", VFS(kernel))
    kernel.register_module("process_manager", ProcessManager(kernel))
    kernel.register_module("network", NetworkManager(kernel))
    kernel.register_module("scheduler", Scheduler(kernel))
    
    # 2. User Space Infrastructure
    kernel.register_module("users", UserManager(kernel))
    kernel.register_module("packager", PackageManager(kernel))
    
    # 3. IO / Desktop Services
    kernel.register_module("clipboard", Clipboard(kernel))
    kernel.register_module("notifications", NotificationManager(kernel))
    kernel.register_module("view", ViewManager(kernel))
    
    # 4. Bridges / Drivers
    kernel.register_module("bridge", ThothBridge(kernel))
    kernel.register_module("interface", Interface(kernel, port=9999))
    kernel.register_module("xr_server", XRServer(kernel))
    
    kernel.log("Boot", "Kernel Services Loaded.")
