#!/usr/bin/env python3
"""
Comprehensive Test Suite for All Priority Implementations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from datetime import datetime


def test_priority_2_cognitive():
    """Test Priority 2: Cognitive Enhancement."""
    print("\n=== Testing Priority 2: Cognitive Enhancement ===")
    
    # Test cognitive modules
    from unimind.modules.logic_module import LogicModule
    from unimind.modules.emotion_module import EmotionModule
    from unimind.modules.memory_module import MemoryModule
    from unimind.modules.intuition_module import IntuitionModule
    from unimind.modules.ethics_module import EthicsModule
    
    logic = LogicModule()
    emotion = EmotionModule()
    memory = MemoryModule()
    intuition = IntuitionModule()
    ethics = EthicsModule()
    
    print("  ✓ All cognitive modules initialized")
    
    # Test logic module
    logic.add_knowledge("Python is a programming language")
    result = logic.reason_syllogistically(
        "All programming languages have syntax",
        "Python is a programming language"
    )
    print(f"  ✓ Logic syllogism: {result}")
    
    # Test emotion module
    from unimind.modules.emotion_module import EmotionType
    emotion._detect_emotions("I am so happy today!")
    state = emotion.get_current_state()
    print(f"  ✓ Emotion detection: {state['primary_emotion']}")
    
    # Test attention system
    from unimind.attention import AttentionManager, AttentionMode
    attention = AttentionManager()
    attention.add_target("task1", "Important task", salience=0.8)
    attention.attend("task1")
    state = attention.get_state()
    print(f"  ✓ Attention system: {state['mode']}, {len(state['active_targets'])} targets")
    
    # Test metacognition
    from unimind.metacognition import MetacognitiveMonitor, StrategyType
    metacog = MetacognitiveMonitor()
    strategy, conf = metacog.select_strategy("analyze this problem step by step")
    print(f"  ✓ Metacognition strategy: {strategy.value} (conf: {conf:.2f})")
    
    print("  ✓ Priority 2 tests passed!")


def test_priority_3_memory():
    """Test Priority 3: Memory System."""
    print("\n=== Testing Priority 3: Memory System ===")
    
    from memory_tree.advanced_memory import AdvancedMemorySystem, MemoryType
    from memory_tree.semantic_index import SemanticIndex
    
    # Test advanced memory
    memory = AdvancedMemorySystem(storage_path="memory_tree/test_storage")
    
    # Test working memory
    mem_id = memory.attend("This is a test memory", importance=0.8)
    print(f"  ✓ Working memory: added {mem_id}")
    
    wm = memory.get_working_memory()
    print(f"  ✓ Working memory size: {len(wm)}")
    
    # Test episodic memory
    ep_id = memory.start_episode("Test Episode", participants=["user", "system"])
    memory.add_event_to_episode(ep_id, "Started conversation")
    memory.add_event_to_episode(ep_id, "User asked question")
    episode = memory.end_episode(ep_id)
    print(f"  ✓ Episodic memory: {len(episode.events)} events")
    
    # Test semantic memory
    concept_id = memory.store_concept(
        "Python",
        "A high-level programming language",
        "programming",
        related=["programming", "coding"]
    )
    print(f"  ✓ Semantic memory: stored concept {concept_id}")
    
    # Test semantic index
    index = SemanticIndex(storage_path="memory_tree/test_index")
    index.add_document("doc1", "Python is a programming language used for AI")
    index.add_document("doc2", "Machine learning requires data and algorithms")
    
    results = index.search("programming AI", limit=2)
    print(f"  ✓ Semantic search: {len(results)} results")
    
    stats = memory.get_stats()
    print(f"  ✓ Memory stats: {stats['total_indexed_memories']} indexed")
    
    print("  ✓ Priority 3 tests passed!")


def test_priority_4_integration():
    """Test Priority 4: Integration Layer."""
    print("\n=== Testing Priority 4: Integration Layer ===")
    
    # Test LLM providers
    from interop.llm_providers import (
        OllamaProvider, OpenAIProvider, LLMRouter,
        CompletionRequest, Message
    )
    
    router = LLMRouter()
    
    # Register Ollama provider
    ollama = OllamaProvider({"default_model": "llama3"})
    router.register_provider("ollama", ollama, is_default=True)
    print(f"  ✓ LLM Router: registered {len(router.providers)} providers")
    
    providers = router.list_providers()
    print(f"  ✓ Available providers: {[p['name'] for p in providers]}")
    
    # Test tool framework
    from interop.tool_framework import ToolRegistry, Tool, execute_tool
    
    registry = ToolRegistry()
    
    @Tool(name="greet", description="Greet someone", category="social")
    def greet(name: str) -> str:
        return f"Hello, {name}!"
    
    registry.register(greet)
    print(f"  ✓ Tool registry: {len(registry.list_tools())} tools")
    
    result = execute_tool("greet", {"name": "World"})
    print(f"  ✓ Tool execution: {result.result}")
    
    schemas = registry.get_schemas(format="openai")
    print(f"  ✓ Tool schemas: {len(schemas)} OpenAI-compatible")
    
    # Test API server (just initialization)
    from interop.api_server import APIServer
    server = APIServer(port=8081)  # Don't actually start
    print(f"  ✓ API Server initialized on port {server.port}")
    
    print("  ✓ Priority 4 tests passed!")


def test_priority_5_evolution():
    """Test Priority 5: Self-Improvement."""
    print("\n=== Testing Priority 5: Self-Improvement ===")
    
    # Test code analyzer
    from guardian.code_analyzer import CodeAnalyzer, IssueType, Severity
    
    analyzer = CodeAnalyzer()
    
    # Analyze a simple code string
    test_code = '''
def complex_function(a, b, c, d, e, f):
    """A test function."""
    if a > b:
        if c > d:
            if e > f:
                return True
    return False

class TestClass:
    def method_one(self):
        pass
    
    def method_two(self):
        pass
'''
    
    metrics = analyzer.analyze_source(test_code, "test.py")
    print(f"  ✓ Code analysis: {len(metrics.functions)} functions, {len(metrics.classes)} classes")
    print(f"  ✓ Complexity score: {metrics.complexity_score:.2f}")
    
    issues = analyzer.get_issues()
    print(f"  ✓ Detected issues: {len(issues)}")
    
    summary = analyzer.get_summary()
    print(f"  ✓ Analysis summary: {summary['total_functions']} functions analyzed")
    
    # Test test generator
    from guardian.test_generator import TestGenerator
    
    generator = TestGenerator()
    # Can't test file generation without a real file, but test initialization
    print("  ✓ Test generator initialized")
    
    # Test learning engine
    from guardian.learning_engine import LearningEngine, FeedbackType
    
    learner = LearningEngine(storage_path="logs/test_learning")
    
    # Record some experiences
    exp_id = learner.record_experience(
        context={"mode": "learning", "topic": "python"},
        action="explain_concept",
        result="User understood",
        reward=1.0
    )
    print(f"  ✓ Learning engine: recorded experience {exp_id}")
    
    learner.add_feedback(exp_id, FeedbackType.POSITIVE)
    print("  ✓ Feedback recorded")
    
    learner.practice_skill("explanation", success=True)
    learner.practice_skill("explanation", success=True)
    skill_level = learner.get_skill_level("explanation")
    print(f"  ✓ Skill learning: 'explanation' at {skill_level:.0%}")
    
    learner.observe_preference("verbosity", "response", "detailed", confidence=0.8)
    pref, conf = learner.get_preference("verbosity", "response")
    print(f"  ✓ Preference learning: verbosity={pref} (conf: {conf:.2f})")
    
    report = learner.get_learning_report()
    print(f"  ✓ Learning report: {report['total_experiences']} experiences")
    
    print("  ✓ Priority 5 tests passed!")


def test_integrated_system():
    """Test the full integrated system."""
    print("\n=== Testing Integrated System ===")
    
    from kernel.kernel_core import ThothKernel
    from unimind.core import Unimind
    from lam.lam_planner import LAMPlanner
    
    # Boot kernel
    kernel = ThothKernel()
    
    # Register core modules
    unimind = Unimind()
    planner = LAMPlanner()
    
    kernel.register_module(unimind, "unimind")
    kernel.register_module(planner, "lam_planner")
    
    # Boot
    kernel.boot()
    print("  ✓ Kernel booted with cognitive modules")
    
    # Test thinking with enhanced Unimind
    result = unimind.think("How can I learn Python effectively?")
    print(f"  ✓ Unimind thinking: confidence={result['confidence']:.2f}")
    if result.get('metacognition'):
        print(f"    Metacog checkpoints: {len(result['metacognition'].get('checkpoints', []))}")
    
    # Test planning
    plan = planner.create_plan("study python programming")
    print(f"  ✓ LAM planning: {len(plan.actions)} actions")
    
    # Test kernel state
    status = kernel.get_status()
    print(f"  ✓ Kernel status: {status['state']}, {len(status['modules'])} modules")
    
    # Shutdown
    kernel.shutdown()
    print("  ✓ Kernel shutdown complete")
    
    print("  ✓ Integrated system tests passed!")


def run_all_tests():
    """Run all priority tests."""
    print("=" * 70)
    print("  ThothOS Full Priority Test Suite")
    print("  Testing Priorities 2-5 Implementations")
    print("=" * 70)
    
    tests = [
        ("Priority 2: Cognitive Enhancement", test_priority_2_cognitive),
        ("Priority 3: Memory System", test_priority_3_memory),
        ("Priority 4: Integration Layer", test_priority_4_integration),
        ("Priority 5: Self-Improvement", test_priority_5_evolution),
        ("Integrated System", test_integrated_system),
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
    
    print("\n" + "=" * 70)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
