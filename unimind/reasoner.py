# unimind/reasoner.py
"""
Symbolic Reasoner - Chain-of-thought reasoning with symbolic representations

This module provides structured reasoning capabilities that can:
- Build reasoning chains step-by-step
- Apply logical rules and constraints
- Generate hypotheses and test them
- Produce explainable conclusions
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class ReasoningStep(Enum):
    """Types of reasoning steps."""
    OBSERVATION = "observation"     # Initial input/perception
    DECOMPOSITION = "decomposition" # Breaking down complex problems
    HYPOTHESIS = "hypothesis"       # Proposed explanation
    INFERENCE = "inference"         # Logical conclusion from premises
    ANALOGY = "analogy"            # Similarity-based reasoning
    CONTRADICTION = "contradiction" # Identified inconsistency
    SYNTHESIS = "synthesis"        # Combining multiple insights
    CONCLUSION = "conclusion"      # Final determination


@dataclass
class ReasoningNode:
    """A single step in a reasoning chain."""
    step_type: ReasoningStep
    content: str
    confidence: float = 0.7
    premises: List[str] = field(default_factory=list)
    rule_applied: Optional[str] = None
    supports: List[int] = field(default_factory=list)  # Indices of nodes this supports
    contradicts: List[int] = field(default_factory=list)  # Indices this contradicts
    
    def to_dict(self) -> Dict:
        return {
            "type": self.step_type.value,
            "content": self.content,
            "confidence": self.confidence,
            "premises": self.premises,
            "rule": self.rule_applied
        }


class SymbolicReasoner:
    """
    Performs structured symbolic reasoning using inference rules.
    
    Features:
    - Modus ponens (if A then B, A → B)
    - Modus tollens (if A then B, not B → not A)
    - Syllogistic reasoning
    - Analogical reasoning
    - Contradiction detection
    """
    
    def __init__(self):
        self.rules: Dict[str, Tuple[str, str]] = {
            # rule_name: (pattern, consequence_template)
            "study_implies_knowledge": (r"study\s+(\w+)", "gain knowledge about {0}"),
            "learn_implies_capability": (r"learn\s+(\w+)", "develop capability in {0}"),
            "task_implies_planning": (r"run task|execute", "requires planning and execution"),
            "optimize_implies_improvement": (r"optimi[sz]e", "leads to performance improvement"),
            "error_implies_debug": (r"error|fail|bug", "requires debugging and analysis"),
            "question_implies_inquiry": (r"\?$|what|how|why|when|where", "requires information gathering"),
        }
        
        self.knowledge_base: List[str] = []
        self.reasoning_chains: List[List[ReasoningNode]] = []
    
    def add_knowledge(self, fact: str):
        """Add a fact to the knowledge base."""
        if fact not in self.knowledge_base:
            self.knowledge_base.append(fact)
    
    def symbolic_reasoning_chain(
        self,
        query: str,
        context: Dict[str, Any] = None,
        max_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Build a chain of reasoning for the given query.
        
        Args:
            query: The input to reason about
            context: Additional context information
            max_steps: Maximum reasoning steps
            
        Returns:
            Reasoning chain with conclusion
        """
        chain: List[ReasoningNode] = []
        context = context or {}
        
        # Step 1: Observation - record initial input
        chain.append(ReasoningNode(
            step_type=ReasoningStep.OBSERVATION,
            content=f"Input received: {query}",
            confidence=1.0
        ))
        
        # Step 2: Decomposition - break down the query
        components = self._decompose(query)
        if components:
            chain.append(ReasoningNode(
                step_type=ReasoningStep.DECOMPOSITION,
                content=f"Query components: {', '.join(components)}",
                confidence=0.9,
                premises=[query]
            ))
        
        # Step 3: Apply inference rules
        inferences = self._apply_rules(query)
        for rule_name, inference in inferences:
            chain.append(ReasoningNode(
                step_type=ReasoningStep.INFERENCE,
                content=inference,
                confidence=0.75,
                rule_applied=rule_name,
                premises=[query]
            ))
        
        # Step 4: Check knowledge base for relevant facts
        relevant_facts = self._query_knowledge_base(query)
        for fact in relevant_facts[:3]:
            chain.append(ReasoningNode(
                step_type=ReasoningStep.ANALOGY,
                content=f"Related knowledge: {fact}",
                confidence=0.6,
                premises=[query, fact]
            ))
        
        # Step 5: Generate hypotheses
        hypotheses = self._generate_hypotheses(query, chain)
        for hyp in hypotheses[:2]:
            chain.append(ReasoningNode(
                step_type=ReasoningStep.HYPOTHESIS,
                content=hyp,
                confidence=0.5,
                premises=[n.content for n in chain[-3:] if n.content]
            ))
        
        # Step 6: Check for contradictions
        contradictions = self._find_contradictions(chain)
        for i, j, explanation in contradictions:
            chain.append(ReasoningNode(
                step_type=ReasoningStep.CONTRADICTION,
                content=f"Contradiction detected: {explanation}",
                confidence=0.8,
                contradicts=[i, j]
            ))
        
        # Step 7: Synthesis - combine insights
        if len(chain) > 3:
            synthesis = self._synthesize(chain)
            chain.append(ReasoningNode(
                step_type=ReasoningStep.SYNTHESIS,
                content=synthesis,
                confidence=0.7,
                premises=[n.content for n in chain if n.confidence > 0.6]
            ))
        
        # Step 8: Conclusion
        conclusion, confidence = self._derive_conclusion(chain)
        chain.append(ReasoningNode(
            step_type=ReasoningStep.CONCLUSION,
            content=conclusion,
            confidence=confidence
        ))
        
        # Store chain for later analysis
        self.reasoning_chains.append(chain)
        
        return {
            "query": query,
            "chain": [node.to_dict() for node in chain],
            "conclusion": conclusion,
            "confidence": confidence,
            "steps": len(chain),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _decompose(self, query: str) -> List[str]:
        """Break down query into components."""
        # Simple decomposition by phrases
        components = []
        
        # Split on conjunctions
        parts = re.split(r'\s+and\s+|\s+or\s+|\s+then\s+|,\s+', query.lower())
        components.extend([p.strip() for p in parts if p.strip()])
        
        # Extract key terms
        key_terms = re.findall(r'\b(study|learn|task|optimize|analyze|create|build|fix)\b', query.lower())
        components.extend(key_terms)
        
        return list(set(components))
    
    def _apply_rules(self, query: str) -> List[Tuple[str, str]]:
        """Apply inference rules to the query."""
        results = []
        query_lower = query.lower()
        
        for rule_name, (pattern, template) in self.rules.items():
            match = re.search(pattern, query_lower)
            if match:
                # Fill in template with captured groups
                groups = match.groups() if match.groups() else []
                inference = template
                for i, group in enumerate(groups):
                    inference = inference.replace(f"{{{i}}}", group)
                results.append((rule_name, inference))
        
        return results
    
    def _query_knowledge_base(self, query: str) -> List[str]:
        """Find relevant facts from knowledge base."""
        query_words = set(query.lower().split())
        scored = []
        
        for fact in self.knowledge_base:
            fact_words = set(fact.lower().split())
            overlap = len(query_words & fact_words)
            if overlap > 0:
                scored.append((overlap, fact))
        
        scored.sort(reverse=True)
        return [fact for _, fact in scored]
    
    def _generate_hypotheses(
        self,
        query: str,
        chain: List[ReasoningNode]
    ) -> List[str]:
        """Generate hypotheses based on observations and inferences."""
        hypotheses = []
        
        # Combine observation patterns
        inferences = [n.content for n in chain if n.step_type == ReasoningStep.INFERENCE]
        
        if inferences:
            hypotheses.append(f"Given the inferences, the action should: {'; '.join(inferences[:2])}")
        
        # Pattern-based hypothesis generation
        if "study" in query.lower() or "learn" in query.lower():
            hypotheses.append("This is a knowledge acquisition request requiring focused learning")
        elif "task" in query.lower() or "run" in query.lower():
            hypotheses.append("This is an execution request requiring action planning")
        elif "?" in query:
            hypotheses.append("This is an inquiry requiring information retrieval")
        
        return hypotheses
    
    def _find_contradictions(
        self,
        chain: List[ReasoningNode]
    ) -> List[Tuple[int, int, str]]:
        """Detect contradictions in the reasoning chain."""
        contradictions = []
        
        for i, node_a in enumerate(chain):
            for j, node_b in enumerate(chain[i+1:], start=i+1):
                if self._are_contradictory(node_a.content, node_b.content):
                    contradictions.append((
                        i, j,
                        f"'{node_a.content[:30]}...' vs '{node_b.content[:30]}...'"
                    ))
        
        return contradictions
    
    def _are_contradictory(self, statement_a: str, statement_b: str) -> bool:
        """Check if two statements are contradictory."""
        negations = ["not", "cannot", "won't", "shouldn't", "impossible", "unable"]
        
        a_lower = statement_a.lower()
        b_lower = statement_b.lower()
        
        a_negated = any(neg in a_lower for neg in negations)
        b_negated = any(neg in b_lower for neg in negations)
        
        # If one is negated and other isn't, check for topic similarity
        if a_negated != b_negated:
            words_a = set(a_lower.split()) - set(negations)
            words_b = set(b_lower.split()) - set(negations)
            overlap = len(words_a & words_b)
            return overlap >= 3
        
        return False
    
    def _synthesize(self, chain: List[ReasoningNode]) -> str:
        """Synthesize insights from the reasoning chain."""
        insights = []
        
        for node in chain:
            if node.confidence > 0.6 and node.step_type in (
                ReasoningStep.INFERENCE,
                ReasoningStep.HYPOTHESIS
            ):
                # Extract key insight
                insights.append(node.content.split(':')[-1].strip())
        
        if insights:
            return f"Synthesis: {'; '.join(insights[:3])}"
        return "Synthesis: No high-confidence insights to combine"
    
    def _derive_conclusion(
        self,
        chain: List[ReasoningNode]
    ) -> Tuple[str, float]:
        """Derive final conclusion from the reasoning chain."""
        # Weight nodes by type and confidence
        weighted_content = []
        
        for node in chain:
            weight = node.confidence
            if node.step_type == ReasoningStep.SYNTHESIS:
                weight *= 1.5
            elif node.step_type == ReasoningStep.INFERENCE:
                weight *= 1.2
            elif node.step_type == ReasoningStep.HYPOTHESIS:
                weight *= 0.8
            
            weighted_content.append((weight, node.content))
        
        # Sort by weight
        weighted_content.sort(reverse=True)
        
        # Build conclusion from top weighted content
        if weighted_content:
            top_insight = weighted_content[0][1]
            avg_confidence = sum(w for w, _ in weighted_content) / len(weighted_content)
            
            # Check for contradictions that reduce confidence
            contradictions = [n for n in chain if n.step_type == ReasoningStep.CONTRADICTION]
            if contradictions:
                avg_confidence *= 0.8
            
            conclusion = f"Conclusion: {top_insight}"
            return conclusion, min(0.95, avg_confidence)
        
        return "Unable to derive conclusion from available information", 0.3
    
    def get_recent_chains(self, count: int = 5) -> List[Dict]:
        """Get recent reasoning chains."""
        chains = self.reasoning_chains[-count:]
        return [
            {
                "steps": len(chain),
                "conclusion": chain[-1].content if chain else None,
                "confidence": chain[-1].confidence if chain else 0
            }
            for chain in chains
        ]
    
    def explain(self, chain_index: int = -1) -> str:
        """Generate a human-readable explanation of a reasoning chain."""
        if not self.reasoning_chains:
            return "No reasoning chains available."
        
        chain = self.reasoning_chains[chain_index]
        explanation = ["Reasoning Process:\n"]
        
        for i, node in enumerate(chain, 1):
            icon = {
                ReasoningStep.OBSERVATION: "👁️",
                ReasoningStep.DECOMPOSITION: "🔍",
                ReasoningStep.HYPOTHESIS: "💡",
                ReasoningStep.INFERENCE: "➡️",
                ReasoningStep.ANALOGY: "🔗",
                ReasoningStep.CONTRADICTION: "⚠️",
                ReasoningStep.SYNTHESIS: "🧩",
                ReasoningStep.CONCLUSION: "✅"
            }.get(node.step_type, "•")
            
            explanation.append(f"{i}. {icon} [{node.step_type.value}] {node.content}")
            if node.rule_applied:
                explanation.append(f"   (Rule: {node.rule_applied})")
            explanation.append(f"   Confidence: {node.confidence:.0%}")
        
        return "\n".join(explanation)


# Module-level instance for external imports
_reasoner = SymbolicReasoner()

def symbolic_reasoning_chain(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Module-level function for symbolic reasoning."""
    return _reasoner.symbolic_reasoning_chain(query, context)

def add_knowledge(fact: str):
    """Add knowledge to the reasoner."""
    _reasoner.add_knowledge(fact)

def explain_last_reasoning() -> str:
    """Explain the most recent reasoning chain."""
    return _reasoner.explain()
