import random
from typing import Optional

# Optional dependency
try:
    from codex.curriculum import CurriculumManager
    CURRICULUM_AVAILABLE = True
except ImportError:
    CurriculumManager = None
    CURRICULUM_AVAILABLE = False


class CodeMaster:
    def __init__(self):
        self.curriculum = None
        self.pack = None
        
        if CURRICULUM_AVAILABLE:
            try:
                self.curriculum = CurriculumManager()
                self.pack = self.curriculum.packs.get("MasterCoding")
            except Exception:
                pass
        
    def get_advice(self, topic: str):
        """
        Retrieves expert advice on a coding topic.
        """
        if not self.pack:
            # Try reloading if missing (e.g. created after init)
            self.curriculum.load_all()
            self.pack = self.curriculum.packs.get("MasterCoding")
            
        if not self.pack:
            return "I haven't studied the MasterCoding curriculum yet."
            
        results = self.pack.search(topic)
        if not results:
            return f"I don't have specific advice on '{topic}' yet, but I recommend adhering to SOLID principles."
            
        best = results[0]
        return f"**{best['title']}**: {best['content']}"

    def review_code(self, code_snippet: str) -> str:
        """
        Simulates a code review based on heuristics and known patterns.
        (Real implementation would parse AST, this is heuristic/mock).
        """
        critique = []
        
        # 1. Check Function Length
        lines = code_snippet.split('\n')
        if len(lines) > 50:
            critique.append("- **Refactor**: This code block is quite long. Consider breaking it into smaller functions (SRP).")
            
        # 2. Check Naming (Simple heuristic)
        if any(len(word) == 1 and word not in ['i', 'x', 'y', 'z'] for word in code_snippet.split()):
             critique.append("- **Naming**: Avoid single-letter variable names outside of loops. Be descriptive.")
             
        # 3. Check hardcoded values
        if any(char.isdigit() for char in code_snippet) and "const" not in code_snippet.lower() and "=" in code_snippet:
             critique.append("- **Magic Numbers**: I see hardcoded numbers. Consider moving them to named constants.")

        if not critique:
            return "✅ This code looks clean to me! It seems to follow basic readability standards."
            
        return "### Code Review Feedback:\n" + "\n".join(critique)

    def generate_scaffold(self, pattern_name: str) -> str:
        """
        Generates code scaffolding for a known design pattern.
        """
        if "singleton" in pattern_name.lower():
            return """class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
            # Initialize configuration
        return cls._instance
"""
        elif "factory" in pattern_name.lower():
             return """class Product:
    def operation(self):
        pass

class ConcreteProductA(Product):
    def operation(self):
        return "Result of ConcreteProductA"

class Creator:
    def factory_method(self):
        return Product()

    def some_operation(self):
        product = self.factory_method()
        result = f"Creator: {product.operation()}"
        return result
"""
        elif "observer" in pattern_name.lower():
            return """class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

class Observer:
    def update(self, subject):
        pass
"""
        else:
            return f"# I don't have a template for '{pattern_name}' yet, but I can look it up in my curriculum."

