# storyrealms/narrative_engine.py
"""
Story Realms Narrative Engine

Manages story arcs, quests, dialog trees, and narrative progression.
AI-native design for dynamic storytelling driven by intelligent agents.
"""

import uuid
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum


class NarrativeType(Enum):
    STORY_ARC = "story_arc"      # Major overarching narratives
    QUEST = "quest"              # Player-facing objectives
    SUBPLOT = "subplot"          # Background narrative threads
    DIALOG = "dialog"            # Conversation sequences
    EVENT = "event"              # One-time narrative events
    RUMOR = "rumor"              # Spreading information through NPCs


class NarrativeState(Enum):
    DORMANT = "dormant"          # Not yet triggered
    ACTIVE = "active"            # Currently in progress
    PAUSED = "paused"            # Temporarily suspended
    COMPLETED = "completed"      # Successfully finished
    FAILED = "failed"            # Failed/abandoned
    BRANCHED = "branched"        # Split into multiple paths


@dataclass
class NarrativeNode:
    """A single node in a narrative graph."""
    id: str
    content: str                          # Text/description of this node
    node_type: str = "scene"              # scene, choice, condition, action
    choices: List[Dict] = field(default_factory=list)    # Available choices
    conditions: List[Dict] = field(default_factory=list) # Required conditions
    actions: List[Dict] = field(default_factory=list)    # Actions to execute
    next_nodes: List[str] = field(default_factory=list)  # Connected node IDs
    metadata: Dict = field(default_factory=dict)


@dataclass
class Narrative:
    """
    A narrative structure (story arc, quest, dialog, etc.)
    
    Uses a node-based graph for flexible branching narratives.
    """
    id: str
    title: str
    narrative_type: NarrativeType
    description: str = ""
    state: NarrativeState = NarrativeState.DORMANT
    
    # Node graph
    nodes: Dict[str, NarrativeNode] = field(default_factory=dict)
    start_node_id: Optional[str] = None
    current_node_id: Optional[str] = None
    
    # Participants
    participant_ids: Set[str] = field(default_factory=set)  # Entity IDs involved
    
    # Progress tracking
    completed_nodes: Set[str] = field(default_factory=set)
    choices_made: List[Dict] = field(default_factory=list)
    
    # Triggers and conditions
    trigger_conditions: List[Dict] = field(default_factory=list)
    completion_conditions: List[Dict] = field(default_factory=list)
    
    # Rewards and consequences
    rewards: List[Dict] = field(default_factory=list)
    consequences: List[Dict] = field(default_factory=list)
    
    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    time_limit: Optional[float] = None  # World time limit for completion
    
    # Metadata
    priority: int = 5  # 1 (low) to 10 (critical)
    tags: Set[str] = field(default_factory=set)
    
    def add_node(self, node: NarrativeNode):
        """Add a node to this narrative."""
        self.nodes[node.id] = node
        if not self.start_node_id:
            self.start_node_id = node.id
    
    def get_current_node(self) -> Optional[NarrativeNode]:
        """Get the current active node."""
        if self.current_node_id:
            return self.nodes.get(self.current_node_id)
        return None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["narrative_type"] = self.narrative_type.value
        data["state"] = self.state.value
        data["participant_ids"] = list(self.participant_ids)
        data["completed_nodes"] = list(self.completed_nodes)
        data["tags"] = list(self.tags)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Narrative':
        """Create from dictionary."""
        data["narrative_type"] = NarrativeType(data["narrative_type"])
        data["state"] = NarrativeState(data["state"])
        data["participant_ids"] = set(data.get("participant_ids", []))
        data["completed_nodes"] = set(data.get("completed_nodes", []))
        data["tags"] = set(data.get("tags", []))
        
        # Reconstruct nodes
        nodes = {}
        for node_id, node_data in data.get("nodes", {}).items():
            nodes[node_id] = NarrativeNode(**node_data)
        data["nodes"] = nodes
        
        return cls(**data)


class NarrativeEngine:
    """
    Manages narratives within the Story Realms world.
    
    Provides:
    - Narrative lifecycle (create, trigger, progress, complete)
    - Dynamic dialog generation
    - Quest tracking and completion
    - Story arc orchestration
    - Consequence propagation
    """
    
    def __init__(self, world_engine):
        self.world_engine = world_engine
        self.narratives: Dict[str, Narrative] = {}
        
        # Indices for quick lookup
        self.type_index: Dict[NarrativeType, Set[str]] = {}
        self.active_narratives: Set[str] = set()
        self.participant_index: Dict[str, Set[str]] = {}  # entity_id -> narrative_ids
        
        # Dialog state for ongoing conversations
        self.active_dialogs: Dict[str, Dict] = {}  # session_id -> dialog state
        
        print("[NarrativeEngine] Initialized")
    
    # ─────────────────────────────────────────────────────────────────
    # NARRATIVE CREATION
    # ─────────────────────────────────────────────────────────────────
    
    def create_narrative(
        self,
        title: str,
        narrative_type: NarrativeType | str,
        description: str = "",
        nodes: List[Dict] = None,
        trigger_conditions: List[Dict] = None,
        participants: List[str] = None,
        **kwargs
    ) -> Narrative:
        """
        Create a new narrative.
        
        Args:
            title: Display title for the narrative
            narrative_type: Type of narrative (quest, story_arc, etc.)
            description: Description text
            nodes: List of narrative nodes to add
            trigger_conditions: Conditions to auto-trigger this narrative
            participants: Entity IDs initially involved
        """
        if isinstance(narrative_type, str):
            narrative_type = NarrativeType(narrative_type.lower())
        
        narrative = Narrative(
            id=str(uuid.uuid4()),
            title=title,
            narrative_type=narrative_type,
            description=description,
            trigger_conditions=trigger_conditions or [],
            participant_ids=set(participants or []),
            **kwargs
        )
        
        # Add nodes
        if nodes:
            for i, node_data in enumerate(nodes):
                node = NarrativeNode(
                    id=node_data.get("id", f"node_{i}"),
                    content=node_data.get("content", ""),
                    node_type=node_data.get("node_type", "scene"),
                    choices=node_data.get("choices", []),
                    conditions=node_data.get("conditions", []),
                    actions=node_data.get("actions", []),
                    next_nodes=node_data.get("next_nodes", []),
                    metadata=node_data.get("metadata", {})
                )
                narrative.add_node(node)
        
        # Store and index
        self.narratives[narrative.id] = narrative
        self._index_narrative(narrative)
        
        print(f"[NarrativeEngine] Created {narrative_type.value}: {title}")
        return narrative
    
    def create_quest(
        self,
        title: str,
        description: str,
        objectives: List[Dict],
        rewards: List[Dict] = None,
        time_limit: float = None,
        **kwargs
    ) -> Narrative:
        """Convenience method for creating quest narratives."""
        # Convert objectives to nodes
        nodes = []
        for i, objective in enumerate(objectives):
            node = {
                "id": f"objective_{i}",
                "content": objective.get("description", "Complete objective"),
                "node_type": "objective",
                "conditions": objective.get("conditions", []),
                "actions": objective.get("actions", []),
                "next_nodes": [f"objective_{i+1}"] if i < len(objectives) - 1 else ["completion"]
            }
            nodes.append(node)
        
        # Add completion node
        nodes.append({
            "id": "completion",
            "content": "Quest completed!",
            "node_type": "completion",
            "actions": [{"type": "grant_rewards"}]
        })
        
        return self.create_narrative(
            title=title,
            narrative_type=NarrativeType.QUEST,
            description=description,
            nodes=nodes,
            rewards=rewards or [],
            time_limit=time_limit,
            **kwargs
        )
    
    def create_dialog(
        self,
        npc_id: str,
        dialog_tree: List[Dict],
        greeting: str = "Hello there.",
        **kwargs
    ) -> Narrative:
        """Create a dialog narrative for an NPC."""
        nodes = [
            {
                "id": "greeting",
                "content": greeting,
                "node_type": "dialog",
                "choices": [{"text": d.get("prompt", "..."), "next": d.get("id")} for d in dialog_tree],
                "next_nodes": [d.get("id") for d in dialog_tree]
            }
        ]
        
        for dialog in dialog_tree:
            nodes.append({
                "id": dialog.get("id"),
                "content": dialog.get("response", ""),
                "node_type": "dialog",
                "choices": dialog.get("choices", []),
                "next_nodes": dialog.get("next_nodes", ["greeting"]),
                "actions": dialog.get("actions", [])
            })
        
        return self.create_narrative(
            title=f"Dialog: {npc_id[:8]}",
            narrative_type=NarrativeType.DIALOG,
            nodes=nodes,
            participants=[npc_id],
            **kwargs
        )
    
    # ─────────────────────────────────────────────────────────────────
    # NARRATIVE LIFECYCLE
    # ─────────────────────────────────────────────────────────────────
    
    def trigger_arc(self, narrative_id: str = None, **kwargs) -> Dict:
        """Trigger a narrative to become active."""
        if narrative_id:
            narrative = self.narratives.get(narrative_id)
        else:
            # Create new narrative from kwargs
            narrative = self.create_narrative(**kwargs)
        
        if not narrative:
            return {"status": "error", "message": "Narrative not found"}
        
        if narrative.state == NarrativeState.ACTIVE:
            return {"status": "already_active", "narrative_id": narrative.id}
        
        narrative.state = NarrativeState.ACTIVE
        narrative.started_at = time.time()
        narrative.current_node_id = narrative.start_node_id
        
        self.active_narratives.add(narrative.id)
        
        self.world_engine._emit_event("narrative_triggered", {
            "narrative_id": narrative.id,
            "title": narrative.title,
            "type": narrative.narrative_type.value
        })
        
        print(f"[NarrativeEngine] Triggered: {narrative.title}")
        return {"status": "triggered", "narrative_id": narrative.id, "narrative": narrative.to_dict()}
    
    def progress_narrative(self, narrative_id: str, choice_id: str = None, force_node: str = None) -> Dict:
        """
        Progress a narrative to the next node.
        
        Args:
            narrative_id: The narrative to progress
            choice_id: ID of the choice made (for branching)
            force_node: Force progression to a specific node
        """
        narrative = self.narratives.get(narrative_id)
        if not narrative:
            return {"status": "error", "message": "Narrative not found"}
        
        if narrative.state != NarrativeState.ACTIVE:
            return {"status": "error", "message": f"Narrative is {narrative.state.value}"}
        
        current_node = narrative.get_current_node()
        if not current_node:
            return {"status": "error", "message": "No current node"}
        
        # Mark current node as completed
        narrative.completed_nodes.add(current_node.id)
        
        # Execute node actions
        self._execute_node_actions(narrative, current_node)
        
        # Determine next node
        next_node_id = None
        if force_node:
            next_node_id = force_node
        elif choice_id:
            # Find choice and record it
            for choice in current_node.choices:
                if choice.get("id") == choice_id or choice.get("text") == choice_id:
                    next_node_id = choice.get("next")
                    narrative.choices_made.append({
                        "node_id": current_node.id,
                        "choice": choice,
                        "timestamp": time.time()
                    })
                    break
        elif current_node.next_nodes:
            next_node_id = current_node.next_nodes[0]
        
        if next_node_id:
            if next_node_id in narrative.nodes:
                narrative.current_node_id = next_node_id
                new_node = narrative.nodes[next_node_id]
                
                # Check if this is a completion node
                if new_node.node_type == "completion":
                    return self.complete_narrative(narrative_id, "completed")
                
                return {
                    "status": "progressed",
                    "previous_node": current_node.id,
                    "current_node": next_node_id,
                    "content": new_node.content,
                    "choices": new_node.choices
                }
            else:
                # End of narrative branch
                return self.complete_narrative(narrative_id, "end_of_branch")
        
        return {"status": "no_progression", "current_node": current_node.id}
    
    def complete_narrative(self, narrative_id: str, reason: str = "completed") -> Dict:
        """Mark a narrative as completed."""
        narrative = self.narratives.get(narrative_id)
        if not narrative:
            return {"status": "error", "message": "Narrative not found"}
        
        narrative.state = NarrativeState.COMPLETED if reason == "completed" else NarrativeState.FAILED
        narrative.completed_at = time.time()
        
        self.active_narratives.discard(narrative_id)
        
        # Grant rewards if completed successfully
        if narrative.state == NarrativeState.COMPLETED:
            self._grant_rewards(narrative)
        
        # Apply consequences
        self._apply_consequences(narrative)
        
        self.world_engine._emit_event("narrative_completed", {
            "narrative_id": narrative_id,
            "title": narrative.title,
            "reason": reason,
            "state": narrative.state.value
        })
        
        print(f"[NarrativeEngine] Completed: {narrative.title} ({reason})")
        return {"status": narrative.state.value, "narrative_id": narrative_id}
    
    def progress_narratives(self, delta_time: float) -> Dict:
        """Progress all active narratives (called by world tick)."""
        progressed = 0
        expired = []
        
        for narrative_id in list(self.active_narratives):
            narrative = self.narratives.get(narrative_id)
            if not narrative:
                continue
            
            # Check time limits
            if narrative.time_limit and narrative.started_at:
                elapsed = self.world_engine.world_time - narrative.started_at
                if elapsed > narrative.time_limit:
                    expired.append(narrative_id)
                    continue
            
            # Check automatic progression conditions
            current_node = narrative.get_current_node()
            if current_node and current_node.conditions:
                if self._check_conditions(current_node.conditions):
                    self.progress_narrative(narrative_id)
                    progressed += 1
        
        # Handle expired narratives
        for narrative_id in expired:
            self.complete_narrative(narrative_id, "time_expired")
        
        return {"progressed": progressed, "expired": len(expired)}
    
    # ─────────────────────────────────────────────────────────────────
    # DIALOG SYSTEM
    # ─────────────────────────────────────────────────────────────────
    
    def start_dialog(self, speaker_id: str, listener_id: str, dialog_narrative_id: str = None) -> Dict:
        """Start a dialog session between two entities."""
        session_id = str(uuid.uuid4())
        
        # Find or create dialog narrative for this NPC
        if dialog_narrative_id:
            narrative = self.narratives.get(dialog_narrative_id)
        else:
            # Look for existing dialog for this speaker
            for nid in self.participant_index.get(speaker_id, []):
                n = self.narratives.get(nid)
                if n and n.narrative_type == NarrativeType.DIALOG:
                    narrative = n
                    break
            else:
                # Generate a default dialog
                narrative = self._generate_default_dialog(speaker_id)
        
        if not narrative:
            return {"status": "error", "message": "No dialog available"}
        
        # Create dialog session
        self.active_dialogs[session_id] = {
            "narrative_id": narrative.id,
            "speaker_id": speaker_id,
            "listener_id": listener_id,
            "current_node": narrative.start_node_id,
            "started_at": time.time(),
            "history": []
        }
        
        # Get opening node
        node = narrative.nodes.get(narrative.start_node_id)
        
        return {
            "status": "started",
            "session_id": session_id,
            "speaker": speaker_id,
            "content": node.content if node else "...",
            "choices": node.choices if node else []
        }
    
    def continue_dialog(self, session_id: str, choice_id: str) -> Dict:
        """Continue a dialog session with a choice."""
        session = self.active_dialogs.get(session_id)
        if not session:
            return {"status": "error", "message": "Dialog session not found"}
        
        narrative = self.narratives.get(session["narrative_id"])
        if not narrative:
            return {"status": "error", "message": "Dialog narrative not found"}
        
        current_node = narrative.nodes.get(session["current_node"])
        if not current_node:
            return {"status": "error", "message": "Current node not found"}
        
        # Find the chosen option
        next_node_id = None
        for choice in current_node.choices:
            if choice.get("id") == choice_id or choice.get("text") == choice_id:
                next_node_id = choice.get("next")
                session["history"].append({
                    "node": session["current_node"],
                    "choice": choice,
                    "timestamp": time.time()
                })
                break
        
        if not next_node_id:
            # Default to first next node
            next_node_id = current_node.next_nodes[0] if current_node.next_nodes else None
        
        if not next_node_id or next_node_id not in narrative.nodes:
            # End of dialog
            del self.active_dialogs[session_id]
            return {"status": "ended", "session_id": session_id}
        
        # Move to next node
        session["current_node"] = next_node_id
        next_node = narrative.nodes[next_node_id]
        
        # Execute any actions
        self._execute_node_actions(narrative, next_node)
        
        return {
            "status": "continued",
            "session_id": session_id,
            "content": next_node.content,
            "choices": next_node.choices
        }
    
    def end_dialog(self, session_id: str) -> Dict:
        """End a dialog session."""
        if session_id in self.active_dialogs:
            session = self.active_dialogs.pop(session_id)
            return {"status": "ended", "session_id": session_id, "history": session["history"]}
        return {"status": "not_found"}
    
    def _generate_default_dialog(self, speaker_id: str) -> Narrative:
        """Generate a default dialog for an NPC without defined dialog."""
        # Get speaker entity for context
        entity = None
        if self.world_engine._entity_manager:
            entity = self.world_engine._entity_manager.get(speaker_id)
        
        name = entity.name if entity else "Unknown"
        personality = entity.personality if entity else {}
        
        # Generate contextual greeting
        greeting = personality.get("greeting", f"Hello, I am {name}. How can I help you?")
        
        return self.create_dialog(
            npc_id=speaker_id,
            greeting=greeting,
            dialog_tree=[
                {
                    "id": "about",
                    "prompt": "Tell me about yourself.",
                    "response": personality.get("about", f"I'm {name}. That's all you need to know."),
                    "next_nodes": ["greeting"]
                },
                {
                    "id": "location",
                    "prompt": "What is this place?",
                    "response": personality.get("location_info", "This is where I live. Nothing special."),
                    "next_nodes": ["greeting"]
                },
                {
                    "id": "farewell",
                    "prompt": "Goodbye.",
                    "response": "Farewell, traveler.",
                    "next_nodes": []
                }
            ]
        )
    
    # ─────────────────────────────────────────────────────────────────
    # QUERY METHODS
    # ─────────────────────────────────────────────────────────────────
    
    def get(self, narrative_id: str) -> Optional[Narrative]:
        """Get a narrative by ID."""
        return self.narratives.get(narrative_id)
    
    def get_active(self) -> List[Dict]:
        """Get all active narratives."""
        return [self.narratives[nid].to_dict() for nid in self.active_narratives 
                if nid in self.narratives]
    
    def get_by_type(self, narrative_type: NarrativeType | str) -> List[Narrative]:
        """Get narratives by type."""
        if isinstance(narrative_type, str):
            narrative_type = NarrativeType(narrative_type.lower())
        
        ids = self.type_index.get(narrative_type, set())
        return [self.narratives[nid] for nid in ids if nid in self.narratives]
    
    def get_for_participant(self, entity_id: str) -> List[Narrative]:
        """Get all narratives involving a specific entity."""
        ids = self.participant_index.get(entity_id, set())
        return [self.narratives[nid] for nid in ids if nid in self.narratives]
    
    # ─────────────────────────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────────────────────────
    
    def _index_narrative(self, narrative: Narrative):
        """Add narrative to lookup indices."""
        # Type index
        if narrative.narrative_type not in self.type_index:
            self.type_index[narrative.narrative_type] = set()
        self.type_index[narrative.narrative_type].add(narrative.id)
        
        # Participant index
        for participant_id in narrative.participant_ids:
            if participant_id not in self.participant_index:
                self.participant_index[participant_id] = set()
            self.participant_index[participant_id].add(narrative.id)
    
    def _check_conditions(self, conditions: List[Dict]) -> bool:
        """Check if all conditions are met."""
        for condition in conditions:
            cond_type = condition.get("type")
            
            if cond_type == "entity_state":
                entity_id = condition.get("entity_id")
                expected_state = condition.get("state")
                if self.world_engine._entity_manager:
                    entity = self.world_engine._entity_manager.get(entity_id)
                    if not entity or entity.state.value != expected_state:
                        return False
            
            elif cond_type == "world_time":
                min_time = condition.get("min", 0)
                max_time = condition.get("max", float("inf"))
                if not (min_time <= self.world_engine.world_time <= max_time):
                    return False
            
            elif cond_type == "entity_nearby":
                # Check if entities are near each other
                pass  # Future implementation
            
            # Add more condition types as needed
        
        return True
    
    def _execute_node_actions(self, narrative: Narrative, node: NarrativeNode):
        """Execute actions defined on a narrative node."""
        for action in node.actions:
            action_type = action.get("type")
            
            if action_type == "spawn_entity":
                if self.world_engine._entity_manager:
                    self.world_engine._entity_manager.spawn(**action.get("params", {}))
            
            elif action_type == "grant_rewards":
                self._grant_rewards(narrative)
            
            elif action_type == "trigger_narrative":
                target_id = action.get("narrative_id")
                if target_id:
                    self.trigger_arc(target_id)
            
            elif action_type == "emit_event":
                self.world_engine._emit_event(
                    action.get("event_type", "narrative_action"),
                    action.get("data", {})
                )
            
            elif action_type == "modify_entity":
                if self.world_engine._entity_manager:
                    entity_id = action.get("entity_id")
                    modifications = action.get("modifications", {})
                    entity = self.world_engine._entity_manager.get(entity_id)
                    if entity:
                        entity.attributes.update(modifications.get("attributes", {}))
    
    def _grant_rewards(self, narrative: Narrative):
        """Grant rewards for completing a narrative."""
        for reward in narrative.rewards:
            reward_type = reward.get("type")
            
            if reward_type == "item":
                # Grant item to participants
                pass  # Future: Integrate with inventory system
            
            elif reward_type == "experience":
                # Grant XP
                pass
            
            elif reward_type == "relationship":
                # Modify relationship with faction/NPC
                pass
            
            self.world_engine._emit_event("reward_granted", {
                "narrative_id": narrative.id,
                "reward": reward
            })
    
    def _apply_consequences(self, narrative: Narrative):
        """Apply consequences of narrative completion/failure."""
        for consequence in narrative.consequences:
            # Future: Process various consequence types
            self.world_engine._emit_event("consequence_applied", {
                "narrative_id": narrative.id,
                "consequence": consequence
            })
    
    # ─────────────────────────────────────────────────────────────────
    # SERIALIZATION
    # ─────────────────────────────────────────────────────────────────
    
    def export_all(self) -> List[Dict]:
        """Export all narratives for persistence."""
        return [n.to_dict() for n in self.narratives.values()]
    
    def import_all(self, narratives_data: List[Dict]):
        """Import narratives from persisted data."""
        self.narratives.clear()
        self.type_index.clear()
        self.active_narratives.clear()
        self.participant_index.clear()
        
        for narrative_data in narratives_data:
            narrative = Narrative.from_dict(narrative_data)
            self.narratives[narrative.id] = narrative
            self._index_narrative(narrative)
            
            if narrative.state == NarrativeState.ACTIVE:
                self.active_narratives.add(narrative.id)
        
        print(f"[NarrativeEngine] Imported {len(self.narratives)} narratives")
