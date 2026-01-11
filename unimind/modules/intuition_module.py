# unimind/modules/intuition_module.py
"""
Intuition Module - Pattern-based rapid cognition

Provides fast, heuristic-based reasoning:
- Pattern recognition
- Gut-feel assessments
- Rapid categorization
- Anomaly detection
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import random


@dataclass
class Pattern:
    """A learned pattern for intuitive recognition."""
    pattern_type: str
    signature: str
    frequency: int = 1
    success_rate: float = 0.5
    last_matched: Optional[datetime] = None
    examples: List[str] = field(default_factory=list)


class IntuitionModule:
    """
    Intuition cognitive module for Unimind.
    
    Capabilities:
    - Fast pattern matching
    - Heuristic judgments
    - "Gut feeling" assessments
    - Anomaly detection
    - Rapid categorization
    """
    
    name = "intuition_module"
    
    # Common patterns for quick recognition
    QUICK_PATTERNS = {
        "question": {
            "indicators": ["?", "what", "how", "why", "when", "where", "who", "which"],
            "response_hint": "inquiry_mode"
        },
        "command": {
            "indicators": ["do", "make", "create", "build", "run", "execute", "start", "stop"],
            "response_hint": "action_mode"
        },
        "exploration": {
            "indicators": ["learn", "understand", "explore", "discover", "find out", "research"],
            "response_hint": "learning_mode"
        },
        "problem": {
            "indicators": ["error", "issue", "problem", "bug", "broken", "fix", "help", "wrong"],
            "response_hint": "problem_solving_mode"
        },
        "creative": {
            "indicators": ["imagine", "design", "invent", "brainstorm", "creative", "new idea"],
            "response_hint": "creative_mode"
        },
        "social": {
            "indicators": ["feel", "think about", "opinion", "believe", "hope", "wish"],
            "response_hint": "empathetic_mode"
        }
    }
    
    def __init__(self):
        self.active = True
        self.learned_patterns: List[Pattern] = []
        self.intuition_history: List[Dict] = []
        self.confidence_calibration = 1.0  # Adjust based on accuracy
    
    def process(self, input_data: Any, context: Any) -> List[Any]:
        """
        Process input using intuitive reasoning.
        
        Returns list of Thought objects.
        """
        from unimind.core import Thought
        
        thoughts = []
        input_str = str(input_data).lower()
        
        # Quick pattern recognition
        quick_assessment = self._quick_pattern_match(input_str)
        if quick_assessment:
            pattern_type, hint, confidence = quick_assessment
            thoughts.append(Thought(
                content=f"[Intuition/quick] Pattern: {pattern_type} → Suggested mode: {hint}",
                thought_type="intuition",
                confidence=confidence * self.confidence_calibration,
                source_module="intuition_module"
            ))
        
        # Anomaly detection
        anomalies = self._detect_anomalies(input_str, context)
        for anomaly, severity in anomalies:
            thoughts.append(Thought(
                content=f"[Intuition/anomaly] {anomaly}",
                thought_type="observation",
                confidence=0.6 * severity,
                source_module="intuition_module"
            ))
        
        # Learned pattern matching
        learned_matches = self._match_learned_patterns(input_str)
        for pattern, match_strength in learned_matches[:2]:
            thoughts.append(Thought(
                content=f"[Intuition/learned] Matches pattern '{pattern.pattern_type}' (success rate: {pattern.success_rate:.0%})",
                thought_type="intuition",
                confidence=match_strength * pattern.success_rate,
                source_module="intuition_module"
            ))
        
        # Gut feeling assessment
        gut_feeling = self._gut_assessment(input_str, context)
        if gut_feeling:
            thoughts.append(Thought(
                content=f"[Intuition/gut] {gut_feeling}",
                thought_type="intuition",
                confidence=0.5,  # Gut feelings are inherently uncertain
                source_module="intuition_module"
            ))
        
        # Category suggestion
        category = self._rapid_categorize(input_str)
        if category:
            thoughts.append(Thought(
                content=f"[Intuition/category] This seems to be about: {category}",
                thought_type="observation",
                confidence=0.65,
                source_module="intuition_module"
            ))
        
        # Record for learning
        self._record_intuition(input_str, thoughts)
        
        return thoughts
    
    def evaluate(self, thoughts: List[Any]) -> float:
        """Evaluate intuition quality."""
        if not thoughts:
            return 0.5
        
        intuition_thoughts = [t for t in thoughts if "intuition" in t.source_module.lower()]
        
        if not intuition_thoughts:
            return 0.4
        
        # Intuition is valuable when it provides quick insights
        avg_confidence = sum(t.confidence for t in intuition_thoughts) / len(intuition_thoughts)
        
        # Adjust for calibration
        return avg_confidence * self.confidence_calibration
    
    def _quick_pattern_match(
        self,
        text: str
    ) -> Optional[Tuple[str, str, float]]:
        """Perform quick pattern matching."""
        best_match = None
        best_score = 0
        
        for pattern_type, config in self.QUICK_PATTERNS.items():
            score = 0
            for indicator in config["indicators"]:
                if indicator in text:
                    score += 1
            
            # Normalize by number of indicators
            score = score / len(config["indicators"]) if config["indicators"] else 0
            
            if score > best_score:
                best_score = score
                best_match = (pattern_type, config["response_hint"], score)
        
        return best_match if best_score > 0.1 else None
    
    def _detect_anomalies(
        self,
        text: str,
        context: Any
    ) -> List[Tuple[str, float]]:
        """Detect anomalies or unusual patterns."""
        anomalies = []
        
        # Check for unusual length
        if len(text) > 500:
            anomalies.append(("Unusually long input - may require chunking", 0.7))
        elif len(text) < 5:
            anomalies.append(("Very short input - may need clarification", 0.6))
        
        # Check for mixed signals
        positive = any(w in text for w in ["good", "great", "love", "happy"])
        negative = any(w in text for w in ["bad", "hate", "sad", "angry"])
        if positive and negative:
            anomalies.append(("Mixed emotional signals detected", 0.8))
        
        # Check for urgency markers
        if any(w in text for w in ["urgent", "asap", "immediately", "now", "hurry"]):
            anomalies.append(("Urgency detected - prioritize response", 0.9))
        
        # Check for complexity markers
        if text.count(" and ") > 3 or text.count(",") > 5:
            anomalies.append(("Complex multi-part request detected", 0.7))
        
        return anomalies
    
    def _match_learned_patterns(
        self,
        text: str
    ) -> List[Tuple[Pattern, float]]:
        """Match against learned patterns."""
        matches = []
        
        for pattern in self.learned_patterns:
            # Simple substring matching for signature
            if pattern.signature.lower() in text:
                match_strength = 0.8
            else:
                # Check examples
                example_matches = sum(
                    1 for ex in pattern.examples
                    if any(word in text for word in ex.lower().split())
                )
                match_strength = min(0.6, example_matches * 0.15)
            
            if match_strength > 0.2:
                matches.append((pattern, match_strength))
                pattern.frequency += 1
                pattern.last_matched = datetime.utcnow()
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
    
    def _gut_assessment(self, text: str, context: Any) -> Optional[str]:
        """Generate a gut feeling assessment."""
        # Simulate intuitive assessment based on various heuristics
        
        word_count = len(text.split())
        question_marks = text.count("?")
        
        if question_marks > 2:
            return "Multiple questions suggest uncertainty - may need step-by-step guidance"
        
        if word_count > 50:
            return "Detailed input suggests thorough response expected"
        
        if any(w in text.lower() for w in ["confused", "lost", "stuck", "don't understand"]):
            return "User may be frustrated - consider simpler explanation"
        
        if any(w in text.lower() for w in ["thanks", "please", "appreciate"]):
            return "Polite tone - user is being collaborative"
        
        return None
    
    def _rapid_categorize(self, text: str) -> Optional[str]:
        """Rapidly categorize the input."""
        categories = {
            "technical": ["code", "programming", "function", "error", "debug", "api", "database"],
            "learning": ["learn", "understand", "explain", "how does", "what is", "teach"],
            "creative": ["create", "design", "build", "imagine", "story", "write"],
            "analysis": ["analyze", "compare", "evaluate", "review", "assess"],
            "planning": ["plan", "schedule", "organize", "prepare", "strategy"],
            "personal": ["feel", "think", "believe", "want", "need", "prefer"]
        }
        
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for kw in keywords if kw in text.lower())
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _record_intuition(self, input_text: str, thoughts: List[Any]):
        """Record intuition for future learning."""
        self.intuition_history.append({
            "input": input_text[:100],
            "thought_count": len(thoughts),
            "avg_confidence": sum(t.confidence for t in thoughts) / len(thoughts) if thoughts else 0,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep history bounded
        if len(self.intuition_history) > 200:
            self.intuition_history = self.intuition_history[-200:]
    
    def learn_pattern(
        self,
        pattern_type: str,
        signature: str,
        examples: List[str] = None
    ):
        """Learn a new intuitive pattern."""
        pattern = Pattern(
            pattern_type=pattern_type,
            signature=signature,
            examples=examples or []
        )
        self.learned_patterns.append(pattern)
    
    def update_calibration(self, was_correct: bool):
        """Update confidence calibration based on feedback."""
        if was_correct:
            self.confidence_calibration = min(1.2, self.confidence_calibration + 0.02)
        else:
            self.confidence_calibration = max(0.5, self.confidence_calibration - 0.05)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get intuition module statistics."""
        return {
            "learned_patterns": len(self.learned_patterns),
            "history_size": len(self.intuition_history),
            "confidence_calibration": self.confidence_calibration
        }
