# unimind/models/chain_of_thought.py
# Chain-of-Thought Reasoning Engine

from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re
import time


class ThoughtType(Enum):
    """Types of reasoning thoughts."""
    OBSERVATION = "observation"      # Initial input analysis
    HYPOTHESIS = "hypothesis"        # Possible explanations
    DEDUCTION = "deduction"          # Logical inference
    INDUCTION = "induction"          # Pattern-based inference
    ABDUCTION = "abduction"          # Best explanation
    VERIFICATION = "verification"    # Checking validity
    REFLECTION = "reflection"        # Meta-cognition
    CONCLUSION = "conclusion"        # Final answer
    DECOMPOSITION = "decomposition"  # Breaking down problems
    SYNTHESIS = "synthesis"          # Combining information


class ReasoningStrategy(Enum):
    """Reasoning strategies."""
    STEP_BY_STEP = "step_by_step"           # Linear chain
    TREE_OF_THOUGHT = "tree_of_thought"     # Branching exploration
    SELF_CONSISTENCY = "self_consistency"   # Multiple paths, voting
    LEAST_TO_MOST = "least_to_most"         # Build from simple to complex
    VERIFY_AND_EDIT = "verify_and_edit"     # Generate then verify
    ANALOGICAL = "analogical"               # Compare to similar problems


@dataclass
class ThoughtStep:
    """A single step in chain-of-thought reasoning."""
    step_id: int
    thought_type: ThoughtType
    content: str
    confidence: float = 0.5
    parent_step: Optional[int] = None
    children_steps: List[int] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "step": self.step_id,
            "type": self.thought_type.value,
            "content": self.content,
            "confidence": self.confidence,
            "evidence": self.evidence
        }


@dataclass
class ReasoningTrace:
    """Complete trace of reasoning process."""
    trace_id: str
    query: str
    strategy: ReasoningStrategy
    steps: List[ThoughtStep] = field(default_factory=list)
    final_answer: str = ""
    total_confidence: float = 0.0
    reasoning_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, thought_type: ThoughtType, content: str, confidence: float = 0.5) -> ThoughtStep:
        """Add a reasoning step."""
        step = ThoughtStep(
            step_id=len(self.steps) + 1,
            thought_type=thought_type,
            content=content,
            confidence=confidence
        )
        self.steps.append(step)
        return step
        
    def get_formatted_chain(self) -> str:
        """Get human-readable reasoning chain."""
        lines = [f"Question: {self.query}\n"]
        
        for step in self.steps:
            prefix = {
                ThoughtType.OBSERVATION: "📋 Observation",
                ThoughtType.HYPOTHESIS: "💭 Hypothesis",
                ThoughtType.DEDUCTION: "🔗 Deduction",
                ThoughtType.INDUCTION: "📊 Induction",
                ThoughtType.VERIFICATION: "✅ Verification",
                ThoughtType.REFLECTION: "🪞 Reflection",
                ThoughtType.CONCLUSION: "🎯 Conclusion",
                ThoughtType.DECOMPOSITION: "🧩 Decomposition",
                ThoughtType.SYNTHESIS: "🔮 Synthesis",
            }.get(step.thought_type, "• Step")
            
            lines.append(f"{prefix} {step.step_id}: {step.content}")
            
        if self.final_answer:
            lines.append(f"\n**Final Answer**: {self.final_answer}")
            lines.append(f"(Confidence: {self.total_confidence:.2%})")
            
        return "\n".join(lines)
        
    def to_dict(self) -> Dict:
        return {
            "trace_id": self.trace_id,
            "query": self.query,
            "strategy": self.strategy.value,
            "steps": [s.to_dict() for s in self.steps],
            "final_answer": self.final_answer,
            "confidence": self.total_confidence,
            "reasoning_time_ms": self.reasoning_time_ms
        }


class ReasoningPromptBuilder:
    """Builds prompts for chain-of-thought reasoning."""
    
    @staticmethod
    def step_by_step_prompt(query: str, context: str = "") -> str:
        """Build prompt for step-by-step reasoning."""
        prompt = """You are a careful reasoner. Think through this problem step by step.

Question: {query}

{context_section}

Please reason through this step by step:
1. First, identify what we know and what we need to find
2. Then, work through the logic carefully
3. Finally, state your conclusion

Let's think step by step:"""
        
        context_section = f"Context: {context}\n" if context else ""
        return prompt.format(query=query, context_section=context_section)
        
    @staticmethod
    def tree_of_thought_prompt(query: str, num_paths: int = 3) -> str:
        """Build prompt for tree-of-thought reasoning."""
        return f"""You are exploring multiple reasoning paths for this problem.

Question: {query}

Generate {num_paths} different approaches to solve this:

Approach 1:
[Your first line of reasoning]

Approach 2:
[An alternative approach]

Approach 3:
[A third perspective]

Now evaluate which approach is most promising and why:"""

    @staticmethod
    def verification_prompt(query: str, proposed_answer: str) -> str:
        """Build prompt for verifying an answer."""
        return f"""Verify this answer for correctness.

Question: {query}
Proposed Answer: {proposed_answer}

Check:
1. Does this answer actually address the question?
2. Is the reasoning valid?
3. Are there any errors or gaps?
4. What's your confidence level?

Verification:"""

    @staticmethod
    def decomposition_prompt(query: str) -> str:
        """Build prompt for breaking down a complex problem."""
        return f"""Break this complex problem into simpler sub-problems.

Problem: {query}

Let's decompose this:
1. What are the main components of this problem?
2. What simpler questions need to be answered first?
3. How do the sub-problems connect?

Decomposition:"""


class ChainOfThoughtEngine:
    """
    Engine for chain-of-thought reasoning.
    
    Features:
    - Multiple reasoning strategies
    - Step tracking and verification
    - Confidence scoring
    - Self-correction
    """
    
    def __init__(self, llm_provider=None):
        self.llm = llm_provider
        self.traces: List[ReasoningTrace] = []
        self.strategy_handlers: Dict[ReasoningStrategy, Callable] = {
            ReasoningStrategy.STEP_BY_STEP: self._reason_step_by_step,
            ReasoningStrategy.TREE_OF_THOUGHT: self._reason_tree_of_thought,
            ReasoningStrategy.SELF_CONSISTENCY: self._reason_self_consistency,
            ReasoningStrategy.LEAST_TO_MOST: self._reason_least_to_most,
            ReasoningStrategy.VERIFY_AND_EDIT: self._reason_verify_and_edit,
        }
        
    def reason(
        self,
        query: str,
        strategy: ReasoningStrategy = ReasoningStrategy.STEP_BY_STEP,
        context: str = "",
        max_steps: int = 10
    ) -> ReasoningTrace:
        """
        Perform chain-of-thought reasoning.
        
        Args:
            query: The question or problem to reason about
            strategy: Reasoning strategy to use
            context: Additional context information
            max_steps: Maximum reasoning steps
            
        Returns:
            ReasoningTrace with complete thought chain
        """
        start_time = time.time()
        
        trace = ReasoningTrace(
            trace_id=f"trace_{int(time.time())}",
            query=query,
            strategy=strategy
        )
        
        # Get strategy handler
        handler = self.strategy_handlers.get(strategy, self._reason_step_by_step)
        
        # Execute reasoning
        handler(trace, query, context, max_steps)
        
        trace.reasoning_time_ms = (time.time() - start_time) * 1000
        self.traces.append(trace)
        
        return trace
        
    def _reason_step_by_step(
        self,
        trace: ReasoningTrace,
        query: str,
        context: str,
        max_steps: int
    ):
        """Linear step-by-step reasoning."""
        # Step 1: Observation - analyze the query
        trace.add_step(
            ThoughtType.OBSERVATION,
            f"Analyzing the question: '{query}'",
            confidence=0.9
        )
        
        # Step 2: Decomposition - identify key components
        key_terms = self._extract_key_terms(query)
        trace.add_step(
            ThoughtType.DECOMPOSITION,
            f"Key components identified: {', '.join(key_terms)}",
            confidence=0.8
        )
        
        # Step 3-N: Use LLM if available
        if self.llm:
            prompt = ReasoningPromptBuilder.step_by_step_prompt(query, context)
            response = self.llm.generate(prompt)
            
            # Parse LLM response into steps
            self._parse_llm_reasoning(trace, response.text if hasattr(response, 'text') else str(response))
        else:
            # Fallback: simple heuristic reasoning
            self._heuristic_reasoning(trace, query, key_terms)
            
        # Calculate overall confidence
        if trace.steps:
            trace.total_confidence = sum(s.confidence for s in trace.steps) / len(trace.steps)
            
    def _reason_tree_of_thought(
        self,
        trace: ReasoningTrace,
        query: str,
        context: str,
        max_steps: int
    ):
        """Tree-of-thought: explore multiple reasoning paths."""
        # Generate multiple hypotheses
        trace.add_step(
            ThoughtType.OBSERVATION,
            f"Exploring multiple approaches to: '{query}'",
            confidence=0.9
        )
        
        # Create 3 hypothesis branches
        hypotheses = self._generate_hypotheses(query)
        
        for i, hyp in enumerate(hypotheses, 1):
            step = trace.add_step(
                ThoughtType.HYPOTHESIS,
                f"Approach {i}: {hyp['approach']}",
                confidence=hyp['initial_confidence']
            )
            
        # Evaluate and select best path
        best_idx = max(range(len(hypotheses)), key=lambda i: hypotheses[i]['initial_confidence'])
        best_hyp = hypotheses[best_idx]
        
        trace.add_step(
            ThoughtType.DEDUCTION,
            f"Selected approach {best_idx + 1} as most promising: {best_hyp['reasoning']}",
            confidence=best_hyp['initial_confidence'] * 1.1
        )
        
        # Develop selected path
        trace.add_step(
            ThoughtType.CONCLUSION,
            best_hyp['conclusion'],
            confidence=best_hyp['initial_confidence']
        )
        
        trace.final_answer = best_hyp['conclusion']
        trace.total_confidence = best_hyp['initial_confidence']
        
    def _reason_self_consistency(
        self,
        trace: ReasoningTrace,
        query: str,
        context: str,
        max_steps: int
    ):
        """Self-consistency: multiple chains, then vote."""
        trace.add_step(
            ThoughtType.OBSERVATION,
            f"Using self-consistency to verify answer: '{query}'",
            confidence=0.9
        )
        
        # Generate multiple reasoning chains
        answers = []
        
        for i in range(3):
            # Vary the approach slightly
            sub_answer = self._generate_single_answer(query, variation=i)
            answers.append(sub_answer)
            
            trace.add_step(
                ThoughtType.DEDUCTION,
                f"Chain {i + 1} answer: {sub_answer['answer']}",
                confidence=sub_answer['confidence']
            )
            
        # Vote on most common answer
        answer_counts = {}
        for a in answers:
            key = a['answer']
            answer_counts[key] = answer_counts.get(key, 0) + 1
            
        best_answer = max(answer_counts.keys(), key=lambda k: answer_counts[k])
        consistency = answer_counts[best_answer] / len(answers)
        
        trace.add_step(
            ThoughtType.VERIFICATION,
            f"Consistency check: {answer_counts[best_answer]}/{len(answers)} chains agree",
            confidence=consistency
        )
        
        trace.add_step(
            ThoughtType.CONCLUSION,
            best_answer,
            confidence=consistency
        )
        
        trace.final_answer = best_answer
        trace.total_confidence = consistency
        
    def _reason_least_to_most(
        self,
        trace: ReasoningTrace,
        query: str,
        context: str,
        max_steps: int
    ):
        """Least-to-most: build from simple to complex."""
        trace.add_step(
            ThoughtType.OBSERVATION,
            f"Decomposing into simpler subproblems: '{query}'",
            confidence=0.9
        )
        
        # Decompose problem
        subproblems = self._decompose_problem(query)
        
        trace.add_step(
            ThoughtType.DECOMPOSITION,
            f"Identified {len(subproblems)} subproblems",
            confidence=0.8
        )
        
        # Solve from simplest to most complex
        solved = []
        for i, sub in enumerate(subproblems):
            sub_answer = self._solve_subproblem(sub, solved)
            solved.append(sub_answer)
            
            trace.add_step(
                ThoughtType.DEDUCTION,
                f"Subproblem {i + 1}: {sub} → {sub_answer}",
                confidence=0.7
            )
            
        # Synthesize final answer
        final = self._synthesize_answer(solved, query)
        
        trace.add_step(
            ThoughtType.SYNTHESIS,
            f"Combining solutions: {final}",
            confidence=0.75
        )
        
        trace.final_answer = final
        trace.total_confidence = 0.75
        
    def _reason_verify_and_edit(
        self,
        trace: ReasoningTrace,
        query: str,
        context: str,
        max_steps: int
    ):
        """Generate answer, then verify and edit."""
        trace.add_step(
            ThoughtType.OBSERVATION,
            f"Generating initial answer for: '{query}'",
            confidence=0.9
        )
        
        # Generate initial answer
        initial = self._generate_single_answer(query)
        
        trace.add_step(
            ThoughtType.HYPOTHESIS,
            f"Initial answer: {initial['answer']}",
            confidence=initial['confidence']
        )
        
        # Verify
        verification = self._verify_answer(query, initial['answer'])
        
        trace.add_step(
            ThoughtType.VERIFICATION,
            f"Verification: {verification['assessment']}",
            confidence=verification['confidence']
        )
        
        # Edit if needed
        if verification['needs_edit']:
            edited = self._edit_answer(query, initial['answer'], verification['issues'])
            trace.add_step(
                ThoughtType.REFLECTION,
                f"Edited answer: {edited}",
                confidence=verification['confidence'] * 1.1
            )
            final = edited
        else:
            final = initial['answer']
            
        trace.add_step(
            ThoughtType.CONCLUSION,
            final,
            confidence=verification['confidence']
        )
        
        trace.final_answer = final
        trace.total_confidence = verification['confidence']
        
    # Helper methods
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from query."""
        # Simple word-based extraction
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'when', 'where', 'who', 'which'}
        words = query.lower().replace('?', '').replace('.', '').split()
        return [w for w in words if w not in stop_words and len(w) > 2]
        
    def _generate_hypotheses(self, query: str) -> List[Dict]:
        """Generate multiple hypotheses for a query."""
        # Simple hypothesis generation
        return [
            {
                "approach": "Direct analysis approach",
                "reasoning": "Analyze the question directly and find the answer",
                "conclusion": f"Based on direct analysis: [Answer to '{query[:30]}...']",
                "initial_confidence": 0.7
            },
            {
                "approach": "Comparative approach",
                "reasoning": "Compare to similar known problems",
                "conclusion": f"Based on comparison: [Answer to '{query[:30]}...']",
                "initial_confidence": 0.6
            },
            {
                "approach": "First principles approach",
                "reasoning": "Break down to fundamental concepts",
                "conclusion": f"Based on first principles: [Answer to '{query[:30]}...']",
                "initial_confidence": 0.65
            }
        ]
        
    def _generate_single_answer(self, query: str, variation: int = 0) -> Dict:
        """Generate a single answer."""
        variations = ["direct", "detailed", "concise"]
        style = variations[variation % len(variations)]
        
        return {
            "answer": f"[{style.title()} answer to: {query[:40]}...]",
            "confidence": 0.6 + (variation * 0.05)
        }
        
    def _decompose_problem(self, query: str) -> List[str]:
        """Decompose a problem into subproblems."""
        # Simple decomposition
        return [
            f"What is being asked in '{query[:30]}...'?",
            "What information do we have?",
            "What steps are needed?"
        ]
        
    def _solve_subproblem(self, subproblem: str, prior_solutions: List[str]) -> str:
        """Solve a subproblem."""
        return f"[Solution to: {subproblem[:30]}...]"
        
    def _synthesize_answer(self, solutions: List[str], query: str) -> str:
        """Synthesize final answer from solutions."""
        return f"Combined answer based on {len(solutions)} subproblem solutions"
        
    def _verify_answer(self, query: str, answer: str) -> Dict:
        """Verify an answer."""
        # Simple verification heuristics
        issues = []
        confidence = 0.8
        
        if len(answer) < 10:
            issues.append("Answer may be too short")
            confidence -= 0.2
            
        if query.lower() not in answer.lower():
            confidence -= 0.1
            
        return {
            "assessment": "Answer appears reasonable" if not issues else f"Issues found: {issues}",
            "confidence": confidence,
            "needs_edit": len(issues) > 0,
            "issues": issues
        }
        
    def _edit_answer(self, query: str, answer: str, issues: List[str]) -> str:
        """Edit an answer to fix issues."""
        return f"{answer} [Edited to address: {', '.join(issues)}]"
        
    def _heuristic_reasoning(self, trace: ReasoningTrace, query: str, key_terms: List[str]):
        """Fallback heuristic reasoning without LLM."""
        # Type detection
        if any(w in query.lower() for w in ['what', 'who', 'where', 'when']):
            trace.add_step(
                ThoughtType.DEDUCTION,
                "This is a factual/information-seeking question",
                confidence=0.7
            )
        elif 'how' in query.lower():
            trace.add_step(
                ThoughtType.DEDUCTION,
                "This is a procedural/how-to question",
                confidence=0.7
            )
        elif 'why' in query.lower():
            trace.add_step(
                ThoughtType.DEDUCTION,
                "This is a causal/explanatory question",
                confidence=0.7
            )
            
        # Generate conclusion
        trace.add_step(
            ThoughtType.CONCLUSION,
            f"Based on analysis of '{', '.join(key_terms)}', the answer involves these key concepts.",
            confidence=0.6
        )
        
        trace.final_answer = f"Answer based on key terms: {', '.join(key_terms)}"
        
    def _parse_llm_reasoning(self, trace: ReasoningTrace, response: str):
        """Parse LLM response into reasoning steps."""
        # Look for numbered steps or bullet points
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect step type from content
            if any(w in line.lower() for w in ['first', 'initially', 'observe', 'notice']):
                thought_type = ThoughtType.OBSERVATION
            elif any(w in line.lower() for w in ['therefore', 'thus', 'conclude', 'finally']):
                thought_type = ThoughtType.CONCLUSION
            elif any(w in line.lower() for w in ['because', 'since', 'follows']):
                thought_type = ThoughtType.DEDUCTION
            elif any(w in line.lower() for w in ['might', 'could', 'possibly', 'hypothesis']):
                thought_type = ThoughtType.HYPOTHESIS
            else:
                thought_type = ThoughtType.DEDUCTION
                
            # Clean line
            clean_line = re.sub(r'^[\d\.\)\-\*]+\s*', '', line)
            if clean_line:
                trace.add_step(thought_type, clean_line, confidence=0.7)
                
        # Set final answer from last conclusion step
        for step in reversed(trace.steps):
            if step.thought_type == ThoughtType.CONCLUSION:
                trace.final_answer = step.content
                break
                
    def get_trace(self, trace_id: str) -> Optional[ReasoningTrace]:
        """Get a specific trace by ID."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None
        
    def get_stats(self) -> Dict:
        """Get reasoning engine statistics."""
        if not self.traces:
            return {"total_traces": 0}
            
        return {
            "total_traces": len(self.traces),
            "strategies_used": list(set(t.strategy.value for t in self.traces)),
            "avg_steps": sum(len(t.steps) for t in self.traces) / len(self.traces),
            "avg_confidence": sum(t.total_confidence for t in self.traces) / len(self.traces),
            "avg_time_ms": sum(t.reasoning_time_ms for t in self.traces) / len(self.traces)
        }


# Convenience function
def create_reasoner(llm_provider=None) -> ChainOfThoughtEngine:
    """Create a chain-of-thought reasoning engine."""
    return ChainOfThoughtEngine(llm_provider)
