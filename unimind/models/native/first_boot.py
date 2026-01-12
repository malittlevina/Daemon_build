# unimind/models/native/first_boot.py
# First Boot Initialization - Setup daemon for immediate use

"""
First Boot System

This module handles the first-time initialization of the daemon,
ensuring it's ready to have conversations and understand commands
immediately upon startup.
"""

import os
import json
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FirstBootStatus:
    """Status of first boot initialization."""
    is_first_boot: bool
    initialized_at: Optional[str]
    components_ready: Dict[str, bool]
    version: str = "1.0.0"


class FirstBootInitializer:
    """
    Handles first-boot setup and initialization.
    
    Ensures the daemon is ready for:
    - Basic conversations
    - Command understanding
    - Knowledge queries
    - Learning new patterns
    """
    
    MARKER_FILE = ".daemon_initialized"
    STATE_FILE = "first_boot_state.json"
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or os.path.expanduser("~/.thoth"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.marker_path = self.data_dir / self.MARKER_FILE
        self.state_path = self.data_dir / self.STATE_FILE
        
        self.status = FirstBootStatus(
            is_first_boot=not self.marker_path.exists(),
            initialized_at=None,
            components_ready={}
        )
        
    def is_first_boot(self) -> bool:
        """Check if this is the first boot."""
        return not self.marker_path.exists()
        
    def run_first_boot(
        self,
        progress_callback: Callable[[int, int, str], None] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Run first-boot initialization.
        
        Args:
            progress_callback: Called with (step, total_steps, message)
            verbose: Print progress messages
            
        Returns:
            Initialization result
        """
        total_steps = 7
        results = {
            "success": True,
            "steps_completed": 0,
            "errors": [],
            "warnings": []
        }
        
        def report(step: int, message: str):
            if progress_callback:
                progress_callback(step, total_steps, message)
            if verbose:
                print(f"[First Boot] ({step}/{total_steps}) {message}")
                
        try:
            # Step 1: Create directory structure
            report(1, "Creating directory structure...")
            self._create_directories()
            self.status.components_ready["directories"] = True
            results["steps_completed"] += 1
            
            # Step 2: Initialize model manager
            report(2, "Initializing model manager...")
            self._init_model_manager()
            self.status.components_ready["model_manager"] = True
            results["steps_completed"] += 1
            
            # Step 3: Load pre-trained conversation data
            report(3, "Loading conversation patterns...")
            self._load_pretrained_data()
            self.status.components_ready["pretrained_data"] = True
            results["steps_completed"] += 1
            
            # Step 4: Initialize tokenizer
            report(4, "Training tokenizer...")
            self._init_tokenizer()
            self.status.components_ready["tokenizer"] = True
            results["steps_completed"] += 1
            
            # Step 5: Initialize embeddings
            report(5, "Training embeddings...")
            self._init_embeddings()
            self.status.components_ready["embeddings"] = True
            results["steps_completed"] += 1
            
            # Step 6: Create NativeLLM instance
            report(6, "Creating language model...")
            self._create_llm()
            self.status.components_ready["llm"] = True
            results["steps_completed"] += 1
            
            # Step 7: Finalize and save state
            report(7, "Finalizing setup...")
            self._finalize()
            self.status.components_ready["finalized"] = True
            results["steps_completed"] += 1
            
            self.status.initialized_at = datetime.now().isoformat()
            self._save_state()
            
            if verbose:
                print("\n[First Boot] ✓ Initialization complete!")
                print(f"[First Boot] The daemon is now ready for conversations.\n")
                
        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
            if verbose:
                print(f"\n[First Boot] ✗ Error during initialization: {e}")
                
        return results
        
    def _create_directories(self):
        """Create necessary directories."""
        dirs = [
            self.data_dir / "models",
            self.data_dir / "pretrained",
            self.data_dir / "conversations",
            self.data_dir / "knowledge",
            self.data_dir / "cache",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            
    def _init_model_manager(self):
        """Initialize the model manager."""
        from unimind.models.native.model_manager import get_model_manager
        manager = get_model_manager()
        # Model manager auto-initializes
        
    def _load_pretrained_data(self):
        """Load pre-trained conversation data."""
        from unimind.models.native.pretrain_data import (
            get_all_training_texts,
            get_conversation_pairs,
            COMMAND_PATTERNS,
            RESPONSE_TEMPLATES,
            DOMAIN_KNOWLEDGE,
        )
        
        # Save pretrained data for quick loading later
        data = {
            "conversations": dict(get_conversation_pairs()),
            "command_patterns": COMMAND_PATTERNS,
            "response_templates": RESPONSE_TEMPLATES,
            "domain_knowledge": DOMAIN_KNOWLEDGE,
        }
        
        pretrained_path = self.data_dir / "pretrained" / "conversation_data.json"
        with open(pretrained_path, "w") as f:
            json.dump(data, f, indent=2)
            
    def _init_tokenizer(self):
        """Initialize and train the tokenizer."""
        from unimind.models.native.tokenizer import BPETokenizer
        from unimind.models.native.pretrain_data import get_all_training_texts
        
        tokenizer = BPETokenizer()
        training_texts = get_all_training_texts()
        tokenizer.train(training_texts, vocab_size=4000, min_frequency=1)
        
        # Save tokenizer
        tokenizer_path = self.data_dir / "pretrained" / "tokenizer.json"
        tokenizer.save(str(tokenizer_path))
        
    def _init_embeddings(self):
        """Initialize and train embeddings."""
        from unimind.models.native.embeddings import NativeEmbeddingEngine, EmbeddingConfig
        from unimind.models.native.pretrain_data import get_all_training_texts
        
        config = EmbeddingConfig(dimension=384)
        engine = NativeEmbeddingEngine(config)
        
        training_texts = get_all_training_texts()
        engine.train(training_texts, model="tfidf")
        
        # Save embeddings
        engine.save(str(self.data_dir / "pretrained"))
        
    def _create_llm(self):
        """Create and test the NativeLLM."""
        from unimind.models.native.native_llm import NativeLLM
        
        # Create LLM with pre-training
        llm = NativeLLM(pretrain=True)
        
        # Test basic conversation
        response = llm.chat("Hello!")
        assert len(response) > 0, "LLM failed to generate response"
        
    def _finalize(self):
        """Finalize initialization."""
        # Create marker file
        with open(self.marker_path, "w") as f:
            f.write(datetime.now().isoformat())
            
    def _save_state(self):
        """Save initialization state."""
        state = {
            "is_first_boot": False,
            "initialized_at": self.status.initialized_at,
            "components_ready": self.status.components_ready,
            "version": self.status.version
        }
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)
            
    def load_state(self) -> FirstBootStatus:
        """Load saved initialization state."""
        if self.state_path.exists():
            with open(self.state_path) as f:
                data = json.load(f)
            self.status = FirstBootStatus(
                is_first_boot=data.get("is_first_boot", False),
                initialized_at=data.get("initialized_at"),
                components_ready=data.get("components_ready", {}),
                version=data.get("version", "1.0.0")
            )
        return self.status
        
    def reset(self):
        """Reset first boot state (for testing or re-initialization)."""
        if self.marker_path.exists():
            self.marker_path.unlink()
        if self.state_path.exists():
            self.state_path.unlink()
        self.status = FirstBootStatus(
            is_first_boot=True,
            initialized_at=None,
            components_ready={}
        )
        print("[First Boot] State reset. Next startup will run first boot.")


def ensure_initialized(verbose: bool = True) -> Dict:
    """
    Ensure the daemon is initialized, running first boot if needed.
    
    Args:
        verbose: Print progress messages
        
    Returns:
        Initialization status
    """
    initializer = FirstBootInitializer()
    
    if initializer.is_first_boot():
        if verbose:
            print("\n" + "="*60)
            print("  WELCOME TO THE DAEMON - FIRST BOOT INITIALIZATION")
            print("="*60 + "\n")
        return initializer.run_first_boot(verbose=verbose)
    else:
        state = initializer.load_state()
        if verbose:
            print(f"[First Boot] Already initialized on {state.initialized_at}")
        return {
            "success": True,
            "first_boot": False,
            "initialized_at": state.initialized_at
        }


def get_ready_daemon():
    """
    Get a daemon instance that's ready for conversations.
    
    Handles first-boot if needed, then returns the LLM.
    """
    # Ensure initialized
    result = ensure_initialized(verbose=True)
    
    if not result.get("success", True):
        raise RuntimeError(f"Failed to initialize daemon: {result.get('errors')}")
        
    # Return ready LLM
    from unimind.models.native.native_llm import get_native_llm
    return get_native_llm()


# =============================================================================
# WELCOME MESSAGE
# =============================================================================

WELCOME_MESSAGE = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ████████╗██╗  ██╗ ██████╗ ████████╗██╗  ██╗               ║
║   ╚══██╔══╝██║  ██║██╔═══██╗╚══██╔══╝██║  ██║               ║
║      ██║   ███████║██║   ██║   ██║   ███████║               ║
║      ██║   ██╔══██║██║   ██║   ██║   ██╔══██║               ║
║      ██║   ██║  ██║╚██████╔╝   ██║   ██║  ██║               ║
║      ╚═╝   ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝               ║
║                                                              ║
║              Your Personal AI Daemon                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Welcome! I'm your local AI assistant, running entirely on your system.

I can help you with:
  • Answering questions
  • Having conversations
  • Planning tasks
  • Remembering things
  • Learning from you

Try saying:
  • "Hello" - to start a conversation
  • "What can you do?" - to see my capabilities
  • "Help me plan..." - to create a plan
  • "Remember that..." - to store information

Everything runs locally - your data stays private!
"""


def show_welcome():
    """Display welcome message."""
    print(WELCOME_MESSAGE)


# =============================================================================
# QUICK START
# =============================================================================

def quick_start(show_intro: bool = True) -> 'NativeLLM':
    """
    Quick start the daemon for immediate use.
    
    Args:
        show_intro: Show welcome message
        
    Returns:
        Ready NativeLLM instance
    """
    # Run first boot if needed
    ensure_initialized(verbose=True)
    
    # Show welcome
    if show_intro:
        show_welcome()
        
    # Get ready daemon
    from unimind.models.native.native_llm import get_native_llm
    return get_native_llm()


if __name__ == "__main__":
    # Run first boot when executed directly
    daemon = quick_start()
    
    print("\nDaemon is ready! Try chatting:")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\nDaemon: Goodbye! Feel free to come back anytime.")
                break
                
            response = daemon.chat(user_input)
            print(f"\nDaemon: {response}")
            
        except KeyboardInterrupt:
            print("\n\nDaemon: Goodbye!")
            break
