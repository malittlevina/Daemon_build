#!/usr/bin/env python3
"""
Kernel Test Suite - Verifies core kernel functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
from datetime import datetime


def test_message_bus():
    """Test the message bus pub/sub system."""
    print("\n=== Testing Message Bus ===")
    
    from kernel.message_bus import MessageBus, KernelMessage, MessagePriority
    
    bus = MessageBus()
    bus.start()
    
    received_messages = []
    
    def handler(msg):
        received_messages.append(msg)
        print(f"  Received: {msg.topic} - {msg.payload}")
    
    # Test subscription
    bus.subscribe("test.topic", handler)
    bus.subscribe_pattern("test.*", handler)
    
    # Test publishing
    bus.publish_sync("test.topic", {"value": 1}, "test")
    bus.publish_sync("test.other", {"value": 2}, "test")
    
    time.sleep(0.5)  # Allow async processing
    
    assert len(received_messages) >= 2, f"Expected at least 2 messages, got {len(received_messages)}"
    print(f"  ✓ Received {len(received_messages)} messages")
    
    # Test stats
    stats = bus.get_stats()
    print(f"  Stats: {stats}")
    
    bus.stop()
    print("  ✓ Message bus test passed")


def test_scheduler():
    """Test the task scheduler."""
    print("\n=== Testing Scheduler ===")
    
    from kernel.scheduler import KernelScheduler, TaskPriority
    
    scheduler = KernelScheduler(max_workers=2)
    scheduler.start()
    
    results = []
    
    def task_func(value):
        results.append(value)
        return value * 2
    
    # Schedule tasks
    task_id = scheduler.schedule(
        lambda: task_func(10),
        name="test_task",
        priority=TaskPriority.HIGH
    )
    print(f"  Scheduled task: {task_id[:8]}...")
    
    # Schedule delayed task
    delayed_id = scheduler.schedule(
        lambda: task_func(20),
        name="delayed_task",
        delay_seconds=0.5
    )
    
    time.sleep(1.0)  # Wait for tasks
    
    assert 10 in results, "First task should have run"
    assert 20 in results, "Delayed task should have run"
    print(f"  ✓ Tasks completed: {results}")
    
    # Test stats
    stats = scheduler.get_stats()
    print(f"  Stats: {stats}")
    
    scheduler.stop()
    print("  ✓ Scheduler test passed")


def test_registry():
    """Test the module registry."""
    print("\n=== Testing Module Registry ===")
    
    from kernel.registry import ModuleRegistry, ModuleState
    
    registry = ModuleRegistry()
    
    # Create mock modules
    class MockModule:
        module_name = "mock_module"
        dependencies = []
        
        def initialize(self, kernel):
            print("  MockModule initialized")
            return True
        
        def start(self):
            return True
        
        def stop(self):
            return True
        
        def health_check(self):
            return {"status": "healthy"}
    
    class DependentModule:
        module_name = "dependent_module"
        dependencies = ["mock_module"]
        
        def initialize(self, kernel):
            print("  DependentModule initialized")
            return True
        
        def start(self):
            return True
        
        def stop(self):
            return True
        
        def health_check(self):
            return {"status": "healthy"}
    
    # Register modules
    registry.register(MockModule())
    registry.register(DependentModule())
    
    # Resolve dependencies
    order = registry.resolve_dependencies()
    print(f"  Initialization order: {order}")
    assert order.index("mock_module") < order.index("dependent_module"), "Dependencies should be ordered"
    
    # Initialize
    results = registry.initialize_all(None)
    print(f"  Initialization results: {results}")
    
    # Check health
    health = registry.health_check_all()
    print(f"  Health check: {health}")
    
    print("  ✓ Registry test passed")


def test_kernel_core():
    """Test the full kernel."""
    print("\n=== Testing Kernel Core ===")
    
    from kernel.kernel_core import ThothKernel
    
    kernel = ThothKernel()
    
    # Test boot
    success = kernel.boot()
    assert success, "Kernel boot should succeed"
    print("  ✓ Kernel booted")
    
    # Test state management
    kernel.set_state("test.value", 42)
    value = kernel.get_state("test.value")
    assert value == 42, f"State should be 42, got {value}"
    print("  ✓ State management works")
    
    # Test event publishing
    received = []
    kernel.subscribe("test.event", lambda m: received.append(m))
    kernel.publish("test.event", {"data": "hello"}, "test")
    
    time.sleep(0.3)
    assert len(received) > 0, "Should receive published event"
    print("  ✓ Event publishing works")
    
    # Test status
    status = kernel.get_status()
    print(f"  Kernel status: {status['state']}")
    
    # Test reflection
    reflection = kernel.reflect()
    print(f"  Reflection insights: {len(reflection.get('insights', []))}")
    
    # Test shutdown
    kernel.shutdown()
    print("  ✓ Kernel shutdown complete")
    
    print("  ✓ Kernel core test passed")


def test_unimind():
    """Test the Unimind reasoning engine."""
    print("\n=== Testing Unimind ===")
    
    from unimind.core import Unimind, CognitiveMode
    
    unimind = Unimind()
    
    # Test mode switching
    unimind.set_mode(CognitiveMode.CREATIVE)
    assert unimind.current_mode == CognitiveMode.CREATIVE
    print("  ✓ Mode switching works")
    
    # Test thinking
    result = unimind.think("What should I learn today?")
    print(f"  Think result: confidence={result.get('confidence', 0):.2f}")
    print(f"  Conclusion: {result.get('conclusion', '')[:100]}...")
    
    # Test reflection
    reflection = unimind.reflect()
    print(f"  Reflection: {len(reflection.get('insights', []))} insights")
    
    print("  ✓ Unimind test passed")


def test_lam_planner():
    """Test the LAM planner."""
    print("\n=== Testing LAM Planner ===")
    
    from lam.lam_planner import LAMPlanner
    
    planner = LAMPlanner()
    
    # Test plan creation
    plan = planner.create_plan("study python programming")
    print(f"  Created plan: {plan.plan_id}")
    print(f"  Actions: {len(plan.actions)}")
    
    for action in plan.actions:
        print(f"    - {action.name}: {action.description[:50]}...")
    
    # Test quick action planning
    action = planner.plan_next_action("help me learn about AI", {})
    print(f"  Quick action: {action}")
    
    print("  ✓ LAM Planner test passed")


def test_symbolic_state():
    """Test the symbolic state system."""
    print("\n=== Testing Symbolic State ===")
    
    from lam.symbolic_state import (
        get_current_state, update_state_with_input, 
        get_context, get_flags, set_goal
    )
    
    # Test state update
    result = update_state_with_input("learn about machine learning")
    print(f"  Update result: {result}")
    
    # Check context
    context = get_context()
    print(f"  Context mode: {context.get('mode')}")
    
    # Check flags
    flags = get_flags()
    print(f"  Flags: {flags}")
    
    # Test goals
    set_goal("Master Python", priority=1)
    state = get_current_state()
    goals = state.get("goals", {}).get("active", [])
    print(f"  Active goals: {len(goals)}")
    
    print("  ✓ Symbolic state test passed")


def test_thoth_bridge():
    """Test the ThothBridge."""
    print("\n=== Testing ThothBridge ===")
    
    from bridge.thoth_bridge import ThothBridge
    
    bridge = ThothBridge()
    
    # Test app registration
    def test_app(payload):
        return f"Processed: {payload}"
    
    bridge.register_app("test_app", test_app)
    
    # Test app invocation
    result = bridge.invoke_app("test_app", {"value": 42})
    print(f"  App result: {result}")
    
    # Test status
    status = bridge.receive_status()
    print(f"  Bridge status: {status.get('status')}")
    
    # Test command
    cmd_id = bridge.send_command("test_command", {"param": "value"})
    print(f"  Command sent: {cmd_id[:8]}...")
    
    print("  ✓ ThothBridge test passed")


def test_symbolic_reasoner():
    """Test the symbolic reasoner."""
    print("\n=== Testing Symbolic Reasoner ===")
    
    from unimind.reasoner import symbolic_reasoning_chain, add_knowledge, explain_last_reasoning
    
    # Add some knowledge
    add_knowledge("Python is a programming language")
    add_knowledge("Machine learning requires data")
    
    # Test reasoning
    result = symbolic_reasoning_chain("How do I learn Python for machine learning?")
    print(f"  Reasoning steps: {result.get('steps')}")
    print(f"  Confidence: {result.get('confidence', 0):.2f}")
    print(f"  Conclusion: {result.get('conclusion', '')[:100]}...")
    
    # Test explanation
    explanation = explain_last_reasoning()
    print(f"  Explanation preview: {explanation[:200]}...")
    
    print("  ✓ Symbolic reasoner test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("  ThothOS Kernel Test Suite")
    print("=" * 60)
    
    tests = [
        ("Message Bus", test_message_bus),
        ("Scheduler", test_scheduler),
        ("Registry", test_registry),
        ("Kernel Core", test_kernel_core),
        ("Unimind", test_unimind),
        ("LAM Planner", test_lam_planner),
        ("Symbolic State", test_symbolic_state),
        ("ThothBridge", test_thoth_bridge),
        ("Symbolic Reasoner", test_symbolic_reasoner),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n  ✗ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
