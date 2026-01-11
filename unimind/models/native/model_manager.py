# unimind/models/native/model_manager.py
# Native Model Manager - Local model downloading, storage, and management

import os
import json
import hashlib
import shutil
import subprocess
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import urllib.request
import urllib.error


class ModelFormat(Enum):
    """Supported model formats."""
    GGUF = "gguf"           # llama.cpp format
    GGML = "ggml"           # Legacy llama.cpp
    SAFETENSORS = "safetensors"  # HuggingFace safe format
    PYTORCH = "pytorch"      # PyTorch .bin/.pt
    ONNX = "onnx"           # ONNX format
    NATIVE = "native"        # Our native format


class ModelType(Enum):
    """Types of models."""
    LLM = "llm"                      # Large Language Model
    EMBEDDING = "embedding"          # Text embeddings
    CLASSIFIER = "classifier"        # Classification
    NER = "ner"                      # Named Entity Recognition
    SENTIMENT = "sentiment"          # Sentiment analysis
    SUMMARIZER = "summarizer"        # Summarization
    TRANSLATOR = "translator"        # Translation
    CUSTOM = "custom"                # Custom model


class QuantizationType(Enum):
    """Quantization levels for models."""
    NONE = "none"           # Full precision (FP32)
    FP16 = "fp16"           # Half precision
    INT8 = "int8"           # 8-bit quantization
    INT4 = "int4"           # 4-bit quantization
    Q4_0 = "q4_0"           # GGML Q4_0
    Q4_1 = "q4_1"           # GGML Q4_1
    Q5_0 = "q5_0"           # GGML Q5_0
    Q5_1 = "q5_1"           # GGML Q5_1
    Q8_0 = "q8_0"           # GGML Q8_0


@dataclass
class ModelMetadata:
    """Metadata for a managed model."""
    model_id: str
    name: str
    model_type: ModelType
    format: ModelFormat
    quantization: QuantizationType
    size_bytes: int = 0
    parameters: str = ""  # e.g., "7B", "13B"
    context_length: int = 2048
    vocab_size: int = 32000
    description: str = ""
    source_url: Optional[str] = None
    local_path: Optional[str] = None
    checksum: Optional[str] = None
    downloaded_at: Optional[str] = None
    last_used: Optional[str] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "model_type": self.model_type.value,
            "format": self.format.value,
            "quantization": self.quantization.value,
            "size_bytes": self.size_bytes,
            "parameters": self.parameters,
            "context_length": self.context_length,
            "vocab_size": self.vocab_size,
            "description": self.description,
            "source_url": self.source_url,
            "local_path": self.local_path,
            "checksum": self.checksum,
            "downloaded_at": self.downloaded_at,
            "last_used": self.last_used,
            "custom_config": self.custom_config
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelMetadata':
        return cls(
            model_id=data["model_id"],
            name=data["name"],
            model_type=ModelType(data["model_type"]),
            format=ModelFormat(data["format"]),
            quantization=QuantizationType(data.get("quantization", "none")),
            size_bytes=data.get("size_bytes", 0),
            parameters=data.get("parameters", ""),
            context_length=data.get("context_length", 2048),
            vocab_size=data.get("vocab_size", 32000),
            description=data.get("description", ""),
            source_url=data.get("source_url"),
            local_path=data.get("local_path"),
            checksum=data.get("checksum"),
            downloaded_at=data.get("downloaded_at"),
            last_used=data.get("last_used"),
            custom_config=data.get("custom_config", {})
        )


# Pre-defined model configurations for easy downloading
KNOWN_MODELS = {
    # TinyLlama - Very small, good for testing
    "tinyllama-1b": ModelMetadata(
        model_id="tinyllama-1b",
        name="TinyLlama 1.1B",
        model_type=ModelType.LLM,
        format=ModelFormat.GGUF,
        quantization=QuantizationType.Q4_0,
        parameters="1.1B",
        context_length=2048,
        vocab_size=32000,
        description="Compact 1.1B parameter model, good for local testing"
    ),
    
    # Phi-2 - Microsoft's small but capable model
    "phi-2": ModelMetadata(
        model_id="phi-2",
        name="Phi-2",
        model_type=ModelType.LLM,
        format=ModelFormat.GGUF,
        quantization=QuantizationType.Q4_0,
        parameters="2.7B",
        context_length=2048,
        vocab_size=51200,
        description="Microsoft's efficient 2.7B reasoning model"
    ),
    
    # Mistral 7B - Excellent quality/size ratio
    "mistral-7b": ModelMetadata(
        model_id="mistral-7b",
        name="Mistral 7B Instruct",
        model_type=ModelType.LLM,
        format=ModelFormat.GGUF,
        quantization=QuantizationType.Q4_0,
        parameters="7B",
        context_length=8192,
        vocab_size=32000,
        description="High-quality 7B instruction-tuned model"
    ),
    
    # Embedding models
    "all-minilm": ModelMetadata(
        model_id="all-minilm",
        name="all-MiniLM-L6-v2",
        model_type=ModelType.EMBEDDING,
        format=ModelFormat.NATIVE,
        quantization=QuantizationType.NONE,
        parameters="22M",
        context_length=512,
        vocab_size=30522,
        description="Compact sentence embedding model"
    ),
    
    # Sentiment model
    "sentiment-roberta": ModelMetadata(
        model_id="sentiment-roberta",
        name="RoBERTa Sentiment",
        model_type=ModelType.SENTIMENT,
        format=ModelFormat.NATIVE,
        quantization=QuantizationType.NONE,
        parameters="125M",
        context_length=512,
        vocab_size=50265,
        description="Sentiment analysis model"
    ),
}


class DownloadProgress:
    """Track download progress."""
    
    def __init__(self, callback: Callable = None):
        self.total_size = 0
        self.downloaded = 0
        self.callback = callback
        
    def update(self, block_num: int, block_size: int, total_size: int):
        self.total_size = total_size
        self.downloaded = block_num * block_size
        
        if self.callback:
            progress = (self.downloaded / total_size * 100) if total_size > 0 else 0
            self.callback(self.downloaded, total_size, progress)


class NativeModelManager:
    """
    Manages local AI models for the daemon.
    
    Features:
    - Model downloading from various sources
    - Local storage and organization
    - Model verification (checksums)
    - Quantization management
    - Model metadata tracking
    - Ollama integration
    """
    
    DEFAULT_MODEL_DIR = os.path.expanduser("~/.thoth/models")
    
    def __init__(self, model_dir: str = None):
        self.model_dir = model_dir or self.DEFAULT_MODEL_DIR
        self.models_path = Path(self.model_dir)
        self.registry_path = self.models_path / "registry.json"
        self.registry: Dict[str, ModelMetadata] = {}
        
        # Create directories
        self.models_path.mkdir(parents=True, exist_ok=True)
        (self.models_path / "llm").mkdir(exist_ok=True)
        (self.models_path / "embedding").mkdir(exist_ok=True)
        (self.models_path / "classifier").mkdir(exist_ok=True)
        (self.models_path / "cache").mkdir(exist_ok=True)
        
        # Load existing registry
        self._load_registry()
        
        print(f"[NativeModelManager] Initialized at {self.model_dir}")
        
    def _load_registry(self):
        """Load model registry from disk."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    data = json.load(f)
                    for model_id, model_data in data.items():
                        self.registry[model_id] = ModelMetadata.from_dict(model_data)
            except Exception as e:
                print(f"[NativeModelManager] Error loading registry: {e}")
                
    def _save_registry(self):
        """Save model registry to disk."""
        data = {mid: m.to_dict() for mid, m in self.registry.items()}
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)
            
    def list_available_models(self) -> List[Dict]:
        """List all known models available for download."""
        return [
            {
                "model_id": m.model_id,
                "name": m.name,
                "type": m.model_type.value,
                "parameters": m.parameters,
                "description": m.description,
                "installed": m.model_id in self.registry
            }
            for m in KNOWN_MODELS.values()
        ]
        
    def list_installed_models(self) -> List[Dict]:
        """List all installed models."""
        return [
            {
                **m.to_dict(),
                "size_mb": m.size_bytes / (1024 * 1024) if m.size_bytes else 0
            }
            for m in self.registry.values()
        ]
        
    def get_model(self, model_id: str) -> Optional[ModelMetadata]:
        """Get model metadata by ID."""
        return self.registry.get(model_id)
        
    def is_installed(self, model_id: str) -> bool:
        """Check if a model is installed."""
        model = self.registry.get(model_id)
        if model and model.local_path:
            return Path(model.local_path).exists()
        return False
        
    def download_model(
        self,
        model_id: str,
        source_url: str = None,
        progress_callback: Callable = None
    ) -> bool:
        """
        Download a model to local storage.
        
        Args:
            model_id: Model identifier
            source_url: Override URL for download
            progress_callback: Function(downloaded, total, percent)
            
        Returns:
            True if successful
        """
        # Get model info
        if model_id in KNOWN_MODELS:
            metadata = KNOWN_MODELS[model_id]
        elif model_id in self.registry:
            metadata = self.registry[model_id]
        else:
            print(f"[NativeModelManager] Unknown model: {model_id}")
            return False
            
        url = source_url or metadata.source_url
        
        # If no URL, try to use Ollama
        if not url:
            return self._download_via_ollama(model_id, metadata)
            
        # Determine local path
        type_dir = self.models_path / metadata.model_type.value
        local_path = type_dir / f"{model_id}.{metadata.format.value}"
        
        print(f"[NativeModelManager] Downloading {metadata.name}...")
        
        try:
            progress = DownloadProgress(progress_callback)
            urllib.request.urlretrieve(
                url,
                local_path,
                reporthook=progress.update
            )
            
            # Update metadata
            metadata.local_path = str(local_path)
            metadata.size_bytes = local_path.stat().st_size
            metadata.downloaded_at = datetime.now().isoformat()
            metadata.checksum = self._calculate_checksum(local_path)
            
            # Save to registry
            self.registry[model_id] = metadata
            self._save_registry()
            
            print(f"[NativeModelManager] Downloaded {metadata.name} ({metadata.size_bytes / 1024 / 1024:.1f} MB)")
            return True
            
        except Exception as e:
            print(f"[NativeModelManager] Download failed: {e}")
            return False
            
    def _download_via_ollama(self, model_id: str, metadata: ModelMetadata) -> bool:
        """Download model using Ollama."""
        # Map our model IDs to Ollama model names
        ollama_names = {
            "tinyllama-1b": "tinyllama",
            "phi-2": "phi",
            "mistral-7b": "mistral",
        }
        
        ollama_name = ollama_names.get(model_id)
        if not ollama_name:
            print(f"[NativeModelManager] No Ollama mapping for {model_id}")
            return False
            
        print(f"[NativeModelManager] Pulling {ollama_name} via Ollama...")
        
        try:
            result = subprocess.run(
                ["ollama", "pull", ollama_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                # Update metadata
                metadata.local_path = f"ollama:{ollama_name}"
                metadata.downloaded_at = datetime.now().isoformat()
                
                self.registry[model_id] = metadata
                self._save_registry()
                
                print(f"[NativeModelManager] Successfully pulled {ollama_name}")
                return True
            else:
                print(f"[NativeModelManager] Ollama pull failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[NativeModelManager] Ollama pull timed out")
            return False
        except FileNotFoundError:
            print("[NativeModelManager] Ollama not installed")
            return False
            
    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    def verify_model(self, model_id: str) -> bool:
        """Verify model integrity using checksum."""
        model = self.registry.get(model_id)
        if not model or not model.local_path or not model.checksum:
            return False
            
        if model.local_path.startswith("ollama:"):
            return True  # Ollama handles its own verification
            
        path = Path(model.local_path)
        if not path.exists():
            return False
            
        current_checksum = self._calculate_checksum(path)
        return current_checksum == model.checksum
        
    def remove_model(self, model_id: str) -> bool:
        """Remove a model from local storage."""
        model = self.registry.get(model_id)
        if not model:
            return False
            
        # Remove file
        if model.local_path and not model.local_path.startswith("ollama:"):
            path = Path(model.local_path)
            if path.exists():
                path.unlink()
                
        # Remove from Ollama if applicable
        if model.local_path and model.local_path.startswith("ollama:"):
            ollama_name = model.local_path.split(":")[1]
            try:
                subprocess.run(["ollama", "rm", ollama_name], capture_output=True)
            except:
                pass
                
        # Remove from registry
        del self.registry[model_id]
        self._save_registry()
        
        print(f"[NativeModelManager] Removed {model_id}")
        return True
        
    def register_custom_model(
        self,
        model_id: str,
        name: str,
        model_type: ModelType,
        local_path: str,
        format: ModelFormat = ModelFormat.NATIVE,
        quantization: QuantizationType = QuantizationType.NONE,
        **kwargs
    ) -> ModelMetadata:
        """Register a custom/external model."""
        path = Path(local_path)
        
        metadata = ModelMetadata(
            model_id=model_id,
            name=name,
            model_type=model_type,
            format=format,
            quantization=quantization,
            local_path=str(path),
            size_bytes=path.stat().st_size if path.exists() else 0,
            downloaded_at=datetime.now().isoformat(),
            **kwargs
        )
        
        if path.exists():
            metadata.checksum = self._calculate_checksum(path)
            
        self.registry[model_id] = metadata
        self._save_registry()
        
        print(f"[NativeModelManager] Registered custom model: {name}")
        return metadata
        
    def get_model_path(self, model_id: str) -> Optional[str]:
        """Get the local path for a model."""
        model = self.registry.get(model_id)
        return model.local_path if model else None
        
    def update_last_used(self, model_id: str):
        """Update the last used timestamp for a model."""
        if model_id in self.registry:
            self.registry[model_id].last_used = datetime.now().isoformat()
            self._save_registry()
            
    def get_recommended_model(
        self,
        model_type: ModelType = ModelType.LLM,
        max_size_gb: float = 8.0
    ) -> Optional[str]:
        """Get recommended model based on constraints."""
        max_bytes = max_size_gb * 1024 * 1024 * 1024
        
        # First check installed models
        for model_id, model in self.registry.items():
            if model.model_type == model_type:
                if model.size_bytes <= max_bytes or model.size_bytes == 0:
                    return model_id
                    
        # Then suggest from known models
        for model_id, model in KNOWN_MODELS.items():
            if model.model_type == model_type:
                return model_id
                
        return None
        
    def get_storage_info(self) -> Dict:
        """Get storage usage information."""
        total_size = 0
        model_sizes = {}
        
        for model_id, model in self.registry.items():
            if model.local_path and not model.local_path.startswith("ollama:"):
                path = Path(model.local_path)
                if path.exists():
                    size = path.stat().st_size
                    total_size += size
                    model_sizes[model_id] = size
                    
        return {
            "model_directory": str(self.models_path),
            "total_models": len(self.registry),
            "total_size_bytes": total_size,
            "total_size_gb": total_size / (1024 ** 3),
            "model_sizes": {k: v / (1024 ** 2) for k, v in model_sizes.items()}  # MB
        }
        
    def check_ollama_available(self) -> bool:
        """Check if Ollama is installed and running."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
            
    def list_ollama_models(self) -> List[str]:
        """List models available in Ollama."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                return [line.split()[0] for line in lines if line.strip()]
        except:
            pass
        return []
        
    def get_status(self) -> Dict:
        """Get manager status."""
        return {
            "model_directory": str(self.models_path),
            "installed_models": len(self.registry),
            "available_models": len(KNOWN_MODELS),
            "ollama_available": self.check_ollama_available(),
            "storage": self.get_storage_info()
        }


# Singleton instance
_model_manager: Optional[NativeModelManager] = None


def get_model_manager() -> NativeModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = NativeModelManager()
    return _model_manager
