# Daemon Intelligence & Apps
from unimind.core import Unimind
from nlu.nlu_engine import NLUEngine
from introspection.personality_tracker import PersonalityTracker
from emotion.emotion_engine import EmotionEngine
from memory_tree.memory_logger import MemoryLogger
from memory_tree.graph import KnowledgeGraph
from prometheus.specialties import PrometheusSpecialties
from guardian.ethical_core import Guardian
from core.homeostasis import Homeostasis
from core.dreamer import Dreamer
from core.shell import Shell
from lam.symbolic_state import SymbolicLayer
from daemon.state_manager import StateManager

# Subsystems / Heavy Modules
from scrolls.scroll_engine import ScrollEngine
from rituals.ritual_registry import RitualRegistry
from world_engine.world import WorldEngine
from world_engine.spatial_map import SpatialMap

# Applications
from apps.browser import Browser
from apps.ide import IDE
from apps.calculator import Calculator
from apps.holodeck import Holodeck
from apps.bard import Bard
from apps.architect import Architect
from apps.sims import SimController

# Services
from optimizer.service import OptimizerService
from voice.service import VoiceService

def load_daemon_services(kernel):
    """
    Registers the High-Level AI and Application layers.
    These constitute the "Thoth" identity.
    """
    kernel.log("Boot", "Loading Daemon Intelligence...")

    # 1. The Mind (Cognitive Stack)
    kernel.register_module("unimind", Unimind(kernel))
    kernel.register_module("nlu", NLUEngine(kernel))
    kernel.register_module("personality", PersonalityTracker(kernel))
    kernel.register_module("emotion", EmotionEngine(kernel))
    kernel.register_module("guardian", Guardian(kernel)) # Ethics
    kernel.register_module("symbolic", SymbolicLayer(kernel))
    kernel.register_module("prometheus", PrometheusSpecialties(kernel))
    kernel.register_module("state", StateManager(kernel))

    # 2. Memory Systems
    kernel.register_module("memory", MemoryLogger(kernel))
    kernel.register_module("knowledge_graph", KnowledgeGraph(kernel))

    # 3. Action / Execution
    kernel.register_module("scrolls", ScrollEngine(kernel))
    kernel.register_module("rituals", RitualRegistry(kernel))
    
    # 4. Simulation & World
    kernel.register_module("world", WorldEngine(kernel))
    kernel.register_module("spatial_map", SpatialMap(kernel))
    
    # 5. Meta-Cognition (Background Processes)
    kernel.register_module("homeostasis", Homeostasis(kernel))
    kernel.register_module("dreamer", Dreamer(kernel))
    kernel.register_module("optimizer", OptimizerService(kernel))
    kernel.register_module("voice", VoiceService(kernel))

    # 6. Applications (User Tools)
    kernel.register_module("shell", Shell(kernel)) # CLI
    kernel.register_module("browser", Browser(kernel))
    kernel.register_module("ide", IDE(kernel))
    kernel.register_module("calculator", Calculator(kernel))
    kernel.register_module("holodeck", Holodeck(kernel))
    kernel.register_module("bard", Bard(kernel))
    kernel.register_module("architect", Architect(kernel))
    kernel.register_module("sims", SimController(kernel))

    kernel.log("Boot", "Daemon Intelligence Loaded.")
