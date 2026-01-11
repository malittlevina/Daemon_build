# unimind/models/native/bootstrap.py
# Bootstrap System - Pre-train models for first boot readiness

import os
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from unimind.models.native.pretrain_data import (
    get_all_training_texts,
    get_conversation_pairs,
    get_command_intents,
    get_all_command_patterns,
    COMMAND_PATTERNS,
    RESPONSE_TEMPLATES,
    DOMAIN_KNOWLEDGE,
    INTENT_TRAINING_DATA,
    SKILL_EXAMPLES,
)


@dataclass
class BootstrapConfig:
    """Configuration for bootstrap process."""
    data_dir: str = "~/.thoth/pretrained"
    tokenizer_vocab_size: int = 8000
    embedding_dimension: int = 384
    train_word2vec: bool = True
    train_tokenizer: bool = True
    create_knowledge_base: bool = True
    verbose: bool = True


class ConversationEngine:
    """
    Pre-trained conversation engine for immediate responses.
    
    Uses pattern matching and learned responses to handle
    conversations without requiring heavy model inference.
    """
    
    def __init__(self):
        self.conversations: Dict[str, str] = {}
        self.command_patterns: List[Dict] = []
        self.response_templates: Dict[str, List[str]] = {}
        self.knowledge_base: Dict[str, str] = {}
        self.intent_patterns: Dict[str, List[str]] = {}
        self.learned_responses: Dict[str, str] = {}
        
        # Similarity cache for faster lookups
        self.embedding_cache: Dict[str, List[float]] = {}
        
    def load_pretrained_data(self):
        """Load pre-trained conversation data."""
        # Load conversation pairs
        for question, answer in get_conversation_pairs():
            self.conversations[question.lower().strip()] = answer
            
        # Load all command patterns (including research commands)
        self.command_patterns = get_all_command_patterns()
        
        # Load response templates
        self.response_templates = RESPONSE_TEMPLATES.copy()
        
        # Load knowledge base
        self.knowledge_base = DOMAIN_KNOWLEDGE.copy()
        
        # Add research knowledge
        try:
            from unimind.models.native.education_data import get_research_knowledge
            self.knowledge_base.update(get_research_knowledge())
        except ImportError:
            pass
        
        # Load intent patterns
        self.intent_patterns = get_command_intents()
        
        print(f"[ConversationEngine] Loaded {len(self.conversations)} conversations")
        print(f"[ConversationEngine] Loaded {len(self.command_patterns)} command patterns")
        print(f"[ConversationEngine] Loaded {len(self.knowledge_base)} knowledge entries")
        
    def find_response(self, user_input: str) -> Optional[str]:
        """
        Find a response for user input.
        
        Uses multiple strategies:
        1. Exact match
        2. Pattern matching
        3. Intent detection
        4. Knowledge lookup
        5. Learned responses
        """
        input_lower = user_input.lower().strip()
        
        # 1. Check exact matches
        if input_lower in self.conversations:
            return self.conversations[input_lower]
            
        # 2. Check learned responses
        if input_lower in self.learned_responses:
            return self.learned_responses[input_lower]
            
        # 3. Check command patterns
        for pattern_info in self.command_patterns:
            for pattern in pattern_info["patterns"]:
                if pattern in input_lower:
                    return pattern_info["response"]
                    
        # 4. Check knowledge base queries
        for topic, knowledge in self.knowledge_base.items():
            if topic in input_lower or f"what is {topic}" in input_lower:
                return knowledge
                
        # 5. Partial matching on conversations
        best_match = None
        best_score = 0
        
        for question, answer in self.conversations.items():
            score = self._similarity_score(input_lower, question)
            if score > best_score and score > 0.5:
                best_score = score
                best_match = answer
                
        if best_match:
            return best_match
            
        return None
        
    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate simple word overlap similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
        
    def detect_intent(self, user_input: str) -> str:
        """Detect the intent of user input."""
        input_lower = user_input.lower()
        
        # Check each intent's patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in input_lower:
                    return intent
                    
        # Fallback detection based on keywords
        if any(w in input_lower for w in ["?", "what", "how", "why", "when", "where", "who"]):
            return "question"
        elif any(w in input_lower for w in ["hello", "hi", "hey", "morning", "evening"]):
            return "greeting"
        elif any(w in input_lower for w in ["bye", "goodbye", "later", "thanks"]):
            return "farewell"
        elif any(w in input_lower for w in ["please", "can you", "would you", "help"]):
            return "request"
            
        return "statement"
        
    def get_template_response(self, template_type: str) -> str:
        """Get a response from templates."""
        import random
        templates = self.response_templates.get(template_type, ["I understand."])
        return random.choice(templates)
        
    def learn_response(self, user_input: str, response: str):
        """Learn a new response pattern."""
        self.learned_responses[user_input.lower().strip()] = response
        
    def add_knowledge(self, topic: str, information: str):
        """Add knowledge to the knowledge base."""
        self.knowledge_base[topic.lower()] = information
        
    def save(self, path: str):
        """Save conversation engine state."""
        data = {
            "conversations": self.conversations,
            "learned_responses": self.learned_responses,
            "knowledge_base": self.knowledge_base,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            
    def load(self, path: str):
        """Load conversation engine state."""
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            self.conversations.update(data.get("conversations", {}))
            self.learned_responses.update(data.get("learned_responses", {}))
            self.knowledge_base.update(data.get("knowledge_base", {}))


class IntentClassifier:
    """Fast intent classification using pattern matching."""
    
    def __init__(self):
        self.intent_keywords: Dict[str, List[str]] = {
            "greeting": ["hello", "hi", "hey", "howdy", "morning", "afternoon", "evening"],
            "farewell": ["bye", "goodbye", "later", "thanks", "thank you", "see you"],
            "question": ["what", "how", "why", "when", "where", "who", "which", "?"],
            "command": ["do", "make", "create", "start", "stop", "run", "show", "help"],
            "request": ["please", "can you", "would you", "could you", "help me"],
            "affirmation": ["yes", "yeah", "sure", "ok", "okay", "correct", "right"],
            "negation": ["no", "nope", "not", "don't", "won't", "can't"],
            "emotion": ["feel", "happy", "sad", "angry", "excited", "worried", "love", "hate"],
        }
        
        self.intent_scores: Dict[str, float] = {}
        
    def classify(self, text: str) -> Dict[str, Any]:
        """Classify intent of text."""
        text_lower = text.lower()
        scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[intent] = score / len(keywords)
                
        if not scores:
            return {
                "intent": "unknown",
                "confidence": 0.3,
                "scores": {}
            }
            
        best_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(0.95, scores[best_intent] * 2)
        
        return {
            "intent": best_intent,
            "confidence": confidence,
            "scores": scores
        }
        
    def add_intent_keyword(self, intent: str, keyword: str):
        """Add a keyword for an intent."""
        if intent not in self.intent_keywords:
            self.intent_keywords[intent] = []
        if keyword not in self.intent_keywords[intent]:
            self.intent_keywords[intent].append(keyword)


class PretrainedDaemon:
    """
    Pre-trained daemon that's ready to converse immediately.
    
    Combines:
    - Pre-loaded conversation patterns
    - Intent classification
    - Knowledge base
    - Response generation
    - Learning capability
    """
    
    def __init__(self, config: BootstrapConfig = None):
        self.config = config or BootstrapConfig()
        self.data_dir = Path(os.path.expanduser(self.config.data_dir))
        
        # Components
        self.conversation_engine = ConversationEngine()
        self.intent_classifier = IntentClassifier()
        
        # State
        self.conversation_history: List[Dict] = []
        self.is_initialized = False
        self.stats = {
            "conversations": 0,
            "learned_patterns": 0,
            "knowledge_entries": 0
        }
        
    def initialize(self, progress_callback: Callable = None, verbose: bool = None):
        """
        Initialize the pre-trained daemon.
        
        Args:
            progress_callback: Function(step, total, message)
            verbose: Override config verbose setting
        """
        total_steps = 5
        should_print = verbose if verbose is not None else self.config.verbose
        
        def report(step, message):
            if progress_callback:
                progress_callback(step, total_steps, message)
            if should_print:
                print(f"[Bootstrap] Step {step}/{total_steps}: {message}")
                
        # Step 1: Create directories
        report(1, "Setting up directories...")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 2: Load pre-trained conversation data
        report(2, "Loading conversation patterns...")
        self.conversation_engine.load_pretrained_data()
        
        # Step 3: Load any saved state
        report(3, "Loading saved state...")
        state_path = self.data_dir / "daemon_state.json"
        if state_path.exists():
            self.conversation_engine.load(str(state_path))
            
        # Step 4: Initialize tokenizer and embeddings (if needed)
        report(4, "Preparing language models...")
        self._prepare_models()
        
        # Step 5: Finalize
        report(5, "Finalizing initialization...")
        self.is_initialized = True
        self._update_stats()
        
        if self.config.verbose:
            print(f"[Bootstrap] Initialization complete!")
            print(f"  - Conversations: {self.stats['conversations']}")
            print(f"  - Knowledge entries: {self.stats['knowledge_entries']}")
            
    def _prepare_models(self):
        """Prepare NLP models with pre-training data."""
        # This will be called to ensure models are ready
        # The actual training happens in the NativeLLM when needed
        pass
        
    def _update_stats(self):
        """Update statistics."""
        self.stats["conversations"] = len(self.conversation_engine.conversations)
        self.stats["learned_patterns"] = len(self.conversation_engine.learned_responses)
        self.stats["knowledge_entries"] = len(self.conversation_engine.knowledge_base)
        
    def respond(self, user_input: str) -> str:
        """
        Generate a response to user input.
        
        Uses pre-trained patterns first, falls back to generation if needed.
        """
        if not self.is_initialized:
            self.initialize()
            
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Detect intent
        intent_result = self.intent_classifier.classify(user_input)
        intent = intent_result["intent"]
        
        # Try to find pre-trained response
        response = self.conversation_engine.find_response(user_input)
        
        if response is None:
            # Generate contextual response based on intent
            response = self._generate_fallback_response(user_input, intent)
            
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
        
    def _generate_fallback_response(self, user_input: str, intent: str) -> str:
        """Generate a fallback response when no pattern matches."""
        # Intent-based responses
        if intent == "greeting":
            return self.conversation_engine.get_template_response("greeting")
        elif intent == "farewell":
            return "Goodbye! Feel free to come back anytime."
        elif intent == "question":
            return "That's a good question. Let me think about that and provide you with helpful information."
        elif intent == "command":
            return "I understand you want me to do something. Could you be more specific about what you need?"
        elif intent == "request":
            return "I'd be happy to help with that. What specifically would you like me to do?"
        elif intent == "emotion":
            return self.conversation_engine.get_template_response("empathy")
        elif intent == "affirmation":
            return "Great! What would you like to do next?"
        elif intent == "negation":
            return "Understood. Is there something else I can help you with?"
        else:
            return "I'm here to help. Could you tell me more about what you need?"
            
    def learn(self, user_input: str, correct_response: str):
        """Teach the daemon a new response pattern."""
        self.conversation_engine.learn_response(user_input, correct_response)
        self.stats["learned_patterns"] += 1
        
    def add_knowledge(self, topic: str, information: str):
        """Add knowledge to the daemon."""
        self.conversation_engine.add_knowledge(topic, information)
        self.stats["knowledge_entries"] += 1
        
    def save_state(self):
        """Save the daemon's state."""
        state_path = self.data_dir / "daemon_state.json"
        self.conversation_engine.save(str(state_path))
        
        # Save history
        history_path = self.data_dir / "conversation_history.json"
        with open(history_path, "w") as f:
            json.dump(self.conversation_history[-100:], f, indent=2)  # Keep last 100
            
    def get_conversation_context(self, num_turns: int = 5) -> str:
        """Get recent conversation context."""
        recent = self.conversation_history[-num_turns * 2:]  # Each turn has user + assistant
        
        context_parts = []
        for entry in recent:
            role = entry["role"].capitalize()
            content = entry["content"]
            context_parts.append(f"{role}: {content}")
            
        return "\n".join(context_parts)
        
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        
    def get_status(self) -> Dict:
        """Get daemon status."""
        return {
            "initialized": self.is_initialized,
            "stats": self.stats,
            "history_length": len(self.conversation_history),
            "data_dir": str(self.data_dir)
        }


def bootstrap_daemon(config: BootstrapConfig = None) -> PretrainedDaemon:
    """
    Bootstrap a pre-trained daemon ready for conversations.
    
    Returns:
        Initialized PretrainedDaemon instance
    """
    daemon = PretrainedDaemon(config)
    daemon.initialize()
    return daemon


def create_pretrained_native_llm():
    """
    Create a NativeLLM instance with pre-trained components.
    
    Returns an LLM that's ready for basic conversations immediately.
    """
    from unimind.models.native.native_llm import NativeLLM, NativeLLMConfig
    from unimind.models.native.tokenizer import BPETokenizer
    from unimind.models.native.embeddings import NativeEmbeddingEngine
    
    print("[Bootstrap] Creating pre-trained Native LLM...")
    
    # Get training texts
    training_texts = get_all_training_texts()
    print(f"[Bootstrap] Training on {len(training_texts)} text samples...")
    
    # Create and train tokenizer
    print("[Bootstrap] Training tokenizer...")
    tokenizer = BPETokenizer()
    tokenizer.train(training_texts, vocab_size=4000, min_frequency=1)
    
    # Create and train embeddings
    print("[Bootstrap] Training embeddings...")
    embedding_engine = NativeEmbeddingEngine()
    embedding_engine.train(training_texts, model="tfidf")
    
    # Create LLM with pre-trained components
    config = NativeLLMConfig(
        embedding_dimension=384,
        max_tokens=256,
        temperature=0.7
    )
    
    llm = NativeLLM(config)
    llm.tokenizer = tokenizer
    llm.embedding_engine = embedding_engine
    
    print("[Bootstrap] Pre-trained Native LLM ready!")
    
    return llm


# =============================================================================
# QUICK START FUNCTIONS
# =============================================================================

_pretrained_daemon: Optional[PretrainedDaemon] = None


def get_pretrained_daemon() -> PretrainedDaemon:
    """Get the global pre-trained daemon instance."""
    global _pretrained_daemon
    if _pretrained_daemon is None:
        _pretrained_daemon = bootstrap_daemon()
    return _pretrained_daemon


def quick_respond(user_input: str) -> str:
    """Quick response using pre-trained daemon."""
    daemon = get_pretrained_daemon()
    return daemon.respond(user_input)


def quick_teach(user_input: str, response: str):
    """Quick teach a new pattern."""
    daemon = get_pretrained_daemon()
    daemon.learn(user_input, response)
