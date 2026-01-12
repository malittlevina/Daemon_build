# nlu/nlu_engine.py
"""
NLU Engine - Natural Language Understanding
============================================
Interprets user input to understand intent and route to appropriate handlers.
Integrates with Unimind's cognition pipeline for human-like understanding.
"""

import os
import datetime
from typing import Optional, Dict, Any, List

# Import from cognition pipeline
try:
    from unimind.cognition import CognitionPipeline, ThoughtResult, Intent, get_cognition
    COGNITION_AVAILABLE = True
except ImportError:
    COGNITION_AVAILABLE = False

# Import LAM for action planning
try:
    from lam.symbolic_state import update_state_with_input, symbolic_state
    LAM_AVAILABLE = True
except ImportError:
    LAM_AVAILABLE = False


class NLUEngine:
    """
    Natural Language Understanding Engine.
    Routes user input through cognition pipeline and to appropriate handlers.
    """
    
    def __init__(self, scroll_engine=None):
        self.scroll_engine = scroll_engine
        self.learned_phrases: Dict[str, str] = {}
        self.use_ollama_fallback = True
        
        # Initialize cognition pipeline
        self.cognition: Optional[CognitionPipeline] = None
        if COGNITION_AVAILABLE:
            try:
                self.cognition = get_cognition()
                print("[NLUEngine] Cognition pipeline connected.")
            except Exception as e:
                print(f"[NLUEngine] Cognition pipeline unavailable: {e}")
        
        # Intent handlers
        self.intent_handlers: Dict[str, callable] = {}
        self._register_default_handlers()
        
        print("[NLUEngine] Initialized.")
    
    def _register_default_handlers(self):
        """Register default intent handlers."""
        self.intent_handlers['status'] = self._handle_status
        self.intent_handlers['help'] = self._handle_help
        self.intent_handlers['reflect'] = self._handle_reflect
    
    def register_handler(self, intent: str, handler: callable):
        """Register a custom intent handler."""
        self.intent_handlers[intent] = handler
    
    def interpret(self, user_input: str) -> Optional[str]:
        """
        Interpret user input and return appropriate response.
        
        Pipeline:
        1. Check learned phrases
        2. Process through cognition pipeline (NLU → LLM → LAM)
        3. Route to intent handlers
        4. Update symbolic state
        5. Fall back to LLM if needed
        """
        # Check learned phrases first
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]
        
        # Process through cognition pipeline
        if self.cognition:
            try:
                result = self.cognition.process(user_input)
                
                # Check for registered handler
                intent_value = result.intent.value if hasattr(result.intent, 'value') else str(result.intent)
                if intent_value in self.intent_handlers:
                    handler_result = self.intent_handlers[intent_value](user_input, result)
                    if handler_result:
                        return handler_result
                
                # Use LLM response if available
                if result.response:
                    # Update symbolic state
                    if LAM_AVAILABLE:
                        try:
                            update_state_with_input(user_input)
                        except Exception:
                            pass
                    
                    return result.response
                    
            except Exception as e:
                print(f"[NLUEngine] Cognition error: {e}")
        
        # Update symbolic state
        if LAM_AVAILABLE:
            try:
                state_result = update_state_with_input(user_input)
                if state_result:
                    return state_result
            except Exception as e:
                print(f"[NLUEngine] LAM error: {e}")
        
        # Pattern matching fallback
        result = self._pattern_match(user_input)
        if result:
            return result
        
        # Ollama fallback
        if self.use_ollama_fallback:
            return self._ollama_fallback(user_input)
        
        return "[NLUEngine] No known intent"
    
    def _pattern_match(self, user_input: str) -> Optional[str]:
        """Simple pattern matching for common phrases."""
        input_lower = user_input.lower()
        
        # Greeting patterns
        if any(g in input_lower for g in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return "Hello! How can I assist you today?"
        
        # Farewell patterns
        if any(f in input_lower for f in ['bye', 'goodbye', 'see you', 'farewell']):
            return "Goodbye! Take care."
        
        # Gratitude patterns
        if any(t in input_lower for t in ['thank', 'thanks', 'appreciate']):
            return "You're welcome!"
        
        # Status patterns
        if 'how are you' in input_lower or 'status' in input_lower:
            return self._handle_status(user_input, None)
        
        # Help patterns
        if 'help' in input_lower:
            return self._handle_help(user_input, None)
        
        # Scroll patterns (if scroll engine available)
        if self.scroll_engine:
            if 'optimize' in input_lower:
                return self.scroll_engine.invoke('optimize self')
            if 'study' in input_lower:
                # Extract topic
                topic = input_lower.replace('study', '').strip()
                return self.scroll_engine.invoke('study topic', topic or 'general')
        
        return None
    
    def _ollama_fallback(self, user_input: str) -> str:
        """Fallback to Ollama for unhandled input."""
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "run", "llama3"],
                input=user_input,
                text=True,
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip()
            else:
                return "[NLUEngine] Ollama fallback failed."
        except FileNotFoundError:
            return "[NLUEngine] Ollama not installed. Install with: curl -fsSL https://ollama.com/install.sh | sh"
        except Exception as e:
            return f"[NLUEngine] Fallback error: {e}"
    
    def _handle_status(self, user_input: str, result: Optional[ThoughtResult]) -> str:
        """Handle status inquiries."""
        lines = [
            "[Status] Daemon is operational.",
            f"  Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if LAM_AVAILABLE:
            lines.append(f"  Mode: {symbolic_state.get('current_context', {}).get('mode', 'idle')}")
        
        if self.cognition:
            lines.append("  Cognition: Active")
        
        return "\n".join(lines)
    
    def _handle_help(self, user_input: str, result: Optional[ThoughtResult]) -> str:
        """Handle help requests."""
        return """[Help] Available commands:
  - "hello/hi" - Greeting
  - "status" - Check daemon status
  - "observe [something]" - Record an observation
  - "remember [something]" - Store in memory
  - "journal [entry]" - Write diary entry
  - "scan devices" - Discover nearby devices
  - "study [topic]" - Learn about a topic
  - "reflect" - Trigger self-reflection
  - "help" - Show this message
  - "exit" - Shutdown daemon"""
    
    def _handle_reflect(self, user_input: str, result: Optional[ThoughtResult]) -> str:
        """Handle reflection requests."""
        try:
            from unimind.core import get_unimind
            unimind = get_unimind()
            unimind.reflect()
            return "[Reflection] Self-reflection initiated."
        except Exception as e:
            return f"[Reflection] Error: {e}"
    
    def learn(self, phrase: str, response: str):
        """Learn a new phrase-response pair."""
        self.learned_phrases[phrase] = response
        print(f"[NLUEngine] Learned: '{phrase}' → '{response}'")
    
    def forget(self, phrase: str):
        """Forget a learned phrase."""
        if phrase in self.learned_phrases:
            del self.learned_phrases[phrase]
            print(f"[NLUEngine] Forgot: '{phrase}'")
