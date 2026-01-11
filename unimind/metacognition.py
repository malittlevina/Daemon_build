# unimind/metacognition.py
"""
Metacognition - Thinking about thinking

Provides meta-level cognitive monitoring and control:
- Self-monitoring of reasoning quality
- Strategy selection and adjustment
- Confidence calibration
- Learning from reasoning outcomes
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import statistics


class MetacognitiveState(Enum):
    """States of metacognitive awareness."""
    MONITORING = "monitoring"   # Passively observing
    EVALUATING = "evaluating"   # Actively assessing
    ADJUSTING = "adjusting"     # Making changes
    REFLECTING = "reflecting"   # Deep analysis


class StrategyType(Enum):
    """Types of cognitive strategies."""
    ANALYTICAL = "analytical"       # Step-by-step logic
    HEURISTIC = "heuristic"        # Quick rules of thumb
    CREATIVE = "creative"          # Divergent exploration
    SYSTEMATIC = "systematic"      # Exhaustive search
    ANALOGICAL = "analogical"      # Compare to known cases
    DECOMPOSITION = "decomposition" # Break into parts


@dataclass
class ReasoningOutcome:
    """Records the outcome of a reasoning attempt."""
    query: str
    strategy_used: StrategyType
    confidence: float
    was_successful: Optional[bool] = None
    feedback: Optional[str] = None
    duration_ms: float = 0
    thought_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StrategyProfile:
    """Profile of a cognitive strategy."""
    strategy: StrategyType
    usage_count: int = 0
    success_count: int = 0
    total_confidence: float = 0
    avg_duration_ms: float = 0
    best_contexts: List[str] = field(default_factory=list)


@dataclass
class CalibrationData:
    """Data for confidence calibration."""
    confidence_bucket: float  # 0.0-0.1, 0.1-0.2, etc.
    predictions: int = 0
    correct: int = 0
    
    @property
    def accuracy(self) -> float:
        return self.correct / self.predictions if self.predictions > 0 else 0.5


class MetacognitiveMonitor:
    """
    Monitors and controls cognitive processes at a meta level.
    
    Capabilities:
    - Track reasoning quality over time
    - Calibrate confidence levels
    - Select optimal strategies
    - Detect reasoning failures
    - Learn from outcomes
    """
    
    def __init__(self):
        self._state = MetacognitiveState.MONITORING
        self._lock = threading.RLock()
        
        # Outcome tracking
        self._outcomes: List[ReasoningOutcome] = []
        self._max_outcomes = 500
        
        # Strategy profiles
        self._strategy_profiles: Dict[StrategyType, StrategyProfile] = {
            st: StrategyProfile(strategy=st) for st in StrategyType
        }
        
        # Confidence calibration
        self._calibration: Dict[int, CalibrationData] = {
            i: CalibrationData(confidence_bucket=i/10) for i in range(10)
        }
        
        # Current reasoning context
        self._current_reasoning: Optional[Dict] = None
        
        # Meta-level insights
        self._insights: List[Dict] = []
        
        # Thresholds
        self._confidence_threshold = 0.4  # Minimum acceptable confidence
        self._quality_threshold = 0.6     # Minimum reasoning quality
    
    def start_monitoring(self, query: str, strategy: StrategyType):
        """Start monitoring a reasoning process."""
        with self._lock:
            self._state = MetacognitiveState.MONITORING
            self._current_reasoning = {
                "query": query,
                "strategy": strategy,
                "start_time": datetime.utcnow(),
                "checkpoints": [],
                "warnings": []
            }
    
    def checkpoint(self, stage: str, quality: float, notes: str = ""):
        """Record a checkpoint during reasoning."""
        with self._lock:
            if self._current_reasoning:
                self._current_reasoning["checkpoints"].append({
                    "stage": stage,
                    "quality": quality,
                    "notes": notes,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Check for issues
                if quality < self._quality_threshold:
                    self._current_reasoning["warnings"].append(
                        f"Low quality at {stage}: {quality:.2f}"
                    )
    
    def end_monitoring(
        self,
        confidence: float,
        thought_count: int
    ) -> Dict[str, Any]:
        """End monitoring and record outcome."""
        with self._lock:
            if not self._current_reasoning:
                return {"error": "No active reasoning to end"}
            
            duration = (datetime.utcnow() - self._current_reasoning["start_time"]).total_seconds() * 1000
            
            outcome = ReasoningOutcome(
                query=self._current_reasoning["query"],
                strategy_used=self._current_reasoning["strategy"],
                confidence=confidence,
                duration_ms=duration,
                thought_count=thought_count
            )
            
            self._outcomes.append(outcome)
            if len(self._outcomes) > self._max_outcomes:
                self._outcomes = self._outcomes[-self._max_outcomes:]
            
            # Update strategy profile
            profile = self._strategy_profiles[outcome.strategy_used]
            profile.usage_count += 1
            profile.total_confidence += confidence
            profile.avg_duration_ms = (
                (profile.avg_duration_ms * (profile.usage_count - 1) + duration) 
                / profile.usage_count
            )
            
            # Record for calibration
            bucket = int(min(9, confidence * 10))
            self._calibration[bucket].predictions += 1
            
            result = {
                "duration_ms": duration,
                "checkpoints": self._current_reasoning["checkpoints"],
                "warnings": self._current_reasoning["warnings"],
                "strategy": outcome.strategy_used.value,
                "confidence": confidence
            }
            
            self._current_reasoning = None
            self._state = MetacognitiveState.MONITORING
            
            return result
    
    def record_feedback(self, was_successful: bool, feedback: str = ""):
        """Record feedback on the most recent reasoning."""
        with self._lock:
            if self._outcomes:
                outcome = self._outcomes[-1]
                outcome.was_successful = was_successful
                outcome.feedback = feedback
                
                # Update strategy success rate
                profile = self._strategy_profiles[outcome.strategy_used]
                if was_successful:
                    profile.success_count += 1
                
                # Update calibration
                bucket = int(min(9, outcome.confidence * 10))
                if was_successful:
                    self._calibration[bucket].correct += 1
    
    def select_strategy(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Tuple[StrategyType, float]:
        """
        Select the best strategy for a query.
        
        Returns (strategy, confidence in selection).
        """
        with self._lock:
            self._state = MetacognitiveState.EVALUATING
            
            # Score each strategy
            scores: Dict[StrategyType, float] = {}
            
            for strategy, profile in self._strategy_profiles.items():
                # Base score from success rate
                if profile.usage_count > 0:
                    success_rate = profile.success_count / profile.usage_count
                    avg_confidence = profile.total_confidence / profile.usage_count
                    base_score = success_rate * 0.6 + avg_confidence * 0.4
                else:
                    base_score = 0.5  # Unknown, give neutral score
                
                # Context matching
                context_bonus = 0
                if context:
                    for ctx in profile.best_contexts:
                        if ctx in str(context).lower():
                            context_bonus += 0.1
                
                # Query pattern matching
                query_lower = query.lower()
                pattern_bonus = 0
                
                if strategy == StrategyType.ANALYTICAL:
                    if any(w in query_lower for w in ["analyze", "explain", "why", "how"]):
                        pattern_bonus = 0.2
                        
                elif strategy == StrategyType.CREATIVE:
                    if any(w in query_lower for w in ["create", "imagine", "design", "invent"]):
                        pattern_bonus = 0.2
                        
                elif strategy == StrategyType.SYSTEMATIC:
                    if any(w in query_lower for w in ["all", "every", "complete", "comprehensive"]):
                        pattern_bonus = 0.2
                        
                elif strategy == StrategyType.ANALOGICAL:
                    if any(w in query_lower for w in ["like", "similar", "compare", "example"]):
                        pattern_bonus = 0.2
                        
                elif strategy == StrategyType.HEURISTIC:
                    if any(w in query_lower for w in ["quick", "fast", "simple", "basic"]):
                        pattern_bonus = 0.2
                        
                elif strategy == StrategyType.DECOMPOSITION:
                    if any(w in query_lower for w in ["complex", "parts", "steps", "break down"]):
                        pattern_bonus = 0.2
                
                scores[strategy] = base_score + context_bonus + pattern_bonus
            
            # Select best strategy
            best_strategy = max(scores.items(), key=lambda x: x[1])
            
            self._state = MetacognitiveState.MONITORING
            return best_strategy[0], best_strategy[1]
    
    def calibrate_confidence(self, raw_confidence: float) -> float:
        """Calibrate confidence based on historical accuracy."""
        bucket = int(min(9, raw_confidence * 10))
        calibration = self._calibration[bucket]
        
        if calibration.predictions < 5:
            return raw_confidence  # Not enough data
        
        # Adjust based on historical accuracy
        accuracy = calibration.accuracy
        expected_accuracy = (bucket + 0.5) / 10
        
        # If we're overconfident, reduce; if underconfident, increase
        adjustment = (accuracy - expected_accuracy) * 0.3
        calibrated = raw_confidence + adjustment
        
        return max(0.1, min(0.95, calibrated))
    
    def detect_issues(self) -> List[str]:
        """Detect issues in recent reasoning."""
        issues = []
        
        with self._lock:
            if len(self._outcomes) < 5:
                return issues
            
            recent = self._outcomes[-10:]
            
            # Check for declining confidence
            confidences = [o.confidence for o in recent]
            if len(confidences) >= 5:
                recent_avg = statistics.mean(confidences[-5:])
                older_avg = statistics.mean(confidences[:5])
                if recent_avg < older_avg - 0.15:
                    issues.append("Confidence declining over recent queries")
            
            # Check for repeated failures
            if all(o.was_successful == False for o in recent[-3:] if o.was_successful is not None):
                issues.append("Multiple consecutive failures detected")
            
            # Check for strategy over-reliance
            recent_strategies = [o.strategy_used for o in recent]
            if len(set(recent_strategies)) == 1 and len(recent_strategies) >= 5:
                issues.append(f"Over-reliance on {recent_strategies[0].value} strategy")
            
            # Check calibration
            for bucket, cal in self._calibration.items():
                if cal.predictions >= 10:
                    expected = (bucket + 0.5) / 10
                    if abs(cal.accuracy - expected) > 0.2:
                        issues.append(f"Confidence miscalibration in {bucket*10}-{(bucket+1)*10}% range")
        
        return issues
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate metacognitive insights."""
        insights = []
        
        with self._lock:
            self._state = MetacognitiveState.REFLECTING
            
            # Strategy effectiveness
            for strategy, profile in self._strategy_profiles.items():
                if profile.usage_count >= 5:
                    success_rate = profile.success_count / profile.usage_count
                    insights.append({
                        "type": "strategy_effectiveness",
                        "strategy": strategy.value,
                        "success_rate": success_rate,
                        "usage_count": profile.usage_count,
                        "recommendation": "Use more" if success_rate > 0.7 else "Use with caution"
                    })
            
            # Confidence calibration
            total_predictions = sum(c.predictions for c in self._calibration.values())
            if total_predictions >= 20:
                overall_accuracy = sum(c.correct for c in self._calibration.values()) / total_predictions
                insights.append({
                    "type": "calibration",
                    "overall_accuracy": overall_accuracy,
                    "recommendation": "Well calibrated" if 0.4 < overall_accuracy < 0.7 else "Needs calibration adjustment"
                })
            
            # Reasoning patterns
            if self._outcomes:
                avg_duration = statistics.mean(o.duration_ms for o in self._outcomes)
                avg_thoughts = statistics.mean(o.thought_count for o in self._outcomes)
                insights.append({
                    "type": "reasoning_patterns",
                    "avg_duration_ms": avg_duration,
                    "avg_thought_count": avg_thoughts
                })
            
            # Issues
            issues = self.detect_issues()
            if issues:
                insights.append({
                    "type": "detected_issues",
                    "issues": issues
                })
            
            self._state = MetacognitiveState.MONITORING
        
        return insights
    
    def get_strategy_recommendation(self) -> Dict[str, Any]:
        """Get recommendation for strategy improvement."""
        with self._lock:
            # Find underused but successful strategies
            recommendations = []
            
            total_usage = sum(p.usage_count for p in self._strategy_profiles.values())
            if total_usage < 10:
                return {"message": "Not enough data for recommendations"}
            
            for strategy, profile in self._strategy_profiles.items():
                usage_rate = profile.usage_count / total_usage
                if profile.usage_count > 0:
                    success_rate = profile.success_count / profile.usage_count
                    if success_rate > 0.6 and usage_rate < 0.15:
                        recommendations.append({
                            "strategy": strategy.value,
                            "message": f"Consider using more - high success rate ({success_rate:.0%}) but low usage ({usage_rate:.0%})"
                        })
            
            return {
                "recommendations": recommendations,
                "current_best": max(
                    self._strategy_profiles.items(),
                    key=lambda x: x[1].success_count / max(1, x[1].usage_count)
                )[0].value
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current metacognitive state."""
        with self._lock:
            return {
                "state": self._state.value,
                "total_outcomes": len(self._outcomes),
                "strategies": {
                    s.value: {
                        "usage": p.usage_count,
                        "success_rate": p.success_count / max(1, p.usage_count)
                    }
                    for s, p in self._strategy_profiles.items()
                },
                "recent_issues": self.detect_issues()
            }
