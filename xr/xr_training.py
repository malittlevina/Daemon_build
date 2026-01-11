# xr/xr_training.py
# XR Training Module - Immersive training scenarios and skill development for daemon

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import uuid


class TrainingDomain(Enum):
    """Training domain categories."""
    TECHNICAL = "technical"          # Software, engineering, technical skills
    MECHANICAL = "mechanical"        # Physical systems, repairs, assembly
    CREATIVE = "creative"            # Art, design, creative tools
    PROCEDURAL = "procedural"        # Step-by-step procedures
    SAFETY = "safety"                # Safety protocols and emergency response
    SIMULATION = "simulation"        # Physics-based simulations
    SOCIAL = "social"                # Social interactions and communication
    COGNITIVE = "cognitive"          # Problem-solving and reasoning


class TrainingMode(Enum):
    """Training interaction modes."""
    GUIDED = "guided"                # Step-by-step guided instruction
    PRACTICE = "practice"            # Free practice with feedback
    ASSESSMENT = "assessment"        # Skill assessment/testing
    OBSERVATION = "observation"      # Passive observation mode
    COLLABORATIVE = "collaborative"  # Multi-user collaborative training


class TrainingStep:
    """Represents a single step in a training scenario."""
    
    def __init__(
        self,
        step_id: str,
        instruction: str,
        expected_action: str,
        hints: List[str] = None,
        timeout_seconds: float = 60.0,
        success_criteria: Optional[Dict] = None
    ):
        self.step_id = step_id
        self.instruction = instruction
        self.expected_action = expected_action
        self.hints = hints or []
        self.timeout_seconds = timeout_seconds
        self.success_criteria = success_criteria or {}
        self.completed = False
        self.attempts = 0
        self.time_spent = 0.0
        self.feedback_given: List[str] = []
        
    def to_dict(self) -> Dict:
        return {
            "step_id": self.step_id,
            "instruction": self.instruction,
            "expected_action": self.expected_action,
            "completed": self.completed,
            "attempts": self.attempts,
            "time_spent": self.time_spent
        }


class TrainingScenario:
    """Complete training scenario with multiple steps."""
    
    def __init__(
        self,
        scenario_id: str,
        title: str,
        description: str,
        domain: TrainingDomain,
        difficulty: int = 1,  # 1-5 scale
        estimated_duration_minutes: int = 15
    ):
        self.scenario_id = scenario_id
        self.title = title
        self.description = description
        self.domain = domain
        self.difficulty = difficulty
        self.estimated_duration_minutes = estimated_duration_minutes
        self.steps: List[TrainingStep] = []
        self.prerequisites: List[str] = []
        self.skills_taught: List[str] = []
        self.ar_assets: Dict[str, str] = {}  # Asset references for AR overlays
        self.spatial_setup: Dict[str, Any] = {}  # Spatial anchor requirements
        self.created_at = datetime.now()
        
    def add_step(self, step: TrainingStep):
        """Add a training step."""
        self.steps.append(step)
        
    def get_step(self, step_id: str) -> Optional[TrainingStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_progress(self) -> Dict:
        """Get scenario completion progress."""
        completed = sum(1 for s in self.steps if s.completed)
        return {
            "completed_steps": completed,
            "total_steps": len(self.steps),
            "progress_percent": (completed / len(self.steps) * 100) if self.steps else 0
        }
        
    def to_dict(self) -> Dict:
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain.value,
            "difficulty": self.difficulty,
            "steps_count": len(self.steps),
            "skills": self.skills_taught,
            "progress": self.get_progress()
        }


class TrainingSession:
    """Active training session tracking."""
    
    def __init__(
        self,
        session_id: str,
        scenario: TrainingScenario,
        mode: TrainingMode,
        trainee_id: Optional[str] = None
    ):
        self.session_id = session_id
        self.scenario = scenario
        self.mode = mode
        self.trainee_id = trainee_id
        self.started_at = datetime.now()
        self.ended_at: Optional[datetime] = None
        self.current_step_index = 0
        self.step_start_time: Optional[float] = None
        self.total_score = 0.0
        self.max_score = 0.0
        self.events: List[Dict] = []
        self.is_active = True
        
    def get_current_step(self) -> Optional[TrainingStep]:
        """Get the current training step."""
        if 0 <= self.current_step_index < len(self.scenario.steps):
            return self.scenario.steps[self.current_step_index]
        return None
    
    def advance_step(self) -> bool:
        """Advance to the next step."""
        if self.current_step_index < len(self.scenario.steps) - 1:
            self.current_step_index += 1
            self.step_start_time = time.time()
            return True
        return False
    
    def log_event(self, event_type: str, data: Dict):
        """Log a training event."""
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "step_index": self.current_step_index,
            "type": event_type,
            "data": data
        })
        
    def calculate_score(self) -> Dict:
        """Calculate final training score."""
        total_attempts = sum(s.attempts for s in self.scenario.steps)
        completed_steps = sum(1 for s in self.scenario.steps if s.completed)
        
        # Base score from completion
        completion_score = (completed_steps / len(self.scenario.steps)) * 100 if self.scenario.steps else 0
        
        # Efficiency bonus (fewer attempts = higher score)
        optimal_attempts = len(self.scenario.steps)
        efficiency = max(0, 1 - (total_attempts - optimal_attempts) / (optimal_attempts * 3))
        
        # Time bonus
        total_time = sum(s.time_spent for s in self.scenario.steps)
        expected_time = self.scenario.estimated_duration_minutes * 60
        time_efficiency = min(1.2, expected_time / max(total_time, 1))
        
        final_score = completion_score * 0.6 + (efficiency * 100) * 0.25 + (time_efficiency * 100) * 0.15
        
        return {
            "final_score": round(final_score, 1),
            "completion_percent": round(completion_score, 1),
            "efficiency_rating": round(efficiency * 100, 1),
            "time_efficiency": round(time_efficiency * 100, 1),
            "total_attempts": total_attempts,
            "completed_steps": completed_steps,
            "total_steps": len(self.scenario.steps)
        }
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "scenario": self.scenario.to_dict(),
            "mode": self.mode.value,
            "started_at": self.started_at.isoformat(),
            "current_step": self.current_step_index,
            "is_active": self.is_active,
            "score": self.calculate_score() if not self.is_active else None
        }


class XRTrainingModule:
    """
    XR Training Module for immersive skill development.
    
    Provides:
    - Guided AR/VR training scenarios
    - Real-time feedback and assessment
    - Spatial instruction overlays
    - Skill tracking and progression
    - Multi-domain training support
    - Integration with daemon's learning systems
    """
    
    def __init__(
        self,
        xr_engine=None,
        overlay_manager=None,
        anchor_system=None,
        gesture_interface=None
    ):
        self.xr_engine = xr_engine
        self.overlay_manager = overlay_manager
        self.anchor_system = anchor_system
        self.gesture_interface = gesture_interface
        
        self.scenarios: Dict[str, TrainingScenario] = {}
        self.active_session: Optional[TrainingSession] = None
        self.session_history: List[TrainingSession] = []
        self.skill_progress: Dict[str, float] = {}  # skill -> mastery level 0-100
        self.training_stats: Dict[str, int] = {
            "sessions_completed": 0,
            "total_training_minutes": 0,
            "skills_learned": 0
        }
        
        self._load_builtin_scenarios()
        print("[XRTrainingModule] Initialized.")
        
    def _load_builtin_scenarios(self):
        """Load built-in training scenarios."""
        
        # Technical scenario: Code Review in AR
        code_review = TrainingScenario(
            scenario_id="tech_code_review",
            title="AR Code Review Fundamentals",
            description="Learn to review code effectively using AR annotations",
            domain=TrainingDomain.TECHNICAL,
            difficulty=2,
            estimated_duration_minutes=20
        )
        code_review.skills_taught = ["code_review", "annotation", "ar_navigation"]
        code_review.add_step(TrainingStep(
            step_id="cr_1",
            instruction="Look at the holographic code panel. Identify the function with a bug.",
            expected_action="point_at_target",
            hints=["Check the loop conditions", "Look for off-by-one errors"]
        ))
        code_review.add_step(TrainingStep(
            step_id="cr_2",
            instruction="Use a pinch gesture to place an annotation marker on the bug.",
            expected_action="pinch_gesture",
            hints=["Bring thumb and index finger together"]
        ))
        code_review.add_step(TrainingStep(
            step_id="cr_3",
            instruction="Speak your code review comment into the annotation.",
            expected_action="voice_input",
            hints=["Describe what the bug is and how to fix it"]
        ))
        self.scenarios[code_review.scenario_id] = code_review
        
        # Mechanical scenario: Engine Assembly
        engine_assembly = TrainingScenario(
            scenario_id="mech_engine_assembly",
            title="Virtual Engine Assembly Training",
            description="Learn mechanical assembly through AR-guided steps",
            domain=TrainingDomain.MECHANICAL,
            difficulty=3,
            estimated_duration_minutes=30
        )
        engine_assembly.skills_taught = ["mechanical_assembly", "tool_usage", "spatial_reasoning"]
        engine_assembly.add_step(TrainingStep(
            step_id="ea_1",
            instruction="Locate the crankshaft in the parts display. The highlighted part shows its position.",
            expected_action="identify_part",
            hints=["It's the long cylindrical part", "Follow the green highlight"]
        ))
        engine_assembly.add_step(TrainingStep(
            step_id="ea_2",
            instruction="Grab the crankshaft and position it in the engine block.",
            expected_action="grab_and_place",
            hints=["Use grab gesture to pick up", "Align with the mounting points"]
        ))
        engine_assembly.add_step(TrainingStep(
            step_id="ea_3",
            instruction="Select the correct torque wrench and tighten the mounting bolts.",
            expected_action="tool_operation",
            hints=["Check the torque specification: 65 Nm", "Tighten in star pattern"]
        ))
        self.scenarios[engine_assembly.scenario_id] = engine_assembly
        
        # Safety scenario: Emergency Response
        emergency_response = TrainingScenario(
            scenario_id="safety_emergency",
            title="Emergency Response Protocol",
            description="Practice emergency procedures in simulated environment",
            domain=TrainingDomain.SAFETY,
            difficulty=2,
            estimated_duration_minutes=15
        )
        emergency_response.skills_taught = ["emergency_response", "evacuation", "first_aid_basics"]
        emergency_response.add_step(TrainingStep(
            step_id="er_1",
            instruction="The fire alarm has triggered. Locate the nearest emergency exit.",
            expected_action="locate_waypoint",
            hints=["Look for the green exit signs", "Follow the AR waypoints"]
        ))
        emergency_response.add_step(TrainingStep(
            step_id="er_2",
            instruction="Check for obstacles in the evacuation path. Point to any hazards.",
            expected_action="point_at_hazards",
            hints=["Look for blocked paths", "Check for smoke or debris"]
        ))
        emergency_response.add_step(TrainingStep(
            step_id="er_3",
            instruction="Proceed to the assembly point following the AR navigation.",
            expected_action="follow_path",
            hints=["Stay low if there's smoke", "Help others along the way"]
        ))
        self.scenarios[emergency_response.scenario_id] = emergency_response
        
        # Creative scenario: 3D Modeling in AR
        modeling_basics = TrainingScenario(
            scenario_id="creative_3d_modeling",
            title="AR 3D Modeling Basics",
            description="Learn 3D modeling concepts using hand gestures in AR",
            domain=TrainingDomain.CREATIVE,
            difficulty=2,
            estimated_duration_minutes=25
        )
        modeling_basics.skills_taught = ["3d_modeling", "gesture_sculpting", "spatial_design"]
        modeling_basics.add_step(TrainingStep(
            step_id="m3d_1",
            instruction="Create a primitive cube by performing the 'box' gesture.",
            expected_action="create_primitive",
            hints=["Frame a space with both hands", "The cube appears between your hands"]
        ))
        modeling_basics.add_step(TrainingStep(
            step_id="m3d_2",
            instruction="Scale the cube to twice its size using the scale gesture.",
            expected_action="scale_object",
            hints=["Move both hands apart", "Watch the size indicator"]
        ))
        modeling_basics.add_step(TrainingStep(
            step_id="m3d_3",
            instruction="Rotate the cube 45 degrees using the rotation gesture.",
            expected_action="rotate_object",
            hints=["Twist your wrist while grabbing", "Use the rotation gizmo as guide"]
        ))
        self.scenarios[modeling_basics.scenario_id] = modeling_basics
        
        # Procedural scenario: Equipment Calibration
        calibration = TrainingScenario(
            scenario_id="proc_calibration",
            title="Equipment Calibration Procedure",
            description="Learn proper calibration procedures with AR guidance",
            domain=TrainingDomain.PROCEDURAL,
            difficulty=3,
            estimated_duration_minutes=20
        )
        calibration.skills_taught = ["calibration", "precision_measurement", "documentation"]
        calibration.add_step(TrainingStep(
            step_id="cal_1",
            instruction="Power on the calibration target and wait for initialization.",
            expected_action="power_device",
            hints=["Press the green button", "Wait for the ready indicator"]
        ))
        calibration.add_step(TrainingStep(
            step_id="cal_2",
            instruction="Align the sensor with the calibration markers shown in AR.",
            expected_action="align_sensor",
            hints=["Match the crosshairs", "Keep your hand steady"]
        ))
        calibration.add_step(TrainingStep(
            step_id="cal_3",
            instruction="Record the calibration reading in the AR data panel.",
            expected_action="record_data",
            hints=["Use voice or gesture input", "Confirm the value"]
        ))
        self.scenarios[calibration.scenario_id] = calibration
        
        print(f"[XRTrainingModule] Loaded {len(self.scenarios)} built-in scenarios")
        
    def register_scenario(self, scenario: TrainingScenario):
        """Register a custom training scenario."""
        self.scenarios[scenario.scenario_id] = scenario
        print(f"[XRTrainingModule] Registered scenario: {scenario.title}")
        
    def list_scenarios(
        self,
        domain_filter: Optional[str] = None,
        max_difficulty: Optional[int] = None
    ) -> List[Dict]:
        """List available training scenarios with optional filters."""
        scenarios = list(self.scenarios.values())
        
        if domain_filter:
            domain = TrainingDomain(domain_filter.lower())
            scenarios = [s for s in scenarios if s.domain == domain]
            
        if max_difficulty:
            scenarios = [s for s in scenarios if s.difficulty <= max_difficulty]
            
        return [s.to_dict() for s in scenarios]
    
    def start_training(
        self,
        scenario_id: str,
        mode: str = "guided",
        trainee_id: Optional[str] = None
    ) -> Optional[TrainingSession]:
        """
        Start a new training session.
        
        Args:
            scenario_id: ID of the scenario to start
            mode: Training mode (guided, practice, assessment)
            trainee_id: Optional trainee identifier
            
        Returns:
            Created TrainingSession or None if scenario not found
        """
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            print(f"[XRTrainingModule] Scenario not found: {scenario_id}")
            return None
            
        # End any active session
        if self.active_session:
            self.end_training()
            
        # Create new session
        session_id = f"train_{uuid.uuid4().hex[:8]}"
        training_mode = TrainingMode(mode.lower())
        
        session = TrainingSession(
            session_id=session_id,
            scenario=scenario,
            mode=training_mode,
            trainee_id=trainee_id
        )
        session.step_start_time = time.time()
        
        self.active_session = session
        
        # Set up XR environment for training
        self._setup_training_environment(session)
        
        print(f"[XRTrainingModule] Started training: {scenario.title}")
        print(f"[XRTrainingModule] Mode: {training_mode.value}")
        
        # Display first step
        self._display_current_step(session)
        
        return session
    
    def _setup_training_environment(self, session: TrainingSession):
        """Set up the XR environment for training."""
        # Start XR session if not active
        if self.xr_engine and not self.xr_engine.current_session:
            self.xr_engine.start_session(mode="ar", device_type="simulated")
            
        # Create training HUD
        if self.overlay_manager:
            self.overlay_manager.create_hud_element(
                content=f"Training: {session.scenario.title}",
                hud_position="top-left"
            )
            
            # Progress indicator
            progress = session.scenario.get_progress()
            self.overlay_manager.create_hud_element(
                content=f"Step {session.current_step_index + 1}/{len(session.scenario.steps)}",
                hud_position="top-right"
            )
            
        # Set up spatial anchors if defined
        if self.anchor_system and session.scenario.spatial_setup:
            for label, position in session.scenario.spatial_setup.items():
                self.anchor_system.create_semantic_anchor(
                    semantic_label=f"training_{label}",
                    position=tuple(position),
                    persistent=False
                )
                
    def _display_current_step(self, session: TrainingSession):
        """Display the current training step instructions."""
        step = session.get_current_step()
        if not step:
            return
            
        # Create instruction overlay
        if self.overlay_manager:
            self.overlay_manager.clear_group("training_instructions")
            self.overlay_manager.create_info_panel(
                text=step.instruction,
                title=f"Step {session.current_step_index + 1}",
                position=(0, 1.6, 1.5)
            )
            
        # Log event
        session.log_event("step_started", {
            "step_id": step.step_id,
            "instruction": step.instruction
        })
        
        # Notify XR engine
        if self.xr_engine and self.xr_engine.current_session:
            self.xr_engine.current_session.training_context = {
                "scenario": session.scenario.scenario_id,
                "step": step.step_id,
                "expected_action": step.expected_action
            }
    
    def provide_hint(self) -> Optional[str]:
        """Provide a hint for the current step."""
        if not self.active_session:
            return None
            
        step = self.active_session.get_current_step()
        if not step or not step.hints:
            return None
            
        # Get next unused hint
        hint_index = len(step.feedback_given) % len(step.hints)
        hint = step.hints[hint_index]
        step.feedback_given.append(f"Hint: {hint}")
        
        # Display hint
        if self.overlay_manager:
            self.overlay_manager.create_info_panel(
                text=hint,
                title="💡 Hint",
                position=(0.5, 1.4, 1.5)
            )
            
        self.active_session.log_event("hint_provided", {"hint": hint})
        print(f"[XRTrainingModule] Hint: {hint}")
        return hint
    
    def submit_action(
        self,
        action_type: str,
        action_data: Optional[Dict] = None
    ) -> Dict:
        """
        Submit a trainee action for evaluation.
        
        Args:
            action_type: Type of action performed
            action_data: Additional action data
            
        Returns:
            Evaluation result
        """
        if not self.active_session:
            return {"success": False, "error": "No active training session"}
            
        step = self.active_session.get_current_step()
        if not step:
            return {"success": False, "error": "No current step"}
            
        step.attempts += 1
        
        # Calculate time spent on step
        if self.active_session.step_start_time:
            step.time_spent += time.time() - self.active_session.step_start_time
            
        # Evaluate action
        result = self._evaluate_action(step, action_type, action_data)
        
        self.active_session.log_event("action_submitted", {
            "action_type": action_type,
            "expected": step.expected_action,
            "result": result
        })
        
        if result["correct"]:
            step.completed = True
            self._provide_feedback("success", result.get("feedback", "Correct!"))
            
            # Advance to next step
            if self.active_session.advance_step():
                self.active_session.step_start_time = time.time()
                self._display_current_step(self.active_session)
                result["next_step"] = True
            else:
                # Training complete
                result["training_complete"] = True
                self._complete_training()
        else:
            self._provide_feedback("error", result.get("feedback", "Try again."))
            
        return result
    
    def _evaluate_action(
        self,
        step: TrainingStep,
        action_type: str,
        action_data: Optional[Dict]
    ) -> Dict:
        """Evaluate if the action matches the expected action."""
        # Flexible matching based on action type
        action_mappings = {
            "point_at_target": ["point", "tap", "select"],
            "pinch_gesture": ["pinch", "select"],
            "grab_and_place": ["grab", "drop", "place"],
            "voice_input": ["voice", "speech"],
            "identify_part": ["point", "select", "tap"],
            "tool_operation": ["grab", "use", "operate"],
            "locate_waypoint": ["point", "look", "navigate"],
            "point_at_hazards": ["point", "select"],
            "follow_path": ["walk", "move", "navigate"],
            "create_primitive": ["gesture", "create"],
            "scale_object": ["scale", "resize"],
            "rotate_object": ["rotate", "turn"],
            "power_device": ["tap", "press", "activate"],
            "align_sensor": ["move", "align", "position"],
            "record_data": ["confirm", "save", "input"]
        }
        
        expected = step.expected_action
        acceptable = action_mappings.get(expected, [expected])
        
        is_correct = action_type.lower() in acceptable
        
        return {
            "correct": is_correct,
            "expected": expected,
            "received": action_type,
            "feedback": "Well done!" if is_correct else f"Expected action: {expected}"
        }
    
    def _provide_feedback(self, feedback_type: str, message: str):
        """Provide visual/audio feedback to trainee."""
        if self.overlay_manager:
            color = "green" if feedback_type == "success" else "red"
            title = "✓ Success" if feedback_type == "success" else "✗ Try Again"
            
            self.overlay_manager.create_info_panel(
                text=message,
                title=title,
                position=(0, 1.3, 1.5)
            )
            
        print(f"[XRTrainingModule] Feedback ({feedback_type}): {message}")
        
    def _complete_training(self):
        """Handle training completion."""
        if not self.active_session:
            return
            
        session = self.active_session
        session.is_active = False
        session.ended_at = datetime.now()
        
        # Calculate final score
        score = session.calculate_score()
        
        # Update skill progress
        for skill in session.scenario.skills_taught:
            current = self.skill_progress.get(skill, 0)
            improvement = (score["final_score"] / 100) * 10  # Max 10% per session
            self.skill_progress[skill] = min(100, current + improvement)
            
        # Update stats
        duration = (session.ended_at - session.started_at).total_seconds() / 60
        self.training_stats["sessions_completed"] += 1
        self.training_stats["total_training_minutes"] += int(duration)
        self.training_stats["skills_learned"] = len(self.skill_progress)
        
        # Display completion
        if self.overlay_manager:
            self.overlay_manager.clear_group("training_instructions")
            self.overlay_manager.create_info_panel(
                text=(
                    f"Final Score: {score['final_score']}%\n"
                    f"Completion: {score['completion_percent']}%\n"
                    f"Efficiency: {score['efficiency_rating']}%\n"
                    f"Time Bonus: {score['time_efficiency']}%"
                ),
                title="🎓 Training Complete!",
                position=(0, 1.5, 1.5)
            )
            
        # Save session
        self.session_history.append(session)
        self._save_training_log(session)
        
        print(f"[XRTrainingModule] Training complete!")
        print(f"[XRTrainingModule] Score: {score['final_score']}%")
        
    def end_training(self) -> Optional[Dict]:
        """End the current training session early."""
        if not self.active_session:
            return None
            
        self.active_session.is_active = False
        self.active_session.ended_at = datetime.now()
        
        # Log early end
        self.active_session.log_event("session_ended_early", {
            "reason": "user_request",
            "progress": self.active_session.scenario.get_progress()
        })
        
        result = self.active_session.to_dict()
        self.session_history.append(self.active_session)
        self._save_training_log(self.active_session)
        
        # Clean up overlays
        if self.overlay_manager:
            self.overlay_manager.clear_group("training_instructions")
            self.overlay_manager.clear_group("hud")
            
        print(f"[XRTrainingModule] Training ended early")
        self.active_session = None
        return result
    
    def get_skill_progress(self) -> Dict[str, float]:
        """Get current skill mastery levels."""
        return self.skill_progress.copy()
    
    def get_training_stats(self) -> Dict:
        """Get overall training statistics."""
        return {
            **self.training_stats,
            "skills": self.skill_progress,
            "sessions_in_history": len(self.session_history)
        }
    
    def get_recommended_scenarios(self, count: int = 3) -> List[Dict]:
        """Get recommended training scenarios based on skill gaps."""
        recommendations = []
        
        for scenario in self.scenarios.values():
            # Calculate relevance score
            skill_gaps = []
            for skill in scenario.skills_taught:
                current = self.skill_progress.get(skill, 0)
                skill_gaps.append(100 - current)
                
            if skill_gaps:
                avg_gap = sum(skill_gaps) / len(skill_gaps)
                scenario_dict = scenario.to_dict()
                scenario_dict["recommendation_score"] = avg_gap
                recommendations.append(scenario_dict)
                
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:count]
    
    def _save_training_log(self, session: TrainingSession):
        """Save training session log."""
        os.makedirs("logs/training", exist_ok=True)
        log_path = f"logs/training/{session.session_id}.json"
        
        log_data = session.to_dict()
        log_data["events"] = session.events
        log_data["score"] = session.calculate_score()
        
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)
            
        print(f"[XRTrainingModule] Session log saved: {log_path}")
        
    def import_scenario(self, scenario_data: Dict) -> Optional[TrainingScenario]:
        """Import a training scenario from dictionary."""
        try:
            scenario = TrainingScenario(
                scenario_id=scenario_data["scenario_id"],
                title=scenario_data["title"],
                description=scenario_data["description"],
                domain=TrainingDomain(scenario_data["domain"]),
                difficulty=scenario_data.get("difficulty", 1),
                estimated_duration_minutes=scenario_data.get("estimated_duration_minutes", 15)
            )
            
            for step_data in scenario_data.get("steps", []):
                step = TrainingStep(
                    step_id=step_data["step_id"],
                    instruction=step_data["instruction"],
                    expected_action=step_data["expected_action"],
                    hints=step_data.get("hints", []),
                    timeout_seconds=step_data.get("timeout_seconds", 60.0)
                )
                scenario.add_step(step)
                
            scenario.skills_taught = scenario_data.get("skills_taught", [])
            self.register_scenario(scenario)
            return scenario
            
        except Exception as e:
            print(f"[XRTrainingModule] Failed to import scenario: {e}")
            return None
