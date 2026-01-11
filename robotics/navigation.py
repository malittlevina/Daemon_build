# robotics/navigation.py
"""
Navigation Planner for Companion Robot.

Provides intelligent path planning and navigation by integrating
with the LAM (Language-Action Model) planner for symbolic reasoning.

Features:
- Waypoint-based navigation
- Obstacle avoidance
- User-following logic
- Semantic location understanding
"""

import time
import math
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum


class NavigationState(Enum):
    """Navigation state machine states."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    AVOIDING = "avoiding"
    ARRIVED = "arrived"
    FAILED = "failed"
    FOLLOWING = "following"


@dataclass
class Waypoint:
    """A navigation waypoint."""
    x: float
    y: float
    name: Optional[str] = None
    tolerance: float = 0.15  # meters
    speed_limit: Optional[float] = None


@dataclass
class NavigationGoal:
    """A navigation goal with context."""
    target: str  # Semantic or coordinate target
    waypoints: List[Waypoint]
    priority: int = 0
    timeout: float = 300.0  # 5 minutes default
    start_time: float = 0.0


class NavigationPlanner:
    """
    Navigation planner for the companion robot.
    
    Integrates with LAM for:
    - Semantic goal understanding
    - Context-aware path selection
    - Dynamic replanning
    """
    
    # Known semantic locations (can be learned/updated)
    SEMANTIC_LOCATIONS: Dict[str, Tuple[float, float]] = {
        "home": (0.0, 0.0),
        "charging_station": (0.5, 0.0),
        "desk": (2.0, 1.0),
        "door": (3.0, 0.0),
        "couch": (-1.0, 2.0),
        "kitchen": (4.0, 2.0)
    }
    
    def __init__(self, motion_controller, robot_state):
        """
        Initialize navigation planner.
        
        Args:
            motion_controller: MotionController instance
            robot_state: RobotState instance
        """
        self.motion = motion_controller
        self.state = robot_state
        
        self.nav_state = NavigationState.IDLE
        self.current_goal: Optional[NavigationGoal] = None
        self.current_waypoint_index = 0
        
        # Obstacle avoidance parameters
        self.obstacle_threshold = 0.3  # meters
        self.avoidance_distance = 0.5  # meters to back up
        self.avoidance_angle = math.pi / 4  # 45 degrees
        
        # Following parameters
        self.follow_distance = 1.0  # Target distance to user
        self.follow_tolerance = 0.3  # Acceptable range
        
        # Path history for learning
        self.path_history: List[Tuple[float, float]] = []
        
        print("[NavigationPlanner] Initialized")
    
    def set_target(self, target: str) -> bool:
        """
        Set navigation target.
        
        Args:
            target: Semantic location name or "x,y" coordinates
            
        Returns:
            True if target accepted
        """
        waypoints = self._resolve_target(target)
        
        if not waypoints:
            print(f"[NavigationPlanner] Cannot resolve target: {target}")
            self.nav_state = NavigationState.FAILED
            return False
        
        self.current_goal = NavigationGoal(
            target=target,
            waypoints=waypoints,
            start_time=time.time()
        )
        self.current_waypoint_index = 0
        self.nav_state = NavigationState.PLANNING
        
        # Integrate with LAM for context
        self._notify_lam_planning(target)
        
        print(f"[NavigationPlanner] Target set: {target} ({len(waypoints)} waypoints)")
        self.nav_state = NavigationState.EXECUTING
        return True
    
    def _resolve_target(self, target: str) -> List[Waypoint]:
        """
        Resolve target string to waypoints.
        
        Args:
            target: Target specification
            
        Returns:
            List of waypoints
        """
        # Check for coordinate format "x,y"
        if "," in target:
            try:
                parts = target.split(",")
                x = float(parts[0].strip())
                y = float(parts[1].strip())
                return [Waypoint(x=x, y=y, name=f"coord_{x}_{y}")]
            except ValueError:
                pass
        
        # Check semantic locations
        target_lower = target.lower()
        if target_lower in self.SEMANTIC_LOCATIONS:
            x, y = self.SEMANTIC_LOCATIONS[target_lower]
            return [Waypoint(x=x, y=y, name=target_lower)]
        
        # Check for "to user" or "follow user"
        if "user" in target_lower:
            # Dynamic target - handled by follow mode
            return [Waypoint(x=0, y=0, name="user_dynamic")]
        
        # Try to infer from LAM
        waypoints = self._query_lam_for_target(target)
        if waypoints:
            return waypoints
        
        return []
    
    def _query_lam_for_target(self, target: str) -> Optional[List[Waypoint]]:
        """
        Query LAM planner for target resolution.
        
        Args:
            target: Target string
            
        Returns:
            Waypoints if LAM can resolve
        """
        try:
            from lam.lam_planner import plan_next_action
            
            symbolic_state = self.state.get_symbolic_state()
            result = plan_next_action(f"navigate to {target}", symbolic_state)
            
            # Parse LAM response for location hints
            # This is a stub - would be enhanced with actual LAM integration
            if "study" in result.lower():
                return [Waypoint(x=2.0, y=1.0, name="study_area")]
            
            return None
        except Exception as e:
            print(f"[NavigationPlanner] LAM query failed: {e}")
            return None
    
    def _notify_lam_planning(self, target: str) -> None:
        """Notify LAM system of navigation planning."""
        try:
            from lam.symbolic_state import symbolic_state
            symbolic_state["current_context"]["navigation_target"] = target
            symbolic_state["flags"]["is_navigating"] = True
        except Exception as e:
            print(f"[NavigationPlanner] LAM notification failed: {e}")
    
    def execute_step(self) -> None:
        """
        Execute one step of navigation.
        Called from main control loop.
        """
        if self.nav_state == NavigationState.IDLE:
            return
        
        if self.nav_state == NavigationState.FOLLOWING:
            self._execute_follow_step()
            return
        
        if self.nav_state != NavigationState.EXECUTING:
            return
        
        if not self.current_goal:
            self.nav_state = NavigationState.IDLE
            return
        
        # Check timeout
        elapsed = time.time() - self.current_goal.start_time
        if elapsed > self.current_goal.timeout:
            print("[NavigationPlanner] Navigation timeout")
            self.nav_state = NavigationState.FAILED
            self.motion.stop()
            return
        
        # Check for obstacles
        if self._check_obstacles():
            self._execute_avoidance()
            return
        
        # Get current waypoint
        if self.current_waypoint_index >= len(self.current_goal.waypoints):
            self._on_goal_reached()
            return
        
        waypoint = self.current_goal.waypoints[self.current_waypoint_index]
        
        # Navigate to waypoint
        from robotics.motion_controller import Pose2D
        target_pose = Pose2D(x=waypoint.x, y=waypoint.y)
        
        if self.motion.drive_to_pose(target_pose, tolerance=waypoint.tolerance):
            # Waypoint reached
            print(f"[NavigationPlanner] Reached waypoint: {waypoint.name or self.current_waypoint_index}")
            self.current_waypoint_index += 1
            
            # Record path
            self.path_history.append((waypoint.x, waypoint.y))
        
        # Update motion controller
        self.motion.update()
    
    def _check_obstacles(self) -> bool:
        """Check for obstacles in path."""
        front_dist = self.state.environmental.obstacle_front
        return front_dist < self.obstacle_threshold
    
    def _execute_avoidance(self) -> None:
        """Execute obstacle avoidance maneuver."""
        self.nav_state = NavigationState.AVOIDING
        
        left_dist = self.state.environmental.obstacle_left
        right_dist = self.state.environmental.obstacle_right
        
        # Choose direction based on available space
        if left_dist > right_dist:
            self.motion.turn_left(speed=0.8)
        else:
            self.motion.turn_right(speed=0.8)
        
        # After avoidance, return to executing
        self.nav_state = NavigationState.EXECUTING
    
    def _on_goal_reached(self) -> None:
        """Handle goal completion."""
        self.nav_state = NavigationState.ARRIVED
        self.motion.stop()
        
        # Update LAM state
        try:
            from lam.symbolic_state import symbolic_state
            symbolic_state["flags"]["is_navigating"] = False
            symbolic_state["history"].append(f"arrived at {self.current_goal.target}")
        except Exception:
            pass
        
        print(f"[NavigationPlanner] Arrived at: {self.current_goal.target}")
        
        # Perform arrival gesture
        self.motion.start_gesture("attention")
    
    def start_following(self, distance: float = 1.0) -> None:
        """
        Start following the user.
        
        Args:
            distance: Target following distance in meters
        """
        self.follow_distance = distance
        self.nav_state = NavigationState.FOLLOWING
        print(f"[NavigationPlanner] Following at {distance}m")
    
    def stop_following(self) -> None:
        """Stop following the user."""
        if self.nav_state == NavigationState.FOLLOWING:
            self.nav_state = NavigationState.IDLE
            self.motion.stop()
            print("[NavigationPlanner] Following stopped")
    
    def _execute_follow_step(self) -> None:
        """Execute one step of user-following behavior."""
        # Get user direction and distance from state
        user_direction = self.state.environmental.user_direction
        user_proximity = self.state.environmental.user_proximity
        
        # Estimate distance from proximity zone
        proximity_distances = {
            "contact": 0.1,
            "near": 0.5,
            "medium": 2.0,
            "far": 4.0,
            "unknown": 2.0
        }
        estimated_distance = proximity_distances.get(user_proximity, 2.0)
        
        # Calculate distance error
        distance_error = estimated_distance - self.follow_distance
        
        # Check for obstacles
        if self._check_obstacles():
            self.motion.stop()
            return
        
        # Control logic
        if abs(distance_error) < self.follow_tolerance:
            # At correct distance, match heading if we have direction
            if user_direction is not None:
                # Turn to face user's direction
                self.motion.set_velocity(0, 0.5 * user_direction)
            else:
                self.motion.stop()
        elif distance_error > 0:
            # Too far, move closer
            linear_vel = min(0.3, 0.2 * distance_error)
            angular_vel = 0.5 * (user_direction or 0)
            self.motion.set_velocity(linear_vel, angular_vel)
        else:
            # Too close, back up slightly
            self.motion.set_velocity(-0.1, 0)
        
        self.motion.update()
    
    def cancel(self) -> None:
        """Cancel current navigation."""
        self.current_goal = None
        self.current_waypoint_index = 0
        self.nav_state = NavigationState.IDLE
        self.motion.stop()
        
        try:
            from lam.symbolic_state import symbolic_state
            symbolic_state["flags"]["is_navigating"] = False
        except Exception:
            pass
        
        print("[NavigationPlanner] Navigation cancelled")
    
    def add_semantic_location(self, name: str, x: float, y: float) -> None:
        """
        Learn a new semantic location.
        
        Args:
            name: Location name
            x: X coordinate
            y: Y coordinate
        """
        self.SEMANTIC_LOCATIONS[name.lower()] = (x, y)
        print(f"[NavigationPlanner] Learned location: {name} at ({x}, {y})")
    
    def get_status(self) -> Dict[str, Any]:
        """Get navigation status."""
        status = {
            "state": self.nav_state.value,
            "current_goal": None,
            "waypoint_progress": 0,
            "known_locations": list(self.SEMANTIC_LOCATIONS.keys())
        }
        
        if self.current_goal:
            status["current_goal"] = self.current_goal.target
            status["waypoint_progress"] = (
                f"{self.current_waypoint_index}/{len(self.current_goal.waypoints)}"
            )
        
        return status
    
    def plan_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Waypoint]:
        """
        Plan a path between two points.
        
        Simple implementation - can be enhanced with A* or RRT.
        
        Args:
            start: Start coordinates
            end: End coordinates
            
        Returns:
            List of waypoints
        """
        # Simple direct path with intermediate waypoints
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        if distance < 0.5:
            # Short distance, direct path
            return [Waypoint(x=end[0], y=end[1])]
        
        # Add intermediate waypoints for longer paths
        num_waypoints = max(2, int(distance / 0.5))
        waypoints = []
        
        for i in range(1, num_waypoints + 1):
            t = i / num_waypoints
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            waypoints.append(Waypoint(x=x, y=y, name=f"wp_{i}"))
        
        return waypoints
