# storyrealms/__init__.py
"""
Story Realms World Engine

A comprehensive AI-native world simulation system for the Daemon.

Core Components:
- WorldEngine: Central orchestrator for world simulation
- EntityManager: Manages NPCs, players, objects, locations
- NarrativeEngine: Story arcs, quests, dialog systems
- WorldRules: Laws, physics, magic systems
- ProceduralGenerator: Dynamic content generation
- WorldStateManager: Persistence and state management

Usage:
    from storyrealms import WorldEngine, WorldConfig
    
    config = WorldConfig(name="my_realm", seed=42)
    engine = WorldEngine(config)
    engine.initialize()
    
    # Spawn an NPC
    npc = engine.entity_manager.spawn(
        name="Aldric",
        entity_type="npc",
        personality={"primary_trait": "wise"}
    )
    
    # Run simulation
    engine.tick(1.0)

For Daemon integration:
    from storyrealms import StoryRealmsBridge
    
    bridge = StoryRealmsBridge()
    bridge.create_realm("adventure_realm")
    bridge.enter_realm("adventure_realm")
"""

# Core World Engine
from storyrealms.world_engine import (
    WorldEngine,
    WorldConfig,
    WorldEngineState
)

# Entity System
from storyrealms.entity_system import (
    Entity,
    EntityType,
    EntityState,
    EntityManager,
    EntityComponent
)

# Narrative Engine
from storyrealms.narrative_engine import (
    Narrative,
    NarrativeType,
    NarrativeState,
    NarrativeNode,
    NarrativeEngine
)

# World Rules
from storyrealms.world_rules import (
    Rule,
    RuleCategory,
    RulePriority,
    WorldRules
)

# State Management
from storyrealms.world_state import (
    WorldStateManager,
    WorldSnapshot
)

# Procedural Generation
from storyrealms.procedural_gen import (
    ProceduralGenerator,
    GenerationType,
    GenerationTemplate
)

# Bridge and Integration
from storyrealms.storyrealm_bridge import (
    StoryRealmsBridge,
    enter_storyrealm,
    get_current_realm,
    push_event_to_realm,
    list_realm_events
)

from storyrealms.daemon_integration import (
    DaemonIntegration,
    get_daemon_integration,
    setup_full_integration
)


__version__ = "1.0.0"
__all__ = [
    # Core
    "WorldEngine",
    "WorldConfig",
    "WorldEngineState",
    
    # Entities
    "Entity",
    "EntityType",
    "EntityState",
    "EntityManager",
    "EntityComponent",
    
    # Narratives
    "Narrative",
    "NarrativeType",
    "NarrativeState",
    "NarrativeNode",
    "NarrativeEngine",
    
    # Rules
    "Rule",
    "RuleCategory",
    "RulePriority",
    "WorldRules",
    
    # State
    "WorldStateManager",
    "WorldSnapshot",
    
    # Procedural
    "ProceduralGenerator",
    "GenerationType",
    "GenerationTemplate",
    
    # Bridge
    "StoryRealmsBridge",
    "enter_storyrealm",
    "get_current_realm",
    "push_event_to_realm",
    "list_realm_events",
    
    # Integration
    "DaemonIntegration",
    "get_daemon_integration",
    "setup_full_integration"
]
