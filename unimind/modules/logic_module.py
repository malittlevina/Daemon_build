# unimind/modules/logic_module.py
"""
Logic Module - Deductive and inductive reasoning capabilities

Provides structured logical reasoning including:
- Propositional logic evaluation
- Syllogistic reasoning
- Causal inference
- Analogical reasoning
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class LogicalProposition:
    """A logical proposition that can be evaluated."""
    statement: str
    truth_value: Optional[bool] = None
    confidence: float = 0.5
    evidence: List[str] = None
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []


@dataclass 
class InferenceRule:
    """A rule for logical inference."""
    name: str
    pattern: str
    conclusion_template: str
    confidence_modifier: float = 1.0


class LogicModule:
    """
    Logic cognitive module for Unimind.
    
    Capabilities:
    - Pattern-based inference
    - Syllogistic reasoning
    - Causal chain analysis
    - Contradiction detection
    - Argument evaluation
    """
    
    name = "logic_module"
    
    def __init__(self):
        self.active = True
        self.knowledge_base: List[LogicalProposition] = []
        self.inference_rules: List[InferenceRule] = self._init_rules()
        self.inference_history: List[Dict] = []
    
    def _init_rules(self) -> List[InferenceRule]:
        """Initialize inference rules."""
        return [
            # Modus Ponens: If P then Q, P -> Q
            InferenceRule(
                name="modus_ponens",
                pattern=r"if\s+(.+?)\s+then\s+(.+)",
                conclusion_template="Given {0}, therefore {1}",
                confidence_modifier=0.9
            ),
            # Causal inference
            InferenceRule(
                name="causal",
                pattern=r"(.+?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(.+)",
                conclusion_template="{0} is a cause of {1}",
                confidence_modifier=0.8
            ),
            # Definition/classification
            InferenceRule(
                name="definition",
                pattern=r"(.+?)\s+(?:is\s+a|are)\s+(?:type\s+of\s+)?(.+)",
                conclusion_template="{0} belongs to category {1}",
                confidence_modifier=0.85
            ),
            # Necessity
            InferenceRule(
                name="necessity",
                pattern=r"(.+?)\s+(?:requires?|needs?|must\s+have)\s+(.+)",
                conclusion_template="{1} is necessary for {0}",
                confidence_modifier=0.8
            ),
            # Comparison
            InferenceRule(
                name="comparison",
                pattern=r"(.+?)\s+(?:is\s+(?:like|similar\s+to)|resembles?)\s+(.+)",
                conclusion_template="{0} shares properties with {1}",
                confidence_modifier=0.7
            ),
        ]
    
    def process(self, input_data: Any, context: Any) -> List[Any]:
        """
        Process input through logical reasoning.
        
        Returns list of Thought objects (using duck typing for compatibility).
        """
        from unimind.core import Thought
        
        thoughts = []
        input_str = str(input_data).lower()
        
        # Apply inference rules
        for rule in self.inference_rules:
            match = re.search(rule.pattern, input_str, re.IGNORECASE)
            if match:
                groups = match.groups()
                conclusion = rule.conclusion_template
                for i, group in enumerate(groups):
                    conclusion = conclusion.replace(f"{{{i}}}", group.strip())
                
                thoughts.append(Thought(
                    content=f"[Logic/{rule.name}] {conclusion}",
                    thought_type="inference",
                    confidence=0.7 * rule.confidence_modifier,
                    source_module="logic_module"
                ))
        
        # Check for logical patterns
        logical_patterns = self._analyze_logical_structure(input_str)
        for pattern, analysis in logical_patterns:
            thoughts.append(Thought(
                content=f"[Logic/structure] {analysis}",
                thought_type="observation",
                confidence=0.6,
                source_module="logic_module"
            ))
        
        # Check knowledge base for relevant facts
        relevant = self._query_knowledge_base(input_str)
        for prop in relevant[:3]:
            thoughts.append(Thought(
                content=f"[Logic/knowledge] Known fact: {prop.statement}",
                thought_type="memory",
                confidence=prop.confidence,
                source_module="logic_module"
            ))
        
        # Generate logical conclusion if possible
        if thoughts:
            conclusion = self._synthesize_conclusion(thoughts, input_str)
            if conclusion:
                thoughts.append(Thought(
                    content=f"[Logic/conclusion] {conclusion}",
                    thought_type="conclusion",
                    confidence=0.75,
                    source_module="logic_module"
                ))
        
        return thoughts
    
    def evaluate(self, thoughts: List[Any]) -> float:
        """Evaluate logical coherence of thoughts."""
        if not thoughts:
            return 0.0
        
        # Check for contradictions
        contradictions = self._find_contradictions(thoughts)
        contradiction_penalty = len(contradictions) * 0.1
        
        # Check inference chain quality
        inference_count = sum(1 for t in thoughts if t.thought_type == "inference")
        inference_bonus = min(0.2, inference_count * 0.05)
        
        # Base score from confidence
        avg_confidence = sum(t.confidence for t in thoughts) / len(thoughts)
        
        return max(0.0, min(1.0, avg_confidence + inference_bonus - contradiction_penalty))
    
    def _analyze_logical_structure(self, text: str) -> List[Tuple[str, str]]:
        """Analyze the logical structure of text."""
        patterns = []
        
        # Check for conditional statements
        if re.search(r'\bif\b.*\bthen\b', text):
            patterns.append(("conditional", "Contains conditional logic (if-then)"))
        
        # Check for quantifiers
        if re.search(r'\b(all|every|each|any|some|no|none)\b', text):
            patterns.append(("quantified", "Contains quantified statement"))
        
        # Check for negation
        if re.search(r'\b(not|never|no|cannot|won\'t|isn\'t|aren\'t)\b', text):
            patterns.append(("negation", "Contains negation"))
        
        # Check for comparison
        if re.search(r'\b(more|less|better|worse|same|different|equal)\b', text):
            patterns.append(("comparison", "Contains comparison"))
        
        # Check for causation
        if re.search(r'\b(because|therefore|thus|hence|so|consequently)\b', text):
            patterns.append(("causal", "Contains causal reasoning"))
        
        return patterns
    
    def _query_knowledge_base(self, query: str) -> List[LogicalProposition]:
        """Find relevant propositions from knowledge base."""
        query_words = set(query.lower().split())
        scored = []
        
        for prop in self.knowledge_base:
            prop_words = set(prop.statement.lower().split())
            overlap = len(query_words & prop_words)
            if overlap > 0:
                scored.append((overlap, prop))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        return [prop for _, prop in scored[:5]]
    
    def _find_contradictions(self, thoughts: List[Any]) -> List[Tuple[int, int]]:
        """Find contradictions between thoughts."""
        contradictions = []
        
        for i, t1 in enumerate(thoughts):
            for j, t2 in enumerate(thoughts[i+1:], start=i+1):
                if self._are_contradictory(t1.content, t2.content):
                    contradictions.append((i, j))
        
        return contradictions
    
    def _are_contradictory(self, s1: str, s2: str) -> bool:
        """Check if two statements contradict each other."""
        negations = ["not", "no", "never", "cannot", "won't", "isn't"]
        
        s1_negated = any(neg in s1.lower() for neg in negations)
        s2_negated = any(neg in s2.lower() for neg in negations)
        
        if s1_negated != s2_negated:
            words1 = set(s1.lower().split()) - set(negations)
            words2 = set(s2.lower().split()) - set(negations)
            return len(words1 & words2) >= 3
        
        return False
    
    def _synthesize_conclusion(self, thoughts: List[Any], original_input: str) -> Optional[str]:
        """Synthesize a logical conclusion from thoughts."""
        inferences = [t for t in thoughts if t.thought_type == "inference"]
        
        if not inferences:
            return None
        
        # Combine top inferences
        top_inferences = sorted(inferences, key=lambda t: t.confidence, reverse=True)[:2]
        
        if len(top_inferences) == 1:
            return f"Based on logical analysis: {top_inferences[0].content}"
        else:
            return f"Logical synthesis: {top_inferences[0].content}; furthermore, {top_inferences[1].content}"
    
    def add_knowledge(self, statement: str, confidence: float = 0.8):
        """Add a proposition to the knowledge base."""
        self.knowledge_base.append(LogicalProposition(
            statement=statement,
            confidence=confidence
        ))
    
    def reason_syllogistically(
        self,
        major_premise: str,
        minor_premise: str
    ) -> Optional[str]:
        """
        Perform syllogistic reasoning.
        
        Example:
            major: "All humans are mortal"
            minor: "Socrates is a human"
            conclusion: "Socrates is mortal"
        """
        # Extract subject and predicate from major premise
        major_match = re.match(
            r"(?:all|every)\s+(\w+)\s+(?:is|are)\s+(.+)",
            major_premise.lower()
        )
        if not major_match:
            return None
        
        category = major_match.group(1)
        predicate = major_match.group(2)
        
        # Check if minor premise assigns to category
        minor_match = re.match(
            r"(\w+)\s+(?:is|are)\s+(?:a\s+)?(\w+)",
            minor_premise.lower()
        )
        if not minor_match:
            return None
        
        subject = minor_match.group(1)
        assigned_category = minor_match.group(2)
        
        # If categories match, derive conclusion
        if category in assigned_category or assigned_category in category:
            conclusion = f"{subject.capitalize()} is {predicate}"
            
            self.inference_history.append({
                "type": "syllogism",
                "major": major_premise,
                "minor": minor_premise,
                "conclusion": conclusion,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return conclusion
        
        return None
