import unittest
import sys
import os

# Add workspace root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.kernel import Kernel
from core.module import Module
from core.event_bus import EventBus

class TestModule(Module):
    def __init__(self, kernel):
        super().__init__(kernel)
        self.initialized = False
        self.started = False
        self.stopped = False
        self.received_events = []

    def initialize(self):
        self.initialized = True
        self.kernel.events.subscribe("test_event", self.handle_event)

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def handle_event(self, event_type, data):
        self.received_events.append((event_type, data))

class TestKernelIntegration(unittest.TestCase):
    def setUp(self):
        self.kernel = Kernel()
        self.test_module = TestModule(self.kernel)
        self.kernel.register_module("test", self.test_module)

    def test_lifecycle(self):
        # Test Initialize
        self.assertFalse(self.test_module.initialized)
        self.kernel.initialize()
        self.assertTrue(self.test_module.initialized)

        # Test Start
        self.assertFalse(self.test_module.started)
        self.kernel.start()
        self.assertTrue(self.test_module.started)

        # Test Event Dispatch
        test_data = {"foo": "bar"}
        self.kernel.dispatch("test_event", test_data)
        self.assertEqual(len(self.test_module.received_events), 1)
        self.assertEqual(self.test_module.received_events[0][0], "test_event")
        self.assertEqual(self.test_module.received_events[0][1], test_data)

        # Test Stop
        self.assertFalse(self.test_module.stopped)
        self.kernel.stop()
        self.assertTrue(self.test_module.stopped)

    def test_module_registry(self):
        retrieved = self.kernel.get_module("test")
        self.assertEqual(retrieved, self.test_module)
        self.assertIsNone(self.kernel.get_module("non_existent"))

class TestRealModulesSmoke(unittest.TestCase):
    """Smoke test to ensure real modules can at least be instantiated and registered."""
    def setUp(self):
        self.kernel = Kernel()

    def test_unimind_init(self):
        from unimind.core import Unimind
        u = Unimind(self.kernel)
        self.kernel.register_module("unimind", u)
        self.kernel.initialize()
        # Should not crash

    def test_nlu_init(self):
        from nlu.nlu_engine import NLUEngine
        n = NLUEngine(self.kernel)
        self.kernel.register_module("nlu", n)
        self.kernel.initialize()
        # Should not crash

    def test_emotion_init(self):
        from emotion.emotion_engine import EmotionEngine
        e = EmotionEngine(self.kernel)
        self.kernel.register_module("emotion", e)
        self.kernel.initialize()

if __name__ == "__main__":
    unittest.main()
