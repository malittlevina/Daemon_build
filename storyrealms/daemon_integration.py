# storyrealms/daemon_integration.py
"""
Story Realms Daemon Integration

Connects the Story Realms World Engine with all Daemon subsystems:
- Scroll Engine: Trigger scrolls based on world events
- Memory Tree: Log world events as memories
- NLU Engine: Process natural language commands for world interaction
- Prometheus/AI: Use AI for narrative generation and NPC behavior
"""

from typing import Dict, List, Optional, Any


class DaemonIntegration:
    """
    Integration layer connecting Story Realms to Daemon subsystems.
    
    This enables:
    - Scroll triggers from world events
    - Memory logging of world history
    - Natural language world interaction
    - AI-driven narrative and behavior
    """
    
    def __init__(self):
        self._scroll_engine = None
        self._memory_interface = None
        self._nlu_engine = None
        self._personality = None
        
        # Scroll mappings: world_event -> scroll_name
        self.scroll_mappings: Dict[str, str] = {}
        
        # NLU command patterns for world interaction
        self.nlu_patterns: List[Dict] = []
        
        print("[DaemonIntegration] Initialized")
    
    # ─────────────────────────────────────────────────────────────────
    # SUBSYSTEM CONNECTIONS
    # ─────────────────────────────────────────────────────────────────
    
    def connect_scroll_engine(self, scroll_engine):
        """Connect to the Scroll Engine for trigger-based automation."""
        self._scroll_engine = scroll_engine
        self._register_scroll_mappings()
        print("[DaemonIntegration] Connected to Scroll Engine")
    
    def connect_memory_interface(self, memory_interface):
        """Connect to the Memory Tree for world history logging."""
        self._memory_interface = memory_interface
        print("[DaemonIntegration] Connected to Memory Tree")
    
    def connect_nlu_engine(self, nlu_engine):
        """Connect to the NLU Engine for natural language processing."""
        self._nlu_engine = nlu_engine
        self._register_nlu_patterns()
        print("[DaemonIntegration] Connected to NLU Engine")
    
    def connect_personality(self, personality):
        """Connect to the Daemon's personality for AI behavior."""
        self._personality = personality
        print("[DaemonIntegration] Connected to Daemon personality")
    
    # ─────────────────────────────────────────────────────────────────
    # SCROLL ENGINE INTEGRATION
    # ─────────────────────────────────────────────────────────────────
    
    def _register_scroll_mappings(self):
        """Register world events that should trigger scrolls."""
        self.scroll_mappings = {
            "entity_spawned": "on_entity_spawn",
            "entity_death": "on_entity_death",
            "narrative_completed": "on_quest_complete",
            "procedural_event": "on_world_event",
            "entity_interaction": "on_interaction"
        }
    
    def trigger_scroll_for_event(self, event_type: str, event_data: Dict):
        """Trigger a scroll based on a world event."""
        if not self._scroll_engine:
            return
        
        scroll_name = self.scroll_mappings.get(event_type)
        if scroll_name:
            # Check if scroll exists
            if scroll_name in self._scroll_engine.scrolls:
                try:
                    self._scroll_engine.invoke(scroll_name, event_data)
                    print(f"[DaemonIntegration] Triggered scroll: {scroll_name}")
                except Exception as e:
                    print(f"[DaemonIntegration] Scroll trigger failed: {e}")
    
    def register_world_scroll(self, event_type: str, scroll_name: str):
        """Register a custom scroll trigger for a world event."""
        self.scroll_mappings[event_type] = scroll_name
    
    # ─────────────────────────────────────────────────────────────────
    # MEMORY TREE INTEGRATION
    # ─────────────────────────────────────────────────────────────────
    
    def log_world_event(self, event_type: str, event_data: Dict):
        """Log a world event to the Memory Tree."""
        if not self._memory_interface:
            return
        
        # Create memory content based on event type
        content = self._format_event_for_memory(event_type, event_data)
        
        # Determine tags
        tags = ["storyrealms", "world_event", event_type]
        
        # Add entity-specific tags
        if "entity_id" in event_data:
            tags.append(f"entity:{event_data['entity_id'][:8]}")
        if "narrative_id" in event_data:
            tags.append(f"narrative:{event_data['narrative_id'][:8]}")
        
        self._memory_interface.plant_memory_seed(
            content=content,
            tags=tags,
            context="storyrealms_world_engine"
        )
    
    def _format_event_for_memory(self, event_type: str, event_data: Dict) -> str:
        """Format a world event for memory storage."""
        formatters = {
            "entity_spawned": lambda d: f"New entity spawned: {d.get('name', 'Unknown')} ({d.get('type', 'unknown')})",
            "entity_death": lambda d: f"Entity died: {d.get('entity_id', 'Unknown')} - Cause: {d.get('cause', 'unknown')}",
            "entity_moved": lambda d: f"Entity moved from {d.get('from', 'unknown')} to {d.get('to', 'unknown')}",
            "narrative_triggered": lambda d: f"Story began: {d.get('title', 'Unknown')} ({d.get('type', 'unknown')})",
            "narrative_completed": lambda d: f"Story ended: {d.get('title', 'Unknown')} - Result: {d.get('reason', 'completed')}",
            "entity_interaction": lambda d: f"Interaction: {d.get('type', 'unknown')} between entities",
            "procedural_event": lambda d: f"World event: {d.get('event_type', 'unknown')} occurred",
            "world_initialized": lambda d: f"Realm initialized: {d.get('realm', 'unknown')}",
            "new_day": lambda d: f"New day dawned: Day {d.get('day', 1)}",
            "weather_changed": lambda d: f"Weather changed from {d.get('from', 'unknown')} to {d.get('to', 'unknown')}"
        }
        
        formatter = formatters.get(event_type, lambda d: f"Event: {event_type} - {d}")
        return formatter(event_data)
    
    def get_world_memories(self, query: str = None, limit: int = 10) -> List[Dict]:
        """Retrieve world-related memories."""
        if not self._memory_interface:
            return []
        
        all_memories = self._memory_interface.fetch_memories(query or "storyrealms")
        
        # Filter to storyrealms memories
        world_memories = [m for m in all_memories if "storyrealms" in str(m)]
        
        return world_memories[:limit]
    
    # ─────────────────────────────────────────────────────────────────
    # NLU ENGINE INTEGRATION
    # ─────────────────────────────────────────────────────────────────
    
    def _register_nlu_patterns(self):
        """Register NLU patterns for world commands."""
        self.nlu_patterns = [
            {
                "patterns": ["enter realm", "go to realm", "enter world"],
                "action": "enter_realm",
                "extract": ["realm_name"]
            },
            {
                "patterns": ["spawn", "create entity", "add npc"],
                "action": "spawn_entity",
                "extract": ["entity_name", "entity_type"]
            },
            {
                "patterns": ["start quest", "begin quest", "new quest"],
                "action": "trigger_quest",
                "extract": ["quest_title"]
            },
            {
                "patterns": ["talk to", "speak with", "dialog with"],
                "action": "start_dialog",
                "extract": ["npc_name"]
            },
            {
                "patterns": ["advance time", "pass time", "wait"],
                "action": "advance_time",
                "extract": ["duration"]
            },
            {
                "patterns": ["world status", "realm status", "where am i"],
                "action": "query_state",
                "extract": []
            },
            {
                "patterns": ["generate npc", "create character", "new villager"],
                "action": "generate_npc",
                "extract": ["role"]
            },
            {
                "patterns": ["generate location", "create place", "new area"],
                "action": "generate_location",
                "extract": ["location_type"]
            }
        ]
    
    def interpret_world_command(self, user_input: str) -> Optional[Dict]:
        """
        Interpret natural language input as a world command.
        
        Returns a command dict if matched, None otherwise.
        """
        input_lower = user_input.lower()
        
        for pattern_def in self.nlu_patterns:
            for pattern in pattern_def["patterns"]:
                if pattern in input_lower:
                    return {
                        "action": pattern_def["action"],
                        "input": user_input,
                        "extracted": self._extract_parameters(user_input, pattern_def["extract"])
                    }
        
        return None
    
    def _extract_parameters(self, input_text: str, param_names: List[str]) -> Dict:
        """Extract parameters from natural language input."""
        # Simple extraction - in production, use NLU engine
        extracted = {}
        words = input_text.split()
        
        for param in param_names:
            if param == "realm_name" and len(words) > 2:
                extracted["realm_name"] = words[-1]
            elif param == "entity_name" and len(words) > 1:
                extracted["entity_name"] = words[-1]
            elif param == "npc_name" and len(words) > 2:
                extracted["npc_name"] = words[-1]
        
        return extracted
    
    def process_user_input(self, user_input: str, realm_interface) -> Optional[Dict]:
        """
        Process user input and execute world commands if matched.
        
        Args:
            user_input: The natural language input
            realm_interface: The RealmInterface to execute commands on
            
        Returns:
            Command result if a world command was recognized, None otherwise
        """
        command = self.interpret_world_command(user_input)
        if not command:
            return None
        
        action = command["action"]
        extracted = command["extracted"]
        
        # Execute the appropriate action
        if action == "enter_realm":
            realm_name = extracted.get("realm_name", "default")
            return realm_interface.enter_realm(realm_name)
        
        elif action == "spawn_entity":
            return realm_interface.spawn_entity(
                name=extracted.get("entity_name", "Unknown"),
                entity_type=extracted.get("entity_type", "npc")
            )
        
        elif action == "query_state":
            return realm_interface.get_current_state()
        
        elif action == "advance_time":
            return realm_interface.tick()
        
        elif action == "generate_npc":
            return realm_interface.generate_npc(role=extracted.get("role"))
        
        elif action == "generate_location":
            return realm_interface.generate_location(location_type=extracted.get("location_type"))
        
        return None
    
    # ─────────────────────────────────────────────────────────────────
    # AI/PERSONALITY INTEGRATION
    # ─────────────────────────────────────────────────────────────────
    
    def generate_npc_dialog(self, npc_personality: Dict, context: Dict) -> str:
        """Use the Daemon's AI to generate NPC dialog."""
        if not self._personality:
            return self._fallback_dialog(npc_personality)
        
        # Build prompt for AI
        prompt = self._build_dialog_prompt(npc_personality, context)
        
        try:
            # Use personality's response generation
            response = self._personality.respond(prompt)
            return response
        except Exception as e:
            print(f"[DaemonIntegration] AI dialog generation failed: {e}")
            return self._fallback_dialog(npc_personality)
    
    def _build_dialog_prompt(self, npc_personality: Dict, context: Dict) -> str:
        """Build a prompt for AI dialog generation."""
        return f"""You are an NPC with these traits:
- Primary trait: {npc_personality.get('primary_trait', 'neutral')}
- Speech style: {npc_personality.get('speech_style', 'casual')}
- Motivation: {npc_personality.get('motivation', 'none')}

Current context: {context.get('situation', 'general conversation')}
Player said: {context.get('player_input', 'Hello')}

Respond in character:"""
    
    def _fallback_dialog(self, npc_personality: Dict) -> str:
        """Generate fallback dialog without AI."""
        greetings = {
            "formal": "Good day to you, traveler. How may I be of service?",
            "casual": "Hey there! What's going on?",
            "gruff": "What do you want?",
            "poetic": "Ah, a visitor graces us with their presence...",
            "terse": "Speak."
        }
        style = npc_personality.get("speech_style", "casual")
        return greetings.get(style, "Hello.")
    
    def suggest_narrative(self, world_state: Dict) -> Optional[Dict]:
        """Use AI to suggest a new narrative based on world state."""
        if not self._personality:
            return None
        
        # Analyze world state for narrative opportunities
        prompt = f"""Based on this world state, suggest a new quest or story:
- World time: {world_state.get('world_time', 0)}
- Entity count: {world_state.get('entity_count', 0)}
- Recent events: {world_state.get('recent_events', [])}

Suggest a quest with: title, description, objectives"""
        
        try:
            suggestion = self._personality.respond(prompt)
            return {"type": "narrative_suggestion", "content": suggestion}
        except Exception:
            return None


# Singleton instance
_integration = None

def get_daemon_integration() -> DaemonIntegration:
    """Get or create the daemon integration singleton."""
    global _integration
    if _integration is None:
        _integration = DaemonIntegration()
    return _integration


def setup_full_integration(scroll_engine=None, memory_interface=None, nlu_engine=None, personality=None):
    """
    Set up full integration with all Daemon subsystems.
    
    Call this during Daemon initialization to connect Story Realms
    to all available subsystems.
    """
    integration = get_daemon_integration()
    
    if scroll_engine:
        integration.connect_scroll_engine(scroll_engine)
    
    if memory_interface:
        integration.connect_memory_interface(memory_interface)
    
    if nlu_engine:
        integration.connect_nlu_engine(nlu_engine)
    
    if personality:
        integration.connect_personality(personality)
    
    print("[DaemonIntegration] Full integration setup complete")
    return integration
