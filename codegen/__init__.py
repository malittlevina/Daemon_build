# codegen/__init__.py
"""
Code Generation Module
======================
Provides code generation, analysis, and self-evolution capabilities.

Components:
- SelfCoder: Original self-coding module
- SelfEvolutionEngine: Advanced self-improvement system
- CodeIntrospector: Code analysis and complexity measurement
- CodeGenerator: LLM-powered code generation

The daemon uses this module to:
- Analyze its own codebase
- Propose and apply improvements
- Generate new modules and functions
- Support multiple programming languages
"""

from .self_coder import SelfCoder

# Self-evolution system
from .self_evolution import (
    SelfEvolutionEngine,
    CodeIntrospector,
    CodeGenerator,
    CodeChange,
    CodeAnalysis,
    ChangeType,
    RiskLevel,
    Language,
    get_evolution_engine,
    evolve,
)

__all__ = [
    # Original
    'SelfCoder',
    
    # Evolution
    'SelfEvolutionEngine',
    'CodeIntrospector',
    'CodeGenerator',
    'CodeChange',
    'CodeAnalysis',
    'ChangeType',
    'RiskLevel',
    'Language',
    'get_evolution_engine',
    'evolve',
]
