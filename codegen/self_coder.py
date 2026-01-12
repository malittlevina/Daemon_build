# codegen/self_coder.py
"""
Self-Coder Module (Legacy)
==========================
Original self-coding module using OpenAI.
See self_evolution.py for the enhanced version.
"""

from typing import Optional
import subprocess

# Optional OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

# Optional codex import
try:
    from codex.ingestion import load_codex_memory
except ImportError:
    def load_codex_memory():
        return ""

# Optional introspection import
try:
    from introspection.reflection_journal import record_reflection
except ImportError:
    def record_reflection(text):
        pass


class SelfCoder:
    """
    Self-coding capability for the daemon.
    Can use OpenAI, Ollama, or other LLMs for code generation.
    """
    
    def __init__(self, use_openai: bool = False, use_ollama: bool = True):
        self.use_openai = use_openai and OPENAI_AVAILABLE
        self.use_ollama = use_ollama
    
    def generate_code(self, prompt: str, language: str = "python") -> str:
        """
        Generate code from a natural language prompt.
        
        Args:
            prompt: Description of what code to generate
            language: Target programming language
        
        Returns:
            Generated code string
        """
        if self.use_openai and OPENAI_AVAILABLE:
            return self._generate_with_openai(prompt)
        elif self.use_ollama:
            return self._generate_with_ollama(prompt, language)
        else:
            return f"# Code generation not available\n# Request: {prompt}"
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate code using OpenAI."""
        try:
            context = load_codex_memory()
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt}
                ]
            )
            code = response['choices'][0]['message']['content']
            record_reflection("Generated new code:\n" + code)
            return code
        except Exception as e:
            return f"# OpenAI error: {e}"
    
    def _generate_with_ollama(self, prompt: str, language: str = "python") -> str:
        """Generate code using Ollama."""
        try:
            model = "codellama:13b-python" if language == "python" else "codellama:13b"
            
            full_prompt = f"Write {language} code that: {prompt}\n\nProvide only the code, no explanations."
            
            result = subprocess.run(
                ['ollama', 'run', model],
                input=full_prompt,
                text=True,
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                code = result.stdout.strip()
                record_reflection("Generated new code:\n" + code)
                return code
            
            return f"# Ollama error: {result.stderr}"
            
        except Exception as e:
            return f"# Code generation error: {e}"


# Legacy function for backward compatibility
def generate_code(prompt: str) -> str:
    """Legacy function - use SelfCoder class instead."""
    coder = SelfCoder()
    return coder.generate_code(prompt)
