# lam/action_registry.py
# Action Registry - Manages learned actions, behaviors, and skill compositions

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
from dataclasses import dataclass, field
import uuid


class ActionCategory(Enum):
    """Categories for organizing actions."""
    SYSTEM = "system"               # System-level operations
    KNOWLEDGE = "knowledge"         # Knowledge and learning
    TASK = "task"                   # Task execution
    COMMUNICATION = "communication" # Communication and responses
    XR = "xr"                       # AR/VR/XR actions
    CREATIVE = "creative"           # Creative tasks
    ANALYSIS = "analysis"           # Analysis and reasoning
    AUTOMATION = "automation"       # Automated workflows


class ActionComplexity(Enum):
    """Complexity level of actions."""
    ATOMIC = "atomic"               # Single, indivisible action
    COMPOSITE = "composite"         # Composed of multiple actions
    CONDITIONAL = "conditional"     # Has conditional branches
    LOOP = "loop"                   # Contains repetition
    ADAPTIVE = "adaptive"           # Adapts based on context


@dataclass
class ActionDefinition:
    """Definition of a registered action."""
    action_id: str
    name: str
    description: str
    category: ActionCategory
    complexity: ActionComplexity
    handler: Optional[str] = None           # Handler function reference
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_context: List[str] = field(default_factory=list)
    produces: List[str] = field(default_factory=list)  # What this action produces
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    estimated_duration_ms: int = 1000
    success_rate: float = 1.0
    usage_count: int = 0
    last_used: str = ""
    enabled: bool = True
    child_actions: List[str] = field(default_factory=list)  # For composite actions
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "complexity": self.complexity.value,
            "handler": self.handler,
            "parameters": self.parameters,
            "required_context": self.required_context,
            "produces": self.produces,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "estimated_duration_ms": self.estimated_duration_ms,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "enabled": self.enabled,
            "child_actions": self.child_actions
        }


@dataclass
class ActionSequence:
    """A sequence of actions to be executed."""
    sequence_id: str
    name: str
    description: str
    actions: List[str]                      # List of action IDs
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_count: int = 0
    success_count: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "sequence_id": self.sequence_id,
            "name": self.name,
            "description": self.description,
            "actions": self.actions,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "execution_count": self.execution_count,
            "success_rate": self.success_count / self.execution_count if self.execution_count > 0 else 0
        }


class ActionRegistry:
    """
    Central registry for all actions the daemon can perform.
    
    Provides:
    - Action registration and discovery
    - Action composition and sequencing
    - Precondition/postcondition checking
    - Action statistics and optimization
    - Dynamic action generation
    """
    
    def __init__(self, data_path: str = "data/lam"):
        self.data_path = data_path
        self.actions: Dict[str, ActionDefinition] = {}
        self.sequences: Dict[str, ActionSequence] = {}
        self.handlers: Dict[str, Callable] = {}
        self.category_index: Dict[str, List[str]] = {}  # category -> action_ids
        
        os.makedirs(data_path, exist_ok=True)
        self._load_registry()
        self._register_builtin_actions()
        print("[ActionRegistry] Initialized.")
        
    def _load_registry(self):
        """Load registry from disk."""
        registry_file = os.path.join(self.data_path, "action_registry.json")
        if os.path.exists(registry_file):
            try:
                with open(registry_file, "r") as f:
                    data = json.load(f)
                    for a in data.get("actions", []):
                        action = ActionDefinition(
                            action_id=a["action_id"],
                            name=a["name"],
                            description=a["description"],
                            category=ActionCategory(a["category"]),
                            complexity=ActionComplexity(a["complexity"]),
                            handler=a.get("handler"),
                            parameters=a.get("parameters", {}),
                            required_context=a.get("required_context", []),
                            produces=a.get("produces", []),
                            preconditions=a.get("preconditions", []),
                            postconditions=a.get("postconditions", []),
                            estimated_duration_ms=a.get("estimated_duration_ms", 1000),
                            success_rate=a.get("success_rate", 1.0),
                            usage_count=a.get("usage_count", 0),
                            enabled=a.get("enabled", True),
                            child_actions=a.get("child_actions", [])
                        )
                        self.actions[action.action_id] = action
                        self._index_action(action)
                        
                    for s in data.get("sequences", []):
                        seq = ActionSequence(
                            sequence_id=s["sequence_id"],
                            name=s["name"],
                            description=s["description"],
                            actions=s["actions"],
                            parameters=s.get("parameters", {}),
                            created_at=s.get("created_at", ""),
                            execution_count=s.get("execution_count", 0),
                            success_count=s.get("success_count", 0)
                        )
                        self.sequences[seq.sequence_id] = seq
                        
                print(f"[ActionRegistry] Loaded {len(self.actions)} actions, {len(self.sequences)} sequences")
            except Exception as e:
                print(f"[ActionRegistry] Error loading registry: {e}")
                
    def _save_registry(self):
        """Save registry to disk."""
        registry_file = os.path.join(self.data_path, "action_registry.json")
        data = {
            "actions": [a.to_dict() for a in self.actions.values()],
            "sequences": [s.to_dict() for s in self.sequences.values()],
            "saved_at": datetime.now().isoformat()
        }
        with open(registry_file, "w") as f:
            json.dump(data, f, indent=2)
            
    def _index_action(self, action: ActionDefinition):
        """Add action to category index."""
        cat = action.category.value
        if cat not in self.category_index:
            self.category_index[cat] = []
        if action.action_id not in self.category_index[cat]:
            self.category_index[cat].append(action.action_id)
            
    def _register_builtin_actions(self):
        """Register built-in daemon actions."""
        builtins = [
            # System actions
            ActionDefinition(
                action_id="sys_optimize",
                name="Self Optimize",
                description="Trigger self-optimization routine",
                category=ActionCategory.SYSTEM,
                complexity=ActionComplexity.COMPOSITE,
                handler="optimizer.auto_upgrade.run_auto_optimization"
            ),
            ActionDefinition(
                action_id="sys_reflect",
                name="Self Reflect",
                description="Trigger introspection and reflection",
                category=ActionCategory.SYSTEM,
                complexity=ActionComplexity.ATOMIC,
                handler="unimind.core.Unimind.reflect"
            ),
            
            # Knowledge actions
            ActionDefinition(
                action_id="know_study",
                name="Study Topic",
                description="Study and learn about a topic",
                category=ActionCategory.KNOWLEDGE,
                complexity=ActionComplexity.COMPOSITE,
                parameters={"topic": {"type": "string", "required": True}},
                produces=["knowledge_entry", "summary"]
            ),
            ActionDefinition(
                action_id="know_query",
                name="Query Knowledge",
                description="Query the knowledge base",
                category=ActionCategory.KNOWLEDGE,
                complexity=ActionComplexity.ATOMIC,
                parameters={"query": {"type": "string", "required": True}},
                produces=["answer"]
            ),
            ActionDefinition(
                action_id="know_ingest",
                name="Ingest Document",
                description="Ingest a document into the knowledge base",
                category=ActionCategory.KNOWLEDGE,
                complexity=ActionComplexity.ATOMIC,
                parameters={"source": {"type": "string", "required": True}}
            ),
            
            # Task actions
            ActionDefinition(
                action_id="task_execute",
                name="Execute Task",
                description="Execute a general task",
                category=ActionCategory.TASK,
                complexity=ActionComplexity.ADAPTIVE,
                parameters={"description": {"type": "string", "required": True}}
            ),
            ActionDefinition(
                action_id="task_plan",
                name="Create Plan",
                description="Create a multi-step plan for a goal",
                category=ActionCategory.TASK,
                complexity=ActionComplexity.COMPOSITE,
                parameters={"goal": {"type": "string", "required": True}},
                produces=["plan"]
            ),
            
            # Communication actions
            ActionDefinition(
                action_id="comm_respond",
                name="Generate Response",
                description="Generate a response to user input",
                category=ActionCategory.COMMUNICATION,
                complexity=ActionComplexity.ATOMIC,
                parameters={"input": {"type": "string", "required": True}},
                produces=["response"]
            ),
            
            # XR actions
            ActionDefinition(
                action_id="xr_start_session",
                name="Start XR Session",
                description="Start an AR/VR/MR session",
                category=ActionCategory.XR,
                complexity=ActionComplexity.ATOMIC,
                parameters={"mode": {"type": "string", "default": "ar"}},
                produces=["xr_session"]
            ),
            ActionDefinition(
                action_id="xr_start_training",
                name="Start XR Training",
                description="Start an XR training scenario",
                category=ActionCategory.XR,
                complexity=ActionComplexity.COMPOSITE,
                parameters={"scenario_id": {"type": "string", "required": True}},
                produces=["training_session"]
            ),
            ActionDefinition(
                action_id="xr_create_overlay",
                name="Create AR Overlay",
                description="Create an AR overlay element",
                category=ActionCategory.XR,
                complexity=ActionComplexity.ATOMIC,
                parameters={
                    "content": {"type": "string", "required": True},
                    "type": {"type": "string", "default": "info_panel"}
                },
                produces=["overlay"]
            ),
            
            # Analysis actions
            ActionDefinition(
                action_id="analyze_reason",
                name="Symbolic Reasoning",
                description="Perform symbolic reasoning on a problem",
                category=ActionCategory.ANALYSIS,
                complexity=ActionComplexity.COMPOSITE,
                parameters={"problem": {"type": "string", "required": True}},
                produces=["reasoning_chain", "conclusion"]
            ),
        ]
        
        for action in builtins:
            if action.action_id not in self.actions:
                self.actions[action.action_id] = action
                self._index_action(action)
                
    def register_action(
        self,
        name: str,
        description: str,
        category: str,
        complexity: str = "atomic",
        handler: Optional[Callable] = None,
        parameters: Optional[Dict] = None,
        **kwargs
    ) -> ActionDefinition:
        """
        Register a new action.
        
        Args:
            name: Human-readable name
            description: What the action does
            category: Action category
            complexity: Complexity level
            handler: Optional callable handler
            parameters: Parameter definitions
            **kwargs: Additional action properties
            
        Returns:
            Created ActionDefinition
        """
        action_id = f"act_{uuid.uuid4().hex[:8]}"
        
        action = ActionDefinition(
            action_id=action_id,
            name=name,
            description=description,
            category=ActionCategory(category),
            complexity=ActionComplexity(complexity),
            handler=handler.__name__ if handler else None,
            parameters=parameters or {},
            **kwargs
        )
        
        self.actions[action_id] = action
        self._index_action(action)
        
        if handler:
            self.handlers[action_id] = handler
            
        self._save_registry()
        print(f"[ActionRegistry] Registered action: {name} ({action_id})")
        return action
    
    def register_handler(self, action_id: str, handler: Callable):
        """Register a handler for an existing action."""
        if action_id in self.actions:
            self.handlers[action_id] = handler
            self.actions[action_id].handler = handler.__name__
            print(f"[ActionRegistry] Registered handler for {action_id}")
            
    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        """Get action by ID."""
        return self.actions.get(action_id)
    
    def find_actions(
        self,
        category: Optional[str] = None,
        complexity: Optional[str] = None,
        produces: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[ActionDefinition]:
        """
        Find actions matching criteria.
        
        Args:
            category: Filter by category
            complexity: Filter by complexity
            produces: Filter by what the action produces
            enabled_only: Only return enabled actions
            
        Returns:
            List of matching ActionDefinitions
        """
        results = []
        
        for action in self.actions.values():
            if enabled_only and not action.enabled:
                continue
            if category and action.category.value != category:
                continue
            if complexity and action.complexity.value != complexity:
                continue
            if produces and produces not in action.produces:
                continue
            results.append(action)
            
        return results
    
    def create_sequence(
        self,
        name: str,
        description: str,
        action_ids: List[str],
        parameters: Optional[Dict] = None
    ) -> Optional[ActionSequence]:
        """
        Create a new action sequence.
        
        Args:
            name: Sequence name
            description: What the sequence does
            action_ids: Ordered list of action IDs
            parameters: Sequence parameters
            
        Returns:
            Created ActionSequence or None if invalid
        """
        # Validate all actions exist
        for aid in action_ids:
            if aid not in self.actions:
                print(f"[ActionRegistry] Invalid action in sequence: {aid}")
                return None
                
        seq_id = f"seq_{uuid.uuid4().hex[:8]}"
        
        sequence = ActionSequence(
            sequence_id=seq_id,
            name=name,
            description=description,
            actions=action_ids,
            parameters=parameters or {}
        )
        
        self.sequences[seq_id] = sequence
        self._save_registry()
        
        print(f"[ActionRegistry] Created sequence: {name} ({len(action_ids)} actions)")
        return sequence
    
    def execute_action(
        self,
        action_id: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[Any, bool]:
        """
        Execute a registered action.
        
        Args:
            action_id: ID of action to execute
            params: Execution parameters
            context: Current context
            
        Returns:
            Tuple of (result, success)
        """
        action = self.actions.get(action_id)
        if not action:
            return None, False
            
        if not action.enabled:
            print(f"[ActionRegistry] Action {action_id} is disabled")
            return None, False
            
        # Check preconditions
        for precond in action.preconditions:
            if precond not in context.get("satisfied_conditions", []):
                print(f"[ActionRegistry] Precondition not met: {precond}")
                return None, False
                
        # Execute handler
        handler = self.handlers.get(action_id)
        if handler:
            try:
                result = handler(params, context)
                action.usage_count += 1
                action.last_used = datetime.now().isoformat()
                self._save_registry()
                return result, True
            except Exception as e:
                print(f"[ActionRegistry] Execution error: {e}")
                # Update success rate
                action.success_rate = (action.success_rate * action.usage_count) / (action.usage_count + 1)
                action.usage_count += 1
                self._save_registry()
                return None, False
        else:
            print(f"[ActionRegistry] No handler for action: {action_id}")
            return None, False
    
    def execute_sequence(
        self,
        sequence_id: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Tuple[List[Any], bool]:
        """
        Execute an action sequence.
        
        Args:
            sequence_id: ID of sequence to execute
            params: Execution parameters
            context: Current context
            
        Returns:
            Tuple of (results_list, all_succeeded)
        """
        sequence = self.sequences.get(sequence_id)
        if not sequence:
            return [], False
            
        results = []
        all_success = True
        current_context = context.copy()
        
        for action_id in sequence.actions:
            result, success = self.execute_action(action_id, params, current_context)
            results.append({"action_id": action_id, "result": result, "success": success})
            
            if not success:
                all_success = False
                break  # Stop sequence on failure
                
            # Update context with action results
            action = self.actions.get(action_id)
            if action and action.postconditions:
                current_context.setdefault("satisfied_conditions", []).extend(action.postconditions)
                
        sequence.execution_count += 1
        if all_success:
            sequence.success_count += 1
        self._save_registry()
        
        return results, all_success
    
    def compose_action(
        self,
        name: str,
        description: str,
        child_action_ids: List[str],
        category: str = "automation"
    ) -> Optional[ActionDefinition]:
        """
        Create a composite action from existing actions.
        
        Args:
            name: Name for composite action
            description: What the composite does
            child_action_ids: Actions that compose this action
            category: Category for the composite
            
        Returns:
            Created composite ActionDefinition
        """
        # Validate child actions
        for aid in child_action_ids:
            if aid not in self.actions:
                return None
                
        action = self.register_action(
            name=name,
            description=description,
            category=category,
            complexity="composite"
        )
        action.child_actions = child_action_ids
        
        # Aggregate produces from children
        all_produces = set()
        for aid in child_action_ids:
            child = self.actions[aid]
            all_produces.update(child.produces)
        action.produces = list(all_produces)
        
        self._save_registry()
        return action
    
    def get_action_graph(self) -> Dict[str, List[str]]:
        """Get dependency graph of composite actions."""
        graph = {}
        for action in self.actions.values():
            if action.child_actions:
                graph[action.action_id] = action.child_actions
        return graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total_usage = sum(a.usage_count for a in self.actions.values())
        avg_success = sum(a.success_rate for a in self.actions.values()) / len(self.actions) if self.actions else 0
        
        category_counts = {}
        for cat, aids in self.category_index.items():
            category_counts[cat] = len(aids)
            
        return {
            "total_actions": len(self.actions),
            "total_sequences": len(self.sequences),
            "total_usage": total_usage,
            "average_success_rate": avg_success,
            "actions_by_category": category_counts,
            "enabled_actions": sum(1 for a in self.actions.values() if a.enabled)
        }
    
    def list_actions(self, category: Optional[str] = None) -> List[Dict]:
        """List all actions with summaries."""
        actions = self.find_actions(category=category)
        return [a.to_dict() for a in actions]
