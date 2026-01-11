# unimind/modules/ethics_module.py
"""
Ethics Module - Ethical reasoning and value alignment

Provides ethical awareness and constraint checking:
- Value-based evaluation
- Harm assessment
- Fairness checking
- Transparency enforcement
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class EthicalPrinciple(Enum):
    """Core ethical principles."""
    BENEFICENCE = "beneficence"          # Do good
    NON_MALEFICENCE = "non_maleficence"  # Do no harm
    AUTONOMY = "autonomy"                 # Respect user agency
    JUSTICE = "justice"                   # Fairness and equality
    TRANSPARENCY = "transparency"         # Honesty and openness
    PRIVACY = "privacy"                   # Protect personal information
    ACCOUNTABILITY = "accountability"     # Take responsibility


@dataclass
class EthicalConcern:
    """An identified ethical concern."""
    principle: EthicalPrinciple
    description: str
    severity: float  # 0.0 to 1.0
    recommendation: str
    context: str


@dataclass
class EthicalGuideline:
    """A specific ethical guideline or constraint."""
    name: str
    description: str
    principle: EthicalPrinciple
    check_pattern: str  # Regex pattern to detect relevant content
    action: str  # warn, block, modify
    

class EthicsModule:
    """
    Ethics cognitive module for Unimind.
    
    Capabilities:
    - Ethical principle evaluation
    - Harm detection and prevention
    - Fairness assessment
    - Value alignment checking
    - Ethical constraint enforcement
    """
    
    name = "ethics_module"
    
    # Harm-related keywords
    HARM_INDICATORS = {
        "high": ["kill", "harm", "attack", "destroy", "hurt", "damage", "weapon", "exploit", "abuse"],
        "medium": ["hack", "bypass", "circumvent", "steal", "manipulate", "deceive", "trick"],
        "low": ["criticize", "judge", "blame", "exclude", "ignore"]
    }
    
    # Privacy-related keywords
    PRIVACY_INDICATORS = [
        "password", "credit card", "social security", "ssn", "private",
        "personal", "secret", "confidential", "sensitive"
    ]
    
    def __init__(self):
        self.active = True
        self.principles = list(EthicalPrinciple)
        self.guidelines: List[EthicalGuideline] = self._init_guidelines()
        self.concern_history: List[EthicalConcern] = []
        self.evaluation_history: List[Dict] = []
    
    def _init_guidelines(self) -> List[EthicalGuideline]:
        """Initialize default ethical guidelines."""
        return [
            EthicalGuideline(
                name="no_harm_instructions",
                description="Do not provide instructions that could cause harm",
                principle=EthicalPrinciple.NON_MALEFICENCE,
                check_pattern=r"how\s+to\s+(?:hack|attack|harm|kill|steal)",
                action="block"
            ),
            EthicalGuideline(
                name="protect_privacy",
                description="Do not request or expose private information",
                principle=EthicalPrinciple.PRIVACY,
                check_pattern=r"(?:what\s+is|tell\s+me)\s+(?:your|their)\s+(?:password|ssn|credit)",
                action="block"
            ),
            EthicalGuideline(
                name="maintain_honesty",
                description="Do not generate false or misleading information",
                principle=EthicalPrinciple.TRANSPARENCY,
                check_pattern=r"(?:pretend|lie|deceive|fake|fabricate)",
                action="warn"
            ),
            EthicalGuideline(
                name="respect_autonomy",
                description="Respect user's right to make their own decisions",
                principle=EthicalPrinciple.AUTONOMY,
                check_pattern=r"(?:you\s+must|you\s+should\s+always|never\s+do)",
                action="warn"
            ),
            EthicalGuideline(
                name="ensure_fairness",
                description="Avoid biased or discriminatory content",
                principle=EthicalPrinciple.JUSTICE,
                check_pattern=r"(?:all|every)\s+(?:\w+)\s+(?:are|is)\s+(?:bad|stupid|inferior)",
                action="block"
            )
        ]
    
    def process(self, input_data: Any, context: Any) -> List[Any]:
        """
        Process input through ethical reasoning.
        
        Returns list of Thought objects.
        """
        from unimind.core import Thought
        
        thoughts = []
        input_str = str(input_data).lower()
        
        # Check guidelines
        guideline_violations = self._check_guidelines(input_str)
        for guideline, match in guideline_violations:
            severity = 0.9 if guideline.action == "block" else 0.6
            thoughts.append(Thought(
                content=f"[Ethics/{guideline.principle.value}] Guideline '{guideline.name}': {guideline.description}",
                thought_type="observation",
                confidence=severity,
                source_module="ethics_module"
            ))
            
            if guideline.action == "block":
                thoughts.append(Thought(
                    content=f"[Ethics/action] BLOCK recommended: This request may violate ethical guidelines",
                    thought_type="conclusion",
                    confidence=0.95,
                    source_module="ethics_module"
                ))
        
        # Harm assessment
        harm_level, harm_details = self._assess_harm(input_str)
        if harm_level:
            thoughts.append(Thought(
                content=f"[Ethics/harm] {harm_level.upper()} harm potential: {harm_details}",
                thought_type="observation",
                confidence={"high": 0.9, "medium": 0.7, "low": 0.5}.get(harm_level, 0.5),
                source_module="ethics_module"
            ))
        
        # Privacy check
        privacy_concerns = self._check_privacy(input_str)
        for concern in privacy_concerns:
            thoughts.append(Thought(
                content=f"[Ethics/privacy] Privacy concern: {concern}",
                thought_type="observation",
                confidence=0.8,
                source_module="ethics_module"
            ))
        
        # Positive ethics - check for beneficial intent
        beneficial = self._check_beneficial(input_str)
        if beneficial:
            thoughts.append(Thought(
                content=f"[Ethics/beneficence] Positive intent detected: {beneficial}",
                thought_type="observation",
                confidence=0.7,
                source_module="ethics_module"
            ))
        
        # Ethical recommendation
        if thoughts:
            recommendation = self._generate_recommendation(thoughts, input_str)
            thoughts.append(Thought(
                content=f"[Ethics/guidance] {recommendation}",
                thought_type="inference",
                confidence=0.75,
                source_module="ethics_module"
            ))
        
        # Record evaluation
        self._record_evaluation(input_str, thoughts)
        
        return thoughts
    
    def evaluate(self, thoughts: List[Any]) -> float:
        """Evaluate ethical quality of reasoning."""
        if not thoughts:
            return 0.8  # Neutral is okay
        
        ethics_thoughts = [t for t in thoughts if "ethics" in t.source_module.lower()]
        
        if not ethics_thoughts:
            return 0.7  # No ethical concerns raised
        
        # Check for blocks
        blocks = [t for t in ethics_thoughts if "BLOCK" in t.content]
        if blocks:
            return 0.1  # Serious ethical concern
        
        # Check for warnings
        warnings = [t for t in ethics_thoughts if "warn" in t.content.lower() or "concern" in t.content.lower()]
        warning_penalty = len(warnings) * 0.1
        
        # Check for positive ethics
        positives = [t for t in ethics_thoughts if "beneficence" in t.content.lower()]
        positive_bonus = len(positives) * 0.1
        
        return max(0.2, min(1.0, 0.8 - warning_penalty + positive_bonus))
    
    def _check_guidelines(
        self,
        text: str
    ) -> List[Tuple[EthicalGuideline, str]]:
        """Check text against ethical guidelines."""
        violations = []
        
        for guideline in self.guidelines:
            match = re.search(guideline.check_pattern, text, re.IGNORECASE)
            if match:
                violations.append((guideline, match.group()))
        
        return violations
    
    def _assess_harm(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Assess potential harm level in text."""
        for level, indicators in self.HARM_INDICATORS.items():
            for indicator in indicators:
                if indicator in text:
                    return level, f"Contains '{indicator}'"
        
        return None, None
    
    def _check_privacy(self, text: str) -> List[str]:
        """Check for privacy concerns."""
        concerns = []
        
        for indicator in self.PRIVACY_INDICATORS:
            if indicator in text:
                concerns.append(f"References to '{indicator}' detected")
        
        # Check for patterns that might be sensitive data
        if re.search(r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b', text):
            concerns.append("Possible SSN pattern detected")
        
        if re.search(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', text):
            concerns.append("Possible credit card number detected")
        
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            concerns.append("Email address detected - consider privacy")
        
        return concerns
    
    def _check_beneficial(self, text: str) -> Optional[str]:
        """Check for beneficial/positive intent."""
        beneficial_patterns = [
            (r"help|assist|support", "Intent to help"),
            (r"learn|understand|improve", "Educational purpose"),
            (r"protect|secure|safe", "Safety-focused"),
            (r"create|build|make.*positive", "Creative/constructive"),
            (r"thank|appreciate|grateful", "Gratitude expressed")
        ]
        
        for pattern, description in beneficial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return description
        
        return None
    
    def _generate_recommendation(
        self,
        thoughts: List[Any],
        original_input: str
    ) -> str:
        """Generate an ethical recommendation."""
        # Check severity of concerns
        high_concerns = [t for t in thoughts if t.confidence > 0.8 and "BLOCK" not in t.content]
        blocks = [t for t in thoughts if "BLOCK" in t.content]
        
        if blocks:
            return "This request should be declined due to ethical concerns. Consider redirecting to appropriate resources."
        
        if high_concerns:
            return "Proceed with caution. Ensure response adheres to ethical guidelines and avoids potential harms."
        
        return "No major ethical concerns detected. Proceed with standard ethical awareness."
    
    def _record_evaluation(self, input_text: str, thoughts: List[Any]):
        """Record ethical evaluation for analysis."""
        self.evaluation_history.append({
            "input_preview": input_text[:50],
            "concern_count": len([t for t in thoughts if "concern" in t.content.lower() or "BLOCK" in t.content]),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if len(self.evaluation_history) > 200:
            self.evaluation_history = self.evaluation_history[-200:]
    
    def add_guideline(
        self,
        name: str,
        description: str,
        principle: EthicalPrinciple,
        pattern: str,
        action: str = "warn"
    ):
        """Add a new ethical guideline."""
        self.guidelines.append(EthicalGuideline(
            name=name,
            description=description,
            principle=principle,
            check_pattern=pattern,
            action=action
        ))
    
    def get_principles(self) -> List[str]:
        """Get list of ethical principles."""
        return [p.value for p in self.principles]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ethics module statistics."""
        return {
            "guidelines_count": len(self.guidelines),
            "evaluations_count": len(self.evaluation_history),
            "concern_history_size": len(self.concern_history)
        }
