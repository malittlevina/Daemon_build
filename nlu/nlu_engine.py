import os
import datetime
from codex.codex_engine import log_codex_entry
from code.code_generator import propose_improvements
from unimind.reasoner import symbolic_reasoning_chain
from lam.symbolic_state import update_state_with_input

REFLECTION_LOG = "logs/self_reflection.log"
MAX_LOG_SIZE = 10000  # characters

from core.personality_engine import get_personality_engine
from codex.curriculum import CurriculumManager
from code_tools.code_master import CodeMaster
from training.trainer import Trainer
from cognitive.brain.evolution import EvolutionaryPlanner
from codex.knowledge_graph import KnowledgeGraph
from codex.lexicon import Lexicon

class NLUEngine:
    def __init__(self, scroll_engine=None):
        self.learned_phrases = {}
        self.use_ollama_fallback = True
        self.scroll_engine = scroll_engine
        from lam.lam_planner import plan_next_action
        self.lam_planner = plan_next_action
        self.personality = get_personality_engine()
        self.curriculum = CurriculumManager()
        self.graph = KnowledgeGraph()
        self.lexicon = Lexicon()
        self.code_master = CodeMaster()
        self.trainer = Trainer()
        self.hi_tuner = None 
        
        # Actions available to the Evolutionary Planner
        self.available_actions = [
            "study topic", "optimize self", "explore world", 
            "check status", "reflect", "scan environment"
        ]
        self.evo_planner = EvolutionaryPlanner(self.available_actions)

    def interpret(self, user_input, context_drives=None):
        raw_response = self._get_raw_response(user_input)
        
        # Modulate if we have access to drives
        if context_drives:
            return self.personality.modulate_response(raw_response, context_drives)
        return raw_response

    def _get_raw_response(self, user_input):
        # -1. Check for Training Feedback
        if user_input.lower() in ["good job", "good bot", "correct"]:
            if self.trainer.train_on_last_action(1.0):
                return "Thank you. Neural weights updated."
            return "Thank you."
            
        if user_input.lower() in ["bad job", "wrong", "incorrect"]:
            if self.trainer.train_on_last_action(-1.0):
                return "Understood. Behavior penalized."
            return "I apologize."

        # 0. Check for Self-Sufficient Planning (Evolutionary)
        if "plan" in user_input.lower() or "solve" in user_input.lower():
            # Use Genetic Algorithm instead of LLM
            fitness = self.evo_planner.create_mock_fitness(user_input.lower())
            best_plan = self.evo_planner.generate_plan(fitness)
            plan_str = " -> ".join(best_plan)
            
            # Execute the first step?
            # For now just report the plan
            return f"Evolutionary Plan Generated: {plan_str}"

        # 0.5 Check for Ingestion Command
        if "review code" in user_input.lower():
             # In a real CLI, we might ask for the code next, or check clipboard.
             # Here we assume the user might paste it or we just give instructions.
             return "Please provide the code snippet you'd like me to review."
        
        if "generate" in user_input.lower() and "pattern" in user_input.lower():
             # Extract pattern
             pattern = user_input.lower().split("pattern")[-1].strip()
             scaffold = self.code_master.generate_scaffold(pattern)
             return f"Here is a scaffold for the {pattern} pattern:\n```python\n{scaffold}\n```"

        # 0.5 Check for Ingestion Command
        if user_input.lower().startswith("ingest"):
            # ingest /path/to/file
            path = user_input.replace("ingest", "").strip()
            if os.path.exists(path):
                from codex.ingestion import ingest_documents
                # Hack: ingest_documents takes a folder, we might need a file helper
                # For now, if it's a file, we can't easily use ingest_documents without refactor.
                # Let's just mock it or assume folder.
                if os.path.isdir(path):
                    ingest_documents(path)
                    return f"Ingested all documents in {path}."
                else:
                    return "Please provide a directory path for ingestion."
            else:
                 return f"I cannot find the path: {path}"

        # 1. Check for Knowledge Queries (Simple keyword check)
        if "what is" in user_input.lower() or "tell me about" in user_input.lower() or "define" in user_input.lower():
            # Extract basic query
            query = user_input.lower().replace("what is", "").replace("tell me about", "").replace("define", "").strip()
            
            # A. Check Lexicon (Dictionary)
            definition = self.lexicon.lookup(query)
            if definition:
                return f"[Dictionary] {query.title()} ({definition['pos']}): {definition['def']}"

            # B. Check Curriculum (Structured)
            results = self.curriculum.query(query)
            if results:
                best = results[0]
                return f"[Knowledge: {best['source_pack']}] {best['title']}: {best['content']}"
            
            # C. Check Graph (Associative)
            related = self.graph.get_related(query)
            if related:
                return f"[Associative Memory] '{query}' is related to: {', '.join(related)}. I can try to connect these concepts."
            
            # D. Unknown - Trigger Curiosity
            return f"I do not have a definition for '{query}'. If you define it for me (e.g. 'Define {query} as...'), I will learn it."

        # 1.5 Handle User Teaching Definitions
        if user_input.lower().startswith("define") and " as " in user_input.lower():
            # Format: "Define [Word] as [Definition]"
            parts = user_input.lower().replace("define", "").split(" as ")
            if len(parts) >= 2:
                word = parts[0].strip()
                meaning = parts[1].strip()
                self.lexicon.define(word, meaning)
                return f"Understood. I have added '{word}' to my dictionary."

        if user_input in self.learned_phrases:
            return self.learned_phrases[user_input]
            
        # ... existing logic ...
        
        # Try LAM first
        try:
            # We pass a simplified symbolic state for now
            lam_response = self.lam_planner(user_input, {"context": "daemon_cli"})
            if lam_response and lam_response.startswith("[LAM]"):
                intent = lam_response.replace("[LAM] ", "").lower().strip()
                # print(f"[NLU] LAM Intent Detected: {intent}")
                
                # If we have a scroll engine, try to execute the intent
                if self.scroll_engine:
                    if "world interaction" in intent:
                         return self.scroll_engine.invoke("initiate world interaction scroll")
                    elif "study" in intent:
                        # Extract topic crudely
                        topic = user_input.replace("study", "").strip()
                        return self.scroll_engine.invoke("study topic", topic)
                    elif "optimize" in intent:
                        return self.scroll_engine.invoke("optimize self")
                    # Add more mappings as needed
                
                return f"I've identified the intent '{intent}', but I'm not sure how to execute it yet."
                
        except Exception as e:
            print(f"[NLU] LAM Error: {e}")

        # Fallback to older symbolic logic
        try:
            result = update_state_with_input(user_input, source="nlu")
            if result: return result
        except TypeError:
            pass

        if self.use_ollama_fallback:
            try:
                import subprocess
                result = subprocess.run(["ollama", "run", "prometheus", user_input], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass

        return "I'm not sure how to respond to that."

def run_self_analysis():
    reflection = {}

    # Symbolic diagnostic prompt
    reflection["timestamp"] = str(datetime.datetime.now())
    reflection["status"] = "Running self-analysis"
    reflection["reasoning_trace"] = symbolic_reasoning_chain("analyze internal state for weaknesses")

    # Improvement suggestions
    reflection["proposed_improvements"] = propose_improvements("Nightly self-analysis of daemon")

    # Log reflection to Codex
    codex_summary = (
        f"Self-reflection at {reflection['timestamp']}\n"
        f"Status: {reflection['status']}\n"
        f"Symbolic Reasoning: {reflection['reasoning_trace']}\n"
        f"Proposed Fixes: {reflection['proposed_improvements']}"
    )
    log_codex_entry("reflection", codex_summary)

    # Append to local log
    with open(REFLECTION_LOG, "a") as log_file:
        log_file.write(codex_summary + "\n\n")

    truncate_log_if_needed()

    return codex_summary

def truncate_log_if_needed():
    if not os.path.exists(REFLECTION_LOG):
        return
    with open(REFLECTION_LOG, "r") as f:
        content = f.read()
    if len(content) > MAX_LOG_SIZE:
        with open(REFLECTION_LOG, "w") as f:
            f.write(content[-MAX_LOG_SIZE:])

def nightly_reflection():
    print("[SelfReflector] Executing nightly reflection...")
    result = run_self_analysis()
    print("[SelfReflector] Reflection complete.")
    return result