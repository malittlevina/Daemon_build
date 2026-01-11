# nlu/nlu_engine.py
"""
NLU Engine - Natural Language Understanding

Interprets user input and routes to appropriate handlers,
integrating with the symbolic state and scroll engine.
"""

import os
import datetime
from typing import Optional, Dict, Any

# Safe imports with fallbacks
try:
    from lam.symbolic_state import update_state_with_input
except ImportError:
    def update_state_with_input(user_input, source="user"):
        print(f"[SymbolicState] Processing: {user_input}")
        return None

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters


class NLUEngine:
    """
    Natural Language Understanding Engine.
    
    Processes user input through:
    1. Learned phrase matching
    2. Pattern-based intent detection
    3. Symbolic state updates
    4. Scroll invocation
    5. Fallback to LLM if configured
    """
    
    module_name = "nlu_engine"
    dependencies = []
    
    def __init__(self, scroll_engine=None):
        self.scroll_engine = scroll_engine
        self.learned_phrases: Dict[str, str] = {}
        self.use_ollama_fallback = False
        self._kernel = None
        
        # Intent patterns with handlers
        self.intent_patterns = {
            "learn": {
                "keywords": ["learn", "study", "teach me", "explain"],
                "handler": self._handle_learn_intent
            },
            "task": {
                "keywords": ["run task", "execute", "do"],
                "handler": self._handle_task_intent
            },
            "optimize": {
                "keywords": ["optimize", "improve", "upgrade"],
                "handler": self._handle_optimize_intent
            },
            "reflect": {
                "keywords": ["reflect", "think about", "analyze"],
                "handler": self._handle_reflect_intent
            },
            "help": {
                "keywords": ["help", "what can", "how do"],
                "handler": self._handle_help_intent
            },
            "scroll": {
                "keywords": ["scroll", "ritual", "invoke"],
                "handler": self._handle_scroll_intent
            }
        }
        
        print("[NLUEngine] Initialized.")
    
    def initialize(self, kernel) -> bool:
        """Initialize with kernel reference."""
        self._kernel = kernel
        return True
    
    def start(self) -> bool:
        return True
    
    def stop(self) -> bool:
        return True
    
    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "learned_phrases": len(self.learned_phrases),
            "intent_patterns": len(self.intent_patterns)
        }
    
    def interpret(self, user_input: str) -> Optional[str]:
        """
        Interpret user input and return appropriate response.
        
        Args:
            user_input: The raw user input string
            
        Returns:
            Response string or None if no match
        """
        if not user_input:
            return None
        
        # Check learned phrases first
        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]
        
        input_lower = user_input.lower()
        
        # Check intent patterns
        for intent_name, intent_config in self.intent_patterns.items():
            for keyword in intent_config["keywords"]:
                if keyword in input_lower:
                    handler = intent_config["handler"]
                    result = handler(user_input)
                    if result:
                        return result
        
        # Update symbolic state
        try:
            state_result = update_state_with_input(user_input, source="nlu")
            if state_result:
                return state_result
        except Exception as e:
            print(f"[NLUEngine] State update error: {e}")
        
        # Try Ollama fallback if enabled
        if self.use_ollama_fallback:
            return self._ollama_fallback(user_input)
        
        return "[NLUEngine] No known intent"
    
    def _handle_learn_intent(self, user_input: str) -> Optional[str]:
        """Handle learning/study intent."""
        if self.scroll_engine:
            # Extract topic
            import re
            match = re.search(r'(?:learn|study)\s+(?:about\s+)?(.+)', user_input.lower())
            if match:
                topic = match.group(1).strip()
                try:
                    result = self.scroll_engine.invoke("study topic", topic)
                    return f"[NLU] Learning about: {topic}\n{result}"
                except Exception as e:
                    return f"[NLU] Starting learning mode for: {topic}"
        
        return "[NLU] Entering learning mode."
    
    def _handle_task_intent(self, user_input: str) -> Optional[str]:
        """Handle task execution intent."""
        if self.scroll_engine:
            # Extract task description
            import re
            match = re.search(r'(?:run task|execute|do)\s+(.+)', user_input.lower())
            if match:
                task = match.group(1).strip()
                try:
                    result = self.scroll_engine.invoke("run task", task)
                    return f"[NLU] Task result: {result}"
                except Exception as e:
                    return f"[NLU] Task scheduled: {task}"
        
        return "[NLU] Task mode activated."
    
    def _handle_optimize_intent(self, user_input: str) -> Optional[str]:
        """Handle optimization intent."""
        if self.scroll_engine:
            try:
                result = self.scroll_engine.invoke("optimize self")
                return f"[NLU] Optimization: {result}"
            except Exception as e:
                pass
        
        return "[NLU] Self-optimization initiated."
    
    def _handle_reflect_intent(self, user_input: str) -> Optional[str]:
        """Handle reflection intent."""
        return "[NLU] Entering reflection mode."
    
    def _handle_help_intent(self, user_input: str) -> Optional[str]:
        """Handle help intent."""
        return """[NLU] Available commands:
- 'learn <topic>' or 'study <topic>' - Learn about a topic
- 'run task <description>' - Execute a task
- 'optimize' - Run self-optimization
- 'reflect' - Trigger introspection
- 'scroll <name>' - Invoke a scroll/routine
- 'help' - Show this message"""
    
    def _handle_scroll_intent(self, user_input: str) -> Optional[str]:
        """Handle scroll invocation intent."""
        if self.scroll_engine:
            import re
            match = re.search(r'(?:scroll|invoke)\s+(.+)', user_input.lower())
            if match:
                scroll_name = match.group(1).strip()
                try:
                    result = self.scroll_engine.invoke(scroll_name)
                    return f"[NLU] Scroll '{scroll_name}' result: {result}"
                except Exception as e:
                    return f"[NLU] Scroll '{scroll_name}' not found."
        
        return "[NLU] Scroll engine not available."
    
    def _ollama_fallback(self, user_input: str) -> Optional[str]:
        """Fallback to Ollama for unknown inputs."""
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "run", "prometheus", user_input],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "[NLUEngine] Ollama fallback failed."
        except Exception as e:
            return f"[NLUEngine] Fallback exception: {e}"
    
    def learn_phrase(self, phrase: str, response: str):
        """Teach the NLU a new phrase-response mapping."""
        self.learned_phrases[phrase] = response
        print(f"[NLUEngine] Learned: '{phrase}' -> '{response}'")
    
    def add_intent_pattern(
        self,
        intent_name: str,
        keywords: list,
        handler: callable
    ):
        """Add a new intent pattern."""
        self.intent_patterns[intent_name] = {
            "keywords": keywords,
            "handler": handler
        }
        print(f"[NLUEngine] Added intent pattern: {intent_name}")


def run_self_analysis():
    """Run self-analysis for nightly reflection."""
    reflection = {
        "timestamp": str(datetime.datetime.now()),
        "status": "Running self-analysis",
        "insights": []
    }
    
    # Add insights based on log analysis
    try:
        if os.path.exists("logs/task_memory.log"):
            with open("logs/task_memory.log", "r") as f:
                tasks = f.readlines()
                reflection["insights"].append(f"Processed {len(tasks)} tasks")
    except Exception as e:
        reflection["insights"].append(f"Log analysis error: {e}")
    
    # Log reflection
    codex_summary = (
        f"Self-reflection at {reflection['timestamp']}\n"
        f"Status: {reflection['status']}\n"
        f"Insights: {'; '.join(reflection['insights'])}"
    )
    
    os.makedirs("logs", exist_ok=True)
    with open(REFLECTION_LOG, "a") as log_file:
        log_file.write(codex_summary + "\n\n")
    
    truncate_log_if_needed()
    
    return codex_summary


def truncate_log_if_needed():
    """Truncate reflection log if it exceeds max size."""
    if not os.path.exists(REFLECTION_LOG):
        return
    with open(REFLECTION_LOG, "r") as f:
        content = f.read()
    if len(content) > MAX_LOG_SIZE:
        with open(REFLECTION_LOG, "w") as f:
            f.write(content[-MAX_LOG_SIZE:])


def nightly_reflection():
    """Execute nightly reflection routine."""
    print("[NLUEngine] Executing nightly reflection...")
    result = run_self_analysis()
    print("[NLUEngine] Reflection complete.")
    return result
