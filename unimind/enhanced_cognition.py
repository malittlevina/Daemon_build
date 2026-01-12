# unimind/enhanced_cognition.py
"""
Enhanced Cognition Pipeline
============================
Extends the base cognition pipeline with:
- Multimodal task classification (text, image, video, 3D, code)
- Vocabulary integration for deeper understanding
- Spelling correction for input normalization
- Capability routing to specialized modules
- Creative generation interfaces

This enables the daemon to determine HOW to complete a task
by understanding what type of output is required and routing
to the appropriate subsystem.
"""

import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto

from unimind.cognition import (
    CognitionPipeline, NLUProcessor, LLMProcessor, LAMProcessor,
    Intent, ThoughtResult, ThoughtType
)


class OutputType(Enum):
    """Type of output the task requires."""
    TEXT = "text"                  # Natural language response
    CODE = "code"                  # Code generation
    IMAGE = "image"                # Image generation
    VIDEO = "video"                # Video generation
    AUDIO = "audio"                # Audio/speech generation
    THREE_D = "3d"                 # 3D model/scene generation
    AR_OVERLAY = "ar_overlay"      # AR visual overlay
    WORLD = "world"                # World/environment generation
    ACTION = "action"              # Physical/device action
    MEMORY = "memory"              # Memory storage/retrieval
    MIXED = "mixed"                # Multiple output types


class Capability(Enum):
    """Available capabilities in the system."""
    # Language
    NLU = "nlu"
    LLM = "llm"
    VOCABULARY = "vocabulary"
    SPELLING = "spelling"
    
    # Generation
    TEXT_GEN = "text_generation"
    CODE_GEN = "code_generation"
    IMAGE_GEN = "image_generation"
    VIDEO_GEN = "video_generation"
    AUDIO_GEN = "audio_generation"
    MODEL_3D_GEN = "3d_generation"
    
    # Perception
    VISION = "vision"
    SPEECH_TO_TEXT = "speech_to_text"
    OCR = "ocr"
    
    # World
    WORLD_ENGINE = "world_engine"
    PHYSICS = "physics"
    AVATAR = "avatar"
    XR = "xr"
    
    # Actions
    DEVICE_CONTROL = "device_control"
    AUTOMATION = "automation"
    
    # Memory
    MEMORY_STORE = "memory_store"
    MEMORY_RECALL = "memory_recall"


@dataclass
class TaskClassification:
    """Classification of what a task requires."""
    primary_output: OutputType
    secondary_outputs: List[OutputType] = field(default_factory=list)
    required_capabilities: List[Capability] = field(default_factory=list)
    complexity: float = 0.5  # 0-1, how complex the task is
    requires_generation: bool = False
    requires_memory: bool = False
    requires_action: bool = False


@dataclass
class CapabilityProvider:
    """A provider of a specific capability."""
    name: str
    capability: Capability
    handler: Optional[Callable] = None
    available: bool = True
    priority: int = 0  # Higher = preferred
    
    
class TaskClassifier:
    """
    Classifies tasks to determine what type of output is needed
    and which capabilities are required.
    """
    
    # Patterns that indicate specific output types
    OUTPUT_PATTERNS = {
        OutputType.IMAGE: [
            'generate image', 'generate an image', 'create image', 'create an image',
            'draw', 'picture of', 'image of', 'show me', 'visualize',
            'render image', 'make an image', 'make image',
            'illustration', 'photo of', 'artwork', 'painting of'
        ],
        OutputType.VIDEO: [
            'generate video', 'create video', 'make a video',
            'animate', 'animation', 'movie', 'clip of'
        ],
        OutputType.AUDIO: [
            'generate audio', 'create sound', 'speak', 'say',
            'play music', 'compose', 'synthesize voice'
        ],
        OutputType.THREE_D: [
            'create 3d', 'generate 3d', '3d model', 'render 3d',
            'build model', 'sculpt', 'mesh', 'three dimensional'
        ],
        OutputType.CODE: [
            'write code', 'generate code', 'create function',
            'implement', 'code for', 'script', 'program',
            'class for', 'method for', 'algorithm'
        ],
        OutputType.WORLD: [
            'create world', 'create a world', 'create new world', 'new world',
            'generate environment', 'build scene', 'generate world',
            'spawn', 'create room', 'generate terrain', 'build world'
        ],
        OutputType.AR_OVERLAY: [
            'show in ar', 'overlay', 'augmented', 'ar display',
            'heads up', 'hud'
        ],
        OutputType.ACTION: [
            'turn on', 'turn off', 'open', 'close', 'start', 'stop',
            'send', 'control', 'move', 'activate', 'deactivate'
        ],
        OutputType.MEMORY: [
            'remember', 'recall', 'what did i', 'when did',
            'save this', 'note that', 'journal', 'diary'
        ],
    }
    
    def classify(self, text: str, intent: Intent = None) -> TaskClassification:
        """Classify a task based on its text and intent."""
        text_lower = text.lower()
        
        # Score each output type
        output_scores = {}
        for output_type, patterns in self.OUTPUT_PATTERNS.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                output_scores[output_type] = score
        
        # Determine primary output
        if output_scores:
            primary_output = max(output_scores, key=output_scores.get)
            secondary_outputs = [
                ot for ot, score in sorted(
                    output_scores.items(), key=lambda x: x[1], reverse=True
                )[1:3] if score > 0
            ]
        else:
            primary_output = OutputType.TEXT
            secondary_outputs = []
        
        # Map output types to required capabilities
        capability_map = {
            OutputType.TEXT: [Capability.NLU, Capability.LLM, Capability.TEXT_GEN],
            OutputType.CODE: [Capability.NLU, Capability.LLM, Capability.CODE_GEN],
            OutputType.IMAGE: [Capability.NLU, Capability.IMAGE_GEN],
            OutputType.VIDEO: [Capability.NLU, Capability.VIDEO_GEN],
            OutputType.AUDIO: [Capability.NLU, Capability.AUDIO_GEN],
            OutputType.THREE_D: [Capability.NLU, Capability.MODEL_3D_GEN, Capability.WORLD_ENGINE],
            OutputType.WORLD: [Capability.NLU, Capability.WORLD_ENGINE, Capability.PHYSICS],
            OutputType.AR_OVERLAY: [Capability.NLU, Capability.XR, Capability.VISION],
            OutputType.ACTION: [Capability.NLU, Capability.DEVICE_CONTROL],
            OutputType.MEMORY: [Capability.NLU, Capability.MEMORY_STORE, Capability.MEMORY_RECALL],
        }
        
        required_caps = capability_map.get(primary_output, [Capability.NLU, Capability.LLM])
        
        return TaskClassification(
            primary_output=primary_output,
            secondary_outputs=secondary_outputs,
            required_capabilities=required_caps,
            complexity=min(1.0, len(output_scores) * 0.2 + 0.3),
            requires_generation=primary_output in [
                OutputType.IMAGE, OutputType.VIDEO, OutputType.THREE_D,
                OutputType.CODE, OutputType.AUDIO
            ],
            requires_memory=primary_output == OutputType.MEMORY or intent == Intent.REMEMBER,
            requires_action=primary_output == OutputType.ACTION or intent == Intent.COMMAND
        )


class CapabilityRouter:
    """
    Routes tasks to the appropriate capability providers.
    Manages available capabilities and their handlers.
    """
    
    def __init__(self):
        self.providers: Dict[Capability, List[CapabilityProvider]] = {}
        self._register_default_providers()
    
    def _register_default_providers(self):
        """Register default capability providers."""
        # Language capabilities (always available via local processing)
        self.register(CapabilityProvider(
            name="NLU", capability=Capability.NLU, available=True, priority=10
        ))
        self.register(CapabilityProvider(
            name="LLM", capability=Capability.LLM, available=True, priority=10
        ))
        self.register(CapabilityProvider(
            name="Vocabulary", capability=Capability.VOCABULARY, available=True, priority=5
        ))
        self.register(CapabilityProvider(
            name="Spelling", capability=Capability.SPELLING, available=True, priority=5
        ))
        
        # Text generation (via LLM)
        self.register(CapabilityProvider(
            name="TextGen", capability=Capability.TEXT_GEN, available=True, priority=10
        ))
        
        # Code generation (via CodeMaster + LLM)
        self.register(CapabilityProvider(
            name="CodeMaster", capability=Capability.CODE_GEN, available=True, priority=8
        ))
        
        # Media generation (stubs - real implementations would connect to models)
        self.register(CapabilityProvider(
            name="ImageGen", capability=Capability.IMAGE_GEN, available=False, priority=5
        ))
        self.register(CapabilityProvider(
            name="VideoGen", capability=Capability.VIDEO_GEN, available=False, priority=5
        ))
        self.register(CapabilityProvider(
            name="AudioGen", capability=Capability.AUDIO_GEN, available=False, priority=5
        ))
        self.register(CapabilityProvider(
            name="3DGen", capability=Capability.MODEL_3D_GEN, available=False, priority=5
        ))
        
        # World/XR capabilities
        self.register(CapabilityProvider(
            name="WorldEngine", capability=Capability.WORLD_ENGINE, available=True, priority=7
        ))
        self.register(CapabilityProvider(
            name="XREngine", capability=Capability.XR, available=True, priority=7
        ))
        self.register(CapabilityProvider(
            name="Avatar", capability=Capability.AVATAR, available=True, priority=5
        ))
        
        # Perception
        self.register(CapabilityProvider(
            name="Vision", capability=Capability.VISION, available=True, priority=5
        ))
        self.register(CapabilityProvider(
            name="Scribe", capability=Capability.SPEECH_TO_TEXT, available=True, priority=5
        ))
        self.register(CapabilityProvider(
            name="Scribe", capability=Capability.OCR, available=True, priority=5
        ))
        
        # Memory
        self.register(CapabilityProvider(
            name="MemoryStore", capability=Capability.MEMORY_STORE, available=True, priority=10
        ))
        self.register(CapabilityProvider(
            name="MemoryRecall", capability=Capability.MEMORY_RECALL, available=True, priority=10
        ))
        
        # Device control
        self.register(CapabilityProvider(
            name="DeviceBridge", capability=Capability.DEVICE_CONTROL, available=True, priority=8
        ))
    
    def register(self, provider: CapabilityProvider):
        """Register a capability provider."""
        if provider.capability not in self.providers:
            self.providers[provider.capability] = []
        self.providers[provider.capability].append(provider)
        # Sort by priority (higher first)
        self.providers[provider.capability].sort(key=lambda p: -p.priority)
    
    def get_provider(self, capability: Capability) -> Optional[CapabilityProvider]:
        """Get the best available provider for a capability."""
        providers = self.providers.get(capability, [])
        for provider in providers:
            if provider.available:
                return provider
        return None
    
    def check_capabilities(self, required: List[Capability]) -> Dict[str, Any]:
        """Check if all required capabilities are available."""
        results = {
            'all_available': True,
            'available': [],
            'missing': [],
            'providers': {}
        }
        
        for cap in required:
            provider = self.get_provider(cap)
            if provider:
                results['available'].append(cap)
                results['providers'][cap.value] = provider.name
            else:
                results['missing'].append(cap)
                results['all_available'] = False
        
        return results
    
    def get_available_capabilities(self) -> List[Capability]:
        """Get list of all available capabilities."""
        available = []
        for cap, providers in self.providers.items():
            if any(p.available for p in providers):
                available.append(cap)
        return available


class EnhancedNLUProcessor(NLUProcessor):
    """
    Enhanced NLU with vocabulary integration and spelling correction.
    """
    
    def __init__(self):
        super().__init__()
        self.vocabulary = None
        self.spelling = None
        self._init_vocabulary()
        self._init_spelling()
    
    def _init_vocabulary(self):
        """Initialize vocabulary system."""
        try:
            from language.vocabulary import Vocabulary
            self.vocabulary = Vocabulary(load_native=True)
        except Exception as e:
            print(f"[EnhancedNLU] Vocabulary not available: {e}")
    
    def _init_spelling(self):
        """Initialize spelling correction."""
        try:
            from nlu.spelling import SpellingCorrector
            self.spelling = SpellingCorrector()
            # Load vocabulary into spelling dictionary
            if self.vocabulary:
                for word in list(self.vocabulary.words.keys())[:5000]:
                    self.spelling.dictionary.add(word)
        except Exception as e:
            print(f"[EnhancedNLU] Spelling not available: {e}")
    
    def preprocess(self, text: str) -> str:
        """Preprocess text with spelling correction."""
        if not self.spelling:
            return text
        
        words = text.split()
        corrected = []
        
        for word in words:
            # Skip short words and proper nouns
            if len(word) <= 2 or word[0].isupper():
                corrected.append(word)
                continue
            
            # Clean word for checking
            clean_word = ''.join(c for c in word.lower() if c.isalnum())
            
            # Check if known word
            if self.vocabulary and self.vocabulary.has_word(clean_word):
                corrected.append(word)
            else:
                # Try spelling correction
                suggestions = self.spelling.suggest(clean_word)
                if suggestions and suggestions[0].confidence > 0.8:
                    corrected.append(suggestions[0].suggestion)
                else:
                    corrected.append(word)
        
        return ' '.join(corrected)
    
    def understand(self, text: str, context: Optional[Dict] = None) -> Tuple[Intent, float, Dict]:
        """Enhanced understanding with vocabulary lookup."""
        # Preprocess
        processed_text = self.preprocess(text)
        
        # Base understanding
        intent, confidence, entities = super().understand(processed_text, context)
        
        # Enrich with vocabulary analysis
        if self.vocabulary:
            vocab_analysis = self.vocabulary.analyze_text(processed_text)
            entities['vocabulary'] = vocab_analysis
            
            # Boost confidence if we understand most words
            if vocab_analysis['vocabulary_coverage'] > 0.8:
                confidence = min(1.0, confidence + 0.1)
        
        return intent, confidence, entities


class GenerationInterface:
    """
    Interface for creative generation capabilities.
    Provides stubs for image, video, audio, and 3D generation.
    Real implementations would connect to actual models.
    """
    
    def __init__(self, router: CapabilityRouter):
        self.router = router
    
    def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate an image from a prompt."""
        provider = self.router.get_provider(Capability.IMAGE_GEN)
        
        if provider and provider.handler:
            return provider.handler(prompt, **kwargs)
        
        # Stub response
        return {
            'status': 'stub',
            'message': 'Image generation not configured. Would generate image for: ' + prompt,
            'suggestion': 'Connect Stable Diffusion, DALL-E, or similar API',
            'prompt': prompt,
            'type': 'image'
        }
    
    def generate_video(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a video from a prompt."""
        provider = self.router.get_provider(Capability.VIDEO_GEN)
        
        if provider and provider.handler:
            return provider.handler(prompt, **kwargs)
        
        return {
            'status': 'stub',
            'message': 'Video generation not configured. Would generate video for: ' + prompt,
            'suggestion': 'Connect Runway, Pika, or similar API',
            'prompt': prompt,
            'type': 'video'
        }
    
    def generate_audio(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate audio from a prompt."""
        provider = self.router.get_provider(Capability.AUDIO_GEN)
        
        if provider and provider.handler:
            return provider.handler(prompt, **kwargs)
        
        return {
            'status': 'stub',
            'message': 'Audio generation not configured. Would generate audio for: ' + prompt,
            'suggestion': 'Connect ElevenLabs, Bark, or similar API',
            'prompt': prompt,
            'type': 'audio'
        }
    
    def generate_3d(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a 3D model from a prompt."""
        provider = self.router.get_provider(Capability.MODEL_3D_GEN)
        
        if provider and provider.handler:
            return provider.handler(prompt, **kwargs)
        
        # Try using world engine for basic 3D
        try:
            from world_engine.generator import generate_from_prompt
            result = generate_from_prompt(prompt)
            return {
                'status': 'partial',
                'message': 'Using world engine for basic 3D generation',
                'result': result,
                'prompt': prompt,
                'type': '3d'
            }
        except:
            pass
        
        return {
            'status': 'stub',
            'message': '3D generation not configured. Would generate 3D model for: ' + prompt,
            'suggestion': 'Connect Point-E, Shap-E, or similar API',
            'prompt': prompt,
            'type': '3d'
        }
    
    def generate_code(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate code from a prompt."""
        provider = self.router.get_provider(Capability.CODE_GEN)
        
        # Try CodeMaster first
        try:
            from code_tools.code_master import CodeMaster
            code_master = CodeMaster()
            
            # Check for pattern scaffolding
            for pattern in ['singleton', 'factory', 'observer']:
                if pattern in prompt.lower():
                    code = code_master.generate_scaffold(pattern)
                    return {
                        'status': 'success',
                        'code': code,
                        'pattern': pattern,
                        'type': 'code'
                    }
            
            # Generic advice
            advice = code_master.get_advice(prompt)
            return {
                'status': 'partial',
                'advice': advice,
                'message': 'For full code generation, use the LLM',
                'type': 'code'
            }
        except Exception as e:
            pass
        
        return {
            'status': 'stub',
            'message': 'Code generation falling back to LLM',
            'prompt': prompt,
            'type': 'code'
        }


@dataclass 
class EnhancedThoughtResult(ThoughtResult):
    """Extended thought result with multimodal support."""
    task_classification: Optional[TaskClassification] = None
    capability_check: Optional[Dict] = None
    generation_result: Optional[Dict] = None
    execution_plan: List[Dict] = field(default_factory=list)


class EnhancedCognitionPipeline(CognitionPipeline):
    """
    Enhanced cognition pipeline with:
    - Task classification (what output is needed)
    - Capability routing (which modules can handle it)
    - Creative generation interfaces
    - Vocabulary-enhanced NLU
    """
    
    def __init__(self, use_llm: bool = True):
        # Use enhanced NLU
        self.nlu = EnhancedNLUProcessor()
        self.llm = LLMProcessor(use_ollama=use_llm)
        self.lam = LAMProcessor()
        self.use_llm = use_llm
        
        # Enhanced components
        self.classifier = TaskClassifier()
        self.router = CapabilityRouter()
        self.generator = GenerationInterface(self.router)
        
        # Emotion words (inherited)
        self.emotion_words = {
            'positive': ['happy', 'great', 'wonderful', 'excited', 'love', 'amazing', 'good', 'thanks'],
            'negative': ['sad', 'angry', 'frustrated', 'worried', 'bad', 'terrible', 'hate', 'annoyed'],
            'curious': ['wonder', 'curious', 'interesting', 'how', 'why', 'what if'],
            'neutral': []
        }
        
        # Register generation actions with LAM
        self._register_generation_actions()
    
    def _register_generation_actions(self):
        """Register generation handlers with LAM."""
        # Generation actions
        self.lam.register_action('generate_image', self.generator.generate_image)
        self.lam.register_action('generate_video', self.generator.generate_video)
        self.lam.register_action('generate_audio', self.generator.generate_audio)
        self.lam.register_action('generate_3d', self.generator.generate_3d)
        self.lam.register_action('generate_code', self.generator.generate_code)
        
        # XR actions
        self.lam.register_action('start_ar_session', self._start_ar_session)
        self.lam.register_action('show_ar_overlay', self._show_ar_overlay)
        self.lam.register_action('create_spatial_anchor', self._create_spatial_anchor)
        
        # World actions
        self.lam.register_action('create_world', self._create_world)
        self.lam.register_action('spawn_entity', self._spawn_entity)
        self.lam.register_action('step_world', self._step_world)
        
        # Avatar actions
        self.lam.register_action('set_avatar_emotion', self._set_avatar_emotion)
        self.lam.register_action('set_avatar_pose', self._set_avatar_pose)
        
        # Device-specific actions
        self.lam.register_action('control_smart_ring', self._control_smart_ring)
        self.lam.register_action('control_smart_glasses', self._control_smart_glasses)
        self.lam.register_action('control_companion_robot', self._control_companion_robot)
        self.lam.register_action('control_drone', self._control_drone)
        
        # Self-evolution actions
        self.lam.register_action('analyze_codebase', self._analyze_codebase)
        self.lam.register_action('propose_improvement', self._propose_improvement)
        self.lam.register_action('apply_improvement', self._apply_improvement)
        self.lam.register_action('create_module', self._create_module)
        self.lam.register_action('get_evolution_status', self._get_evolution_status)
    
    # XR Actions
    def _start_ar_session(self, mode: str = "ar", **kwargs) -> Dict[str, Any]:
        """Start an AR/VR/MR session."""
        try:
            from xr.xr_engine import XREngine, XRMode, XRDeviceType
            
            engine = XREngine()
            mode_enum = XRMode.AR if mode == "ar" else XRMode.MR if mode == "mr" else XRMode.VR
            session = engine.start_session(mode_enum, XRDeviceType.SIMULATED)
            
            return {
                'status': 'success',
                'session_id': session.session_id,
                'mode': mode,
                'message': f'Started {mode.upper()} session'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _show_ar_overlay(self, content: str, position: str = "center", **kwargs) -> Dict[str, Any]:
        """Show AR overlay content."""
        try:
            from xr.ar_overlay import AROverlay, OverlayType, Position
            
            overlay = AROverlay()
            pos = Position[position.upper()] if hasattr(Position, position.upper()) else None
            result = overlay.show(content, position=pos)
            
            return {
                'status': 'success',
                'overlay_id': result.get('id'),
                'message': f'Showing overlay: {content[:50]}...'
            }
        except Exception as e:
            return {'status': 'stub', 'message': f'AR overlay: {content}', 'error': str(e)}
    
    def _create_spatial_anchor(self, name: str, location: Dict = None, **kwargs) -> Dict[str, Any]:
        """Create a spatial anchor for AR persistence."""
        try:
            from xr.spatial_anchor import SpatialAnchor, AnchorType
            
            anchor = SpatialAnchor(name=name, location=location or {})
            anchor.save()
            
            return {
                'status': 'success',
                'anchor_id': anchor.id,
                'name': name,
                'message': f'Created spatial anchor: {name}'
            }
        except Exception as e:
            return {'status': 'stub', 'message': f'Spatial anchor: {name}', 'error': str(e)}
    
    # World Engine Actions
    def _create_world(self, name: str = "new_world", **kwargs) -> Dict[str, Any]:
        """Create a new world/environment."""
        try:
            from world_engine.core import WorldEngine
            
            engine = WorldEngine(enable_server=False)
            engine.create_new_world()
            
            return {
                'status': 'success',
                'world_name': name,
                'entities': len(engine.state.entities),
                'message': f'Created world "{name}" with {len(engine.state.entities)} entities'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _spawn_entity(self, entity_type: str, name: str = None, position: Dict = None, **kwargs) -> Dict[str, Any]:
        """Spawn an entity in the world."""
        try:
            from world_engine.core import WorldEngine
            from world_engine.state import Entity
            
            engine = WorldEngine(enable_server=False)
            
            entity = Entity(
                entity_id=f"{entity_type}_{len(engine.state.entities)}",
                entity_type=entity_type,
                name=name or entity_type,
                position=position or {"x": 0, "y": 0, "z": 0}
            )
            engine.state.entities[entity.entity_id] = entity
            engine.save_world()
            
            return {
                'status': 'success',
                'entity_id': entity.entity_id,
                'type': entity_type,
                'message': f'Spawned {entity_type}: {entity.entity_id}'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _step_world(self, steps: int = 1, **kwargs) -> Dict[str, Any]:
        """Advance the world simulation."""
        try:
            from world_engine.core import WorldEngine
            
            engine = WorldEngine(enable_server=False)
            logs = []
            for _ in range(steps):
                step_logs = engine.step()
                logs.extend(step_logs)
            
            return {
                'status': 'success',
                'steps': steps,
                'logs': logs[:10],  # Limit logs returned
                'message': f'Advanced world by {steps} steps'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # Avatar Actions
    def _set_avatar_emotion(self, emotion: str, **kwargs) -> Dict[str, Any]:
        """Set the avatar's emotional expression."""
        try:
            from avatar.avatar_engine import AvatarEngine
            
            avatar = AvatarEngine()
            avatar.set_emotion(emotion)
            state = avatar.get_current_visual_state()
            
            return {
                'status': 'success',
                'emotion': emotion,
                'expression': state['expression'],
                'message': f'Avatar emotion set to {emotion}'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _set_avatar_pose(self, pose: str, **kwargs) -> Dict[str, Any]:
        """Set the avatar's pose/action."""
        try:
            from avatar.avatar_engine import AvatarEngine
            
            avatar = AvatarEngine()
            avatar.set_pose(pose)
            state = avatar.get_current_visual_state()
            
            return {
                'status': 'success',
                'pose': pose,
                'state': state,
                'message': f'Avatar pose set to {pose}'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # Device-specific Actions
    def _control_smart_ring(self, action: str, **kwargs) -> Dict[str, Any]:
        """Control smart ring device."""
        try:
            from devices.wearables.smart_ring import SmartRing
            
            ring = SmartRing("daemon_ring")
            
            if action == "get_biometrics":
                data = ring.get_biometrics()
                return {'status': 'success', 'biometrics': data}
            elif action == "haptic_feedback":
                pattern = kwargs.get('pattern', 'pulse')
                ring.haptic_feedback(pattern)
                return {'status': 'success', 'message': f'Haptic {pattern} sent'}
            elif action == "get_gestures":
                gestures = ring.get_recent_gestures()
                return {'status': 'success', 'gestures': gestures}
            else:
                return {'status': 'error', 'message': f'Unknown action: {action}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _control_smart_glasses(self, action: str, **kwargs) -> Dict[str, Any]:
        """Control smart glasses device."""
        try:
            from devices.wearables.smart_glasses import SmartGlasses
            
            glasses = SmartGlasses("daemon_glasses")
            
            if action == "show_notification":
                text = kwargs.get('text', 'Notification')
                glasses.show_notification(text)
                return {'status': 'success', 'message': f'Showing: {text}'}
            elif action == "capture_photo":
                photo = glasses.capture_photo()
                return {'status': 'success', 'photo': photo}
            elif action == "start_recording":
                glasses.start_recording()
                return {'status': 'success', 'message': 'Recording started'}
            elif action == "show_ar_overlay":
                content = kwargs.get('content', '')
                glasses.show_ar_overlay(content)
                return {'status': 'success', 'message': 'AR overlay shown'}
            else:
                return {'status': 'error', 'message': f'Unknown action: {action}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _control_companion_robot(self, action: str, **kwargs) -> Dict[str, Any]:
        """Control companion robot."""
        try:
            from devices.wearables.companion_robot import CompanionRobot
            
            robot = CompanionRobot("daemon_robot")
            
            if action == "move":
                direction = kwargs.get('direction', 'forward')
                distance = kwargs.get('distance', 1.0)
                robot.move(direction, distance)
                return {'status': 'success', 'message': f'Moving {direction} {distance}m'}
            elif action == "speak":
                text = kwargs.get('text', 'Hello')
                robot.speak(text)
                return {'status': 'success', 'message': f'Speaking: {text}'}
            elif action == "express_emotion":
                emotion = kwargs.get('emotion', 'happy')
                robot.express_emotion(emotion)
                return {'status': 'success', 'message': f'Expressing: {emotion}'}
            elif action == "get_perception":
                perception = robot.get_perception()
                return {'status': 'success', 'perception': perception}
            else:
                return {'status': 'error', 'message': f'Unknown action: {action}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _control_drone(self, action: str, **kwargs) -> Dict[str, Any]:
        """Control drone device."""
        try:
            from devices.wearables.drone import Drone
            
            drone = Drone("daemon_drone")
            
            if action == "takeoff":
                drone.takeoff()
                return {'status': 'success', 'message': 'Drone taking off'}
            elif action == "land":
                drone.land()
                return {'status': 'success', 'message': 'Drone landing'}
            elif action == "fly_to":
                x = kwargs.get('x', 0)
                y = kwargs.get('y', 0)
                z = kwargs.get('z', 10)
                drone.fly_to(x, y, z)
                return {'status': 'success', 'message': f'Flying to ({x}, {y}, {z})'}
            elif action == "capture_aerial":
                photo = drone.capture_aerial_photo()
                return {'status': 'success', 'photo': photo}
            elif action == "follow_me":
                drone.start_follow_mode()
                return {'status': 'success', 'message': 'Follow mode activated'}
            else:
                return {'status': 'error', 'message': f'Unknown action: {action}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # Self-Evolution Actions
    def _analyze_codebase(self, module: str = None, **kwargs) -> Dict[str, Any]:
        """Analyze the daemon's codebase for improvements."""
        try:
            from codegen.self_evolution import get_evolution_engine
            
            engine = get_evolution_engine()
            
            if module:
                analyses = engine.introspector.analyze_module(module)
                return {
                    'status': 'success',
                    'module': module,
                    'files_analyzed': len(analyses),
                    'total_lines': sum(a.lines_of_code for a in analyses),
                    'issues': sum(len(a.issues) for a in analyses),
                    'suggestions': sum(len(a.suggestions) for a in analyses)
                }
            else:
                analysis = engine.analyze_self()
                return {
                    'status': 'success',
                    'analysis': analysis
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _propose_improvement(
        self,
        file_path: str,
        description: str,
        change_type: str = "enhancement",
        **kwargs
    ) -> Dict[str, Any]:
        """Propose a code improvement."""
        try:
            from codegen.self_evolution import get_evolution_engine, ChangeType
            
            engine = get_evolution_engine()
            ct = ChangeType(change_type) if change_type in [t.value for t in ChangeType] else ChangeType.ENHANCEMENT
            
            change = engine.propose_improvement(file_path, ct, description)
            
            if change:
                return {
                    'status': 'success',
                    'change_id': change.change_id,
                    'risk_level': change.risk_level.value,
                    'approved': change.approved,
                    'message': f'Proposed improvement to {file_path}'
                }
            return {'status': 'error', 'message': 'Could not generate improvement'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _apply_improvement(self, change_id: str, force: bool = False, **kwargs) -> Dict[str, Any]:
        """Apply a proposed code improvement."""
        try:
            from codegen.self_evolution import get_evolution_engine
            
            engine = get_evolution_engine()
            
            for change in engine.pending_changes:
                if change.change_id == change_id:
                    success = engine.apply_change(change, force=force)
                    if success:
                        return {
                            'status': 'success',
                            'message': f'Applied change {change_id}'
                        }
                    return {
                        'status': 'error',
                        'message': f'Failed to apply change {change_id}'
                    }
            
            return {'status': 'error', 'message': f'Change {change_id} not found'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _create_module(
        self,
        module_name: str,
        purpose: str,
        language: str = "python",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new module."""
        try:
            from codegen.self_evolution import get_evolution_engine, Language
            
            engine = get_evolution_engine()
            lang = Language(language) if language in [l.value for l in Language] else Language.PYTHON
            
            path = engine.create_new_module(module_name, purpose, lang)
            
            return {
                'status': 'success',
                'path': path,
                'message': f'Created module {module_name}'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _get_evolution_status(self, **kwargs) -> Dict[str, Any]:
        """Get self-evolution status."""
        try:
            from codegen.self_evolution import get_evolution_engine
            
            engine = get_evolution_engine()
            return {
                'status': 'success',
                **engine.get_status()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def process(self, input_text: str, context: Optional[Dict] = None) -> EnhancedThoughtResult:
        """Process input through the enhanced cognition pipeline."""
        start_time = time.time()
        
        result = EnhancedThoughtResult(input_text=input_text)
        
        # Step 1: Enhanced NLU - Understand with vocabulary
        intent, confidence, entities = self.nlu.understand(input_text, context)
        result.intent = intent
        result.confidence = confidence
        result.entities = entities
        
        # Step 2: Classify the task
        classification = self.classifier.classify(input_text, intent)
        result.task_classification = classification
        
        # Step 3: Check capabilities
        cap_check = self.router.check_capabilities(classification.required_capabilities)
        result.capability_check = cap_check
        
        # Detect emotion
        result.emotion = self._detect_emotion(input_text)
        
        # Step 4: Build execution plan based on classification
        execution_plan = self._build_execution_plan(
            input_text, intent, classification, cap_check
        )
        result.execution_plan = execution_plan
        
        # Step 5: Execute plan
        if classification.requires_generation:
            gen_result = self._execute_generation(input_text, classification)
            result.generation_result = gen_result
            
            # Build response around generation
            if gen_result.get('status') == 'success':
                result.response = f"Generated {classification.primary_output.value}: {gen_result.get('message', 'Done')}"
            elif gen_result.get('status') == 'stub':
                # Fall back to LLM for description
                result.response = self.llm.reason(input_text, intent, context)
                result.response += f"\n\n[Note: {classification.primary_output.value} generation not yet configured]"
            else:
                result.response = self.llm.reason(input_text, intent, context)
        else:
            # Standard LLM response
            result.response = self.llm.reason(input_text, intent, context)
        
        # Step 6: Plan actions
        actions = self.lam.plan(intent, entities, context)
        result.actions = actions
        
        # Execute if needed
        if actions:
            action_results = self.lam.execute(actions)
            result.actions = action_results
        
        # Calculate processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _build_execution_plan(
        self,
        text: str,
        intent: Intent,
        classification: TaskClassification,
        cap_check: Dict
    ) -> List[Dict]:
        """Build a step-by-step execution plan."""
        plan = []
        
        # Step 1: Always understand
        plan.append({
            'step': 1,
            'action': 'understand',
            'capability': Capability.NLU.value,
            'status': 'complete'
        })
        
        # Step 2: Classify
        plan.append({
            'step': 2,
            'action': 'classify',
            'output_type': classification.primary_output.value,
            'status': 'complete'
        })
        
        # Step 3: Check capabilities
        if cap_check['all_available']:
            plan.append({
                'step': 3,
                'action': 'check_capabilities',
                'status': 'ready',
                'providers': cap_check['providers']
            })
        else:
            plan.append({
                'step': 3,
                'action': 'check_capabilities',
                'status': 'partial',
                'missing': [c.value for c in cap_check['missing']]
            })
        
        # Step 4: Generate or respond
        if classification.requires_generation:
            plan.append({
                'step': 4,
                'action': f'generate_{classification.primary_output.value}',
                'status': 'pending'
            })
        else:
            plan.append({
                'step': 4,
                'action': 'reason_and_respond',
                'status': 'pending'
            })
        
        # Step 5: Execute actions
        if classification.requires_action:
            plan.append({
                'step': 5,
                'action': 'execute_device_action',
                'status': 'pending'
            })
        
        # Step 6: Store to memory
        if classification.requires_memory:
            plan.append({
                'step': 6,
                'action': 'store_to_memory',
                'status': 'pending'
            })
        
        return plan
    
    def _execute_generation(
        self,
        prompt: str,
        classification: TaskClassification
    ) -> Dict[str, Any]:
        """Execute the appropriate generation based on classification."""
        output_type = classification.primary_output
        
        if output_type == OutputType.IMAGE:
            return self.generator.generate_image(prompt)
        elif output_type == OutputType.VIDEO:
            return self.generator.generate_video(prompt)
        elif output_type == OutputType.AUDIO:
            return self.generator.generate_audio(prompt)
        elif output_type == OutputType.THREE_D:
            return self.generator.generate_3d(prompt)
        elif output_type == OutputType.CODE:
            return self.generator.generate_code(prompt)
        else:
            return {'status': 'skip', 'message': 'No generation needed'}
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of available capabilities."""
        available = self.router.get_available_capabilities()
        
        return {
            'total_capabilities': len(Capability),
            'available_count': len(available),
            'available': [c.value for c in available],
            'generation_ready': {
                'image': Capability.IMAGE_GEN in available,
                'video': Capability.VIDEO_GEN in available,
                'audio': Capability.AUDIO_GEN in available,
                '3d': Capability.MODEL_3D_GEN in available,
                'code': Capability.CODE_GEN in available,
            },
            'vocabulary_loaded': self.nlu.vocabulary is not None,
            'spelling_available': self.nlu.spelling is not None,
        }


# Factory function
def create_enhanced_cognition(use_llm: bool = True) -> EnhancedCognitionPipeline:
    """Create an enhanced cognition pipeline."""
    return EnhancedCognitionPipeline(use_llm=use_llm)


# Global instance
_enhanced_cognition: Optional[EnhancedCognitionPipeline] = None


def get_enhanced_cognition() -> EnhancedCognitionPipeline:
    """Get or create the global enhanced cognition pipeline."""
    global _enhanced_cognition
    if _enhanced_cognition is None:
        _enhanced_cognition = create_enhanced_cognition()
    return _enhanced_cognition
