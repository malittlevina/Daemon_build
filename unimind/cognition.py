# unimind/cognition.py
"""
Cognition Pipeline
==================
Coordinates the daemon's thought process through three layers:

1. NLU (Natural Language Understanding) - Understands intent
2. LLM (Large Language Model) - Generates reasoning and responses
3. LAM (Language Action Model) - Plans and executes actions

This creates a coherent, human-like thought process.
"""

import os
import time
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class ThoughtType(Enum):
    """Types of cognitive processing."""
    UNDERSTAND = auto()    # NLU - What does this mean?
    REASON = auto()        # LLM - How should I think about this?
    RESPOND = auto()       # LLM - What should I say?
    PLAN = auto()          # LAM - What should I do?
    EXECUTE = auto()       # LAM - Do the thing
    REFLECT = auto()       # Meta - Think about thinking


class Intent(Enum):
    """Recognized intents from NLU."""
    # Conversational
    GREETING = "greeting"
    FAREWELL = "farewell"
    GRATITUDE = "gratitude"
    QUESTION = "question"
    STATEMENT = "statement"
    
    # Action-oriented
    COMMAND = "command"
    REQUEST = "request"
    TASK = "task"
    
    # Learning
    TEACH = "teach"
    LEARN = "learn"
    REMEMBER = "remember"
    RECALL = "recall"
    
    # System
    STATUS = "status"
    CONFIGURE = "configure"
    HELP = "help"
    
    # Meta
    REFLECT = "reflect"
    JOURNAL = "journal"
    OBSERVE = "observe"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class ThoughtResult:
    """Result of cognitive processing."""
    input_text: str
    intent: Intent = Intent.UNKNOWN
    confidence: float = 0.0
    entities: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    response: str = ""
    actions: List[Dict[str, Any]] = field(default_factory=list)
    emotion: str = "neutral"
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'input': self.input_text,
            'intent': self.intent.value,
            'confidence': self.confidence,
            'entities': self.entities,
            'reasoning': self.reasoning,
            'response': self.response,
            'actions': self.actions,
            'emotion': self.emotion,
            'processing_time_ms': self.processing_time_ms
        }


class NLUProcessor:
    """
    Natural Language Understanding - First layer of cognition.
    Parses input to understand intent, entities, and context.
    """
    
    # Intent patterns
    INTENT_PATTERNS = {
        Intent.GREETING: ['hello', 'hi', 'hey', 'good morning', 'good evening', 'greetings'],
        Intent.FAREWELL: ['bye', 'goodbye', 'see you', 'farewell', 'exit', 'quit'],
        Intent.GRATITUDE: ['thank', 'thanks', 'appreciate', 'grateful'],
        Intent.QUESTION: ['what', 'who', 'where', 'when', 'why', 'how', 'can you', 'could you', 'do you', '?'],
        Intent.COMMAND: ['do', 'execute', 'run', 'start', 'stop', 'create', 'delete', 'open', 'close'],
        Intent.REQUEST: ['please', 'would you', 'can you', 'could you', 'help me'],
        Intent.TASK: ['task', 'todo', 'remind', 'schedule', 'plan'],
        Intent.LEARN: ['learn', 'study', 'understand', 'explain'],
        Intent.TEACH: ['teach', 'show', 'demonstrate', 'let me tell you'],
        Intent.REMEMBER: ['remember', 'note', 'save', 'store', 'keep in mind'],
        Intent.RECALL: ['recall', 'what did', 'when did', 'remember when'],
        Intent.STATUS: ['status', 'how are you', 'what\'s up', 'state'],
        Intent.HELP: ['help', 'assist', 'support', 'guide'],
        Intent.REFLECT: ['reflect', 'think about', 'consider'],
        Intent.JOURNAL: ['journal', 'diary', 'log', 'record'],
        Intent.OBSERVE: ['observe', 'notice', 'saw', 'noticed'],
    }
    
    def __init__(self):
        self.context_history: List[Dict] = []
    
    def understand(self, text: str, context: Optional[Dict] = None) -> Tuple[Intent, float, Dict]:
        """
        Understand the input text.
        
        Returns:
            Tuple of (intent, confidence, entities)
        """
        text_lower = text.lower().strip()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            max_score = intent_scores[best_intent]
            confidence = min(1.0, max_score * 0.3)
        else:
            # Default to statement or question
            if '?' in text:
                best_intent = Intent.QUESTION
                confidence = 0.5
            else:
                best_intent = Intent.STATEMENT
                confidence = 0.3
        
        # Extract entities (simplified)
        entities = self._extract_entities(text)
        
        return best_intent, confidence, entities
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text."""
        entities = {}
        
        # Extract quoted strings
        import re
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            entities['quoted'] = quoted
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if numbers:
            entities['numbers'] = [float(n) if '.' in n else int(n) for n in numbers]
        
        # Extract time references
        time_words = ['today', 'tomorrow', 'yesterday', 'now', 'later', 'morning', 'evening', 'night']
        found_times = [w for w in time_words if w in text.lower()]
        if found_times:
            entities['time_references'] = found_times
        
        return entities


class LLMProcessor:
    """
    Large Language Model - Second layer of cognition.
    Generates reasoning and responses using AI models.
    """
    
    def __init__(self, model: str = "llama3", use_ollama: bool = True):
        self.model = model
        self.use_ollama = use_ollama
        self._ollama_available = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def reason(
        self,
        input_text: str,
        intent: Intent,
        context: Optional[Dict] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate reasoning about the input.
        """
        if not self.use_ollama or not self._ollama_available:
            return self._fallback_reason(input_text, intent)
        
        # Build prompt
        if system_prompt is None:
            system_prompt = """You are Prometheus, an AI daemon companion. 
You help with daily tasks, remember important things, and provide thoughtful assistance.
Be concise, helpful, and maintain a friendly but professional tone.
You have access to memory, can observe and learn, and help plan tasks."""
        
        prompt = f"{system_prompt}\n\nUser: {input_text}\n\nAssistant:"
        
        try:
            result = subprocess.run(
                ['ollama', 'run', self.model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
        except Exception as e:
            print(f"[LLM] Ollama error: {e}")
        
        return self._fallback_reason(input_text, intent)
    
    def _fallback_reason(self, input_text: str, intent: Intent) -> str:
        """Fallback when LLM is not available."""
        responses = {
            Intent.GREETING: "Hello! How can I assist you today?",
            Intent.FAREWELL: "Goodbye! Take care.",
            Intent.GRATITUDE: "You're welcome!",
            Intent.QUESTION: f"That's an interesting question about: {input_text}",
            Intent.STATUS: "I'm operational and ready to assist.",
            Intent.HELP: "I can help with tasks, memory, observation, and daily assistance.",
            Intent.REFLECT: "Taking a moment to reflect...",
            Intent.JOURNAL: "I'll note that in the diary.",
            Intent.OBSERVE: "Observation recorded.",
        }
        return responses.get(intent, f"I understand you said: {input_text}")


class LAMProcessor:
    """
    Language Action Model - Third layer of cognition.
    Plans and executes actions based on understood intent.
    """
    
    def __init__(self):
        self.action_registry: Dict[str, callable] = {}
        self.pending_actions: List[Dict] = []
    
    def register_action(self, name: str, handler: callable):
        """Register an action handler."""
        self.action_registry[name] = handler
    
    def plan(self, intent: Intent, entities: Dict, context: Optional[Dict] = None) -> List[Dict]:
        """
        Plan actions based on intent.
        """
        actions = []
        
        if intent == Intent.TASK:
            actions.append({
                'type': 'create_task',
                'params': entities
            })
        
        elif intent == Intent.REMEMBER:
            actions.append({
                'type': 'store_memory',
                'params': entities
            })
        
        elif intent == Intent.RECALL:
            actions.append({
                'type': 'search_memory',
                'params': entities
            })
        
        elif intent == Intent.LEARN:
            topic = entities.get('quoted', [entities.get('topic', 'general')])[0] if entities.get('quoted') else 'general'
            actions.append({
                'type': 'study',
                'params': {'topic': topic}
            })
        
        elif intent == Intent.OBSERVE:
            actions.append({
                'type': 'observe',
                'params': entities
            })
        
        elif intent == Intent.JOURNAL:
            actions.append({
                'type': 'write_journal',
                'params': entities
            })
        
        elif intent == Intent.COMMAND:
            actions.append({
                'type': 'execute_command',
                'params': entities
            })
        
        return actions
    
    def execute(self, actions: List[Dict]) -> List[Dict]:
        """Execute planned actions."""
        results = []
        
        for action in actions:
            action_type = action.get('type')
            params = action.get('params', {})
            
            if action_type in self.action_registry:
                try:
                    result = self.action_registry[action_type](**params)
                    results.append({
                        'action': action_type,
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'action': action_type,
                        'status': 'error',
                        'error': str(e)
                    })
            else:
                results.append({
                    'action': action_type,
                    'status': 'pending',
                    'message': f'Action {action_type} registered for execution'
                })
                self.pending_actions.append(action)
        
        return results


class CognitionPipeline:
    """
    The complete cognition pipeline - NLU → LLM → LAM.
    
    This creates human-like thought processing:
    1. Understand what was said (NLU)
    2. Think about it and formulate response (LLM)
    3. Plan and take action if needed (LAM)
    """
    
    def __init__(self, use_llm: bool = True):
        self.nlu = NLUProcessor()
        self.llm = LLMProcessor(use_ollama=use_llm)
        self.lam = LAMProcessor()
        self.use_llm = use_llm
        
        # Emotion detection
        self.emotion_words = {
            'positive': ['happy', 'great', 'wonderful', 'excited', 'love', 'amazing', 'good', 'thanks'],
            'negative': ['sad', 'angry', 'frustrated', 'worried', 'bad', 'terrible', 'hate', 'annoyed'],
            'curious': ['wonder', 'curious', 'interesting', 'how', 'why', 'what if'],
            'neutral': []
        }
    
    def process(self, input_text: str, context: Optional[Dict] = None) -> ThoughtResult:
        """
        Process input through the full cognition pipeline.
        """
        start_time = time.time()
        
        result = ThoughtResult(input_text=input_text)
        
        # Step 1: NLU - Understand
        intent, confidence, entities = self.nlu.understand(input_text, context)
        result.intent = intent
        result.confidence = confidence
        result.entities = entities
        
        # Detect emotion
        result.emotion = self._detect_emotion(input_text)
        
        # Step 2: LLM - Reason and Respond
        if self.use_llm:
            response = self.llm.reason(input_text, intent, context)
            result.response = response
        else:
            result.response = self.llm._fallback_reason(input_text, intent)
        
        # Step 3: LAM - Plan Actions
        actions = self.lam.plan(intent, entities, context)
        result.actions = actions
        
        # Execute actions if any
        if actions:
            action_results = self.lam.execute(actions)
            result.actions = action_results
        
        # Calculate processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _detect_emotion(self, text: str) -> str:
        """Detect emotional tone of input."""
        text_lower = text.lower()
        
        scores = {emotion: 0 for emotion in self.emotion_words}
        for emotion, words in self.emotion_words.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] += 1
        
        # Find dominant emotion
        if scores['positive'] > scores['negative']:
            return 'positive'
        elif scores['negative'] > scores['positive']:
            return 'negative'
        elif scores['curious'] > 0:
            return 'curious'
        else:
            return 'neutral'
    
    def register_action(self, name: str, handler: callable):
        """Register an action handler with LAM."""
        self.lam.register_action(name, handler)
    
    def get_pending_actions(self) -> List[Dict]:
        """Get actions waiting for execution."""
        return self.lam.pending_actions


# Global cognition pipeline
_cognition: Optional[CognitionPipeline] = None


def get_cognition() -> CognitionPipeline:
    """Get or create the global cognition pipeline."""
    global _cognition
    if _cognition is None:
        _cognition = CognitionPipeline()
    return _cognition


def process_thought(input_text: str) -> ThoughtResult:
    """Convenience function to process a thought."""
    return get_cognition().process(input_text)
