# unimind/modules/emotion_module.py
"""
Emotion Module - Affective reasoning and emotional intelligence

Provides emotional awareness and processing:
- Sentiment analysis
- Emotional state modeling
- Empathetic response generation
- Emotion-aware decision making
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class EmotionType(Enum):
    """Core emotion types based on Plutchik's wheel."""
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"
    # Secondary emotions
    LOVE = "love"          # joy + trust
    SUBMISSION = "submission"  # trust + fear
    AWE = "awe"            # fear + surprise
    DISAPPROVAL = "disapproval"  # surprise + sadness
    REMORSE = "remorse"    # sadness + disgust
    CONTEMPT = "contempt"  # disgust + anger
    AGGRESSIVENESS = "aggressiveness"  # anger + anticipation
    OPTIMISM = "optimism"  # anticipation + joy


@dataclass
class EmotionalState:
    """Current emotional state of the system."""
    primary_emotion: EmotionType = EmotionType.ANTICIPATION
    intensity: float = 0.5  # 0.0 to 1.0
    valence: float = 0.0   # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.5   # 0.0 (calm) to 1.0 (excited)
    secondary_emotions: Dict[EmotionType, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EmotionalMarker:
    """Detected emotional content in input."""
    emotion: EmotionType
    trigger: str
    intensity: float
    context: str


class EmotionModule:
    """
    Emotion cognitive module for Unimind.
    
    Capabilities:
    - Sentiment analysis
    - Emotional state tracking
    - Empathetic reasoning
    - Emotion-influenced decision support
    """
    
    name = "emotion_module"
    
    # Emotion lexicons
    EMOTION_LEXICON = {
        EmotionType.JOY: [
            "happy", "joy", "delighted", "pleased", "glad", "cheerful",
            "excited", "wonderful", "great", "amazing", "love", "enjoy"
        ],
        EmotionType.SADNESS: [
            "sad", "unhappy", "depressed", "down", "miserable", "grief",
            "sorrow", "disappointed", "heartbroken", "lonely", "hurt"
        ],
        EmotionType.ANGER: [
            "angry", "mad", "furious", "annoyed", "irritated", "frustrated",
            "rage", "hate", "hostile", "resentful", "outraged"
        ],
        EmotionType.FEAR: [
            "afraid", "scared", "fearful", "terrified", "anxious", "worried",
            "nervous", "panic", "dread", "frightened", "alarmed"
        ],
        EmotionType.SURPRISE: [
            "surprised", "amazed", "astonished", "shocked", "stunned",
            "unexpected", "startled", "wow", "incredible"
        ],
        EmotionType.DISGUST: [
            "disgusted", "revolted", "repulsed", "gross", "sick",
            "horrible", "awful", "terrible", "nasty"
        ],
        EmotionType.TRUST: [
            "trust", "believe", "confident", "reliable", "safe",
            "secure", "faith", "loyal", "honest"
        ],
        EmotionType.ANTICIPATION: [
            "expect", "anticipate", "hope", "look forward", "eager",
            "curious", "interested", "wonder", "excited about"
        ]
    }
    
    # Valence mapping
    VALENCE_MAP = {
        EmotionType.JOY: 0.8,
        EmotionType.TRUST: 0.6,
        EmotionType.ANTICIPATION: 0.4,
        EmotionType.SURPRISE: 0.1,
        EmotionType.FEAR: -0.5,
        EmotionType.SADNESS: -0.7,
        EmotionType.DISGUST: -0.6,
        EmotionType.ANGER: -0.8
    }
    
    def __init__(self):
        self.active = True
        self.state = EmotionalState()
        self.emotional_history: List[EmotionalState] = []
        self.detected_markers: List[EmotionalMarker] = []
    
    def process(self, input_data: Any, context: Any) -> List[Any]:
        """
        Process input with emotional awareness.
        
        Returns list of Thought objects.
        """
        from unimind.core import Thought
        
        thoughts = []
        input_str = str(input_data).lower()
        
        # Detect emotions in input
        detected = self._detect_emotions(input_str)
        
        for marker in detected:
            thoughts.append(Thought(
                content=f"[Emotion] Detected {marker.emotion.value}: '{marker.trigger}' (intensity: {marker.intensity:.1f})",
                thought_type="observation",
                confidence=marker.intensity,
                source_module="emotion_module"
            ))
            self.detected_markers.append(marker)
        
        # Update internal state based on detected emotions
        if detected:
            self._update_state(detected)
        
        # Generate empathetic response suggestions
        empathetic = self._generate_empathetic_response(detected, context)
        if empathetic:
            thoughts.append(Thought(
                content=f"[Emotion/empathy] {empathetic}",
                thought_type="inference",
                confidence=0.7,
                source_module="emotion_module"
            ))
        
        # Add emotional context awareness
        if self.state.intensity > 0.6:
            thoughts.append(Thought(
                content=f"[Emotion/state] High emotional intensity detected ({self.state.primary_emotion.value}). Consider emotional impact in response.",
                thought_type="observation",
                confidence=0.8,
                source_module="emotion_module"
            ))
        
        # Emotional inference
        emotional_inference = self._emotional_inference(input_str, detected)
        if emotional_inference:
            thoughts.append(Thought(
                content=f"[Emotion/inference] {emotional_inference}",
                thought_type="inference",
                confidence=0.65,
                source_module="emotion_module"
            ))
        
        return thoughts
    
    def evaluate(self, thoughts: List[Any]) -> float:
        """Evaluate emotional coherence of thoughts."""
        if not thoughts:
            return 0.5
        
        # Check for emotional awareness
        emotion_thoughts = [t for t in thoughts if "emotion" in t.source_module.lower()]
        awareness_score = min(1.0, len(emotion_thoughts) * 0.2)
        
        # Check valence consistency
        valence_consistency = self._check_valence_consistency(thoughts)
        
        return (awareness_score + valence_consistency) / 2
    
    def _detect_emotions(self, text: str) -> List[EmotionalMarker]:
        """Detect emotions in text."""
        markers = []
        
        for emotion, keywords in self.EMOTION_LEXICON.items():
            for keyword in keywords:
                if keyword in text:
                    # Find context around the keyword
                    pattern = rf"(.{{0,30}}{re.escape(keyword)}.{{0,30}})"
                    match = re.search(pattern, text)
                    context = match.group(1) if match else keyword
                    
                    # Calculate intensity based on modifiers
                    intensity = 0.6
                    if any(mod in text for mod in ["very", "extremely", "really", "so"]):
                        intensity = 0.9
                    elif any(mod in text for mod in ["a bit", "slightly", "somewhat"]):
                        intensity = 0.4
                    
                    markers.append(EmotionalMarker(
                        emotion=emotion,
                        trigger=keyword,
                        intensity=intensity,
                        context=context.strip()
                    ))
        
        return markers
    
    def _update_state(self, markers: List[EmotionalMarker]):
        """Update emotional state based on detected markers."""
        if not markers:
            return
        
        # Find dominant emotion
        emotion_scores: Dict[EmotionType, float] = {}
        for marker in markers:
            if marker.emotion not in emotion_scores:
                emotion_scores[marker.emotion] = 0
            emotion_scores[marker.emotion] += marker.intensity
        
        dominant = max(emotion_scores.items(), key=lambda x: x[1])
        
        # Update state
        old_state = EmotionalState(
            primary_emotion=self.state.primary_emotion,
            intensity=self.state.intensity,
            valence=self.state.valence,
            arousal=self.state.arousal
        )
        
        self.state.primary_emotion = dominant[0]
        self.state.intensity = min(1.0, dominant[1])
        self.state.valence = self.VALENCE_MAP.get(dominant[0], 0)
        self.state.arousal = self._calculate_arousal(markers)
        self.state.secondary_emotions = {e: s for e, s in emotion_scores.items() if e != dominant[0]}
        self.state.last_updated = datetime.utcnow()
        
        # Record history
        self.emotional_history.append(old_state)
        if len(self.emotional_history) > 100:
            self.emotional_history = self.emotional_history[-100:]
    
    def _calculate_arousal(self, markers: List[EmotionalMarker]) -> float:
        """Calculate arousal level from emotional markers."""
        high_arousal = {EmotionType.ANGER, EmotionType.FEAR, EmotionType.JOY, EmotionType.SURPRISE}
        low_arousal = {EmotionType.SADNESS, EmotionType.DISGUST}
        
        arousal_sum = 0
        count = 0
        
        for marker in markers:
            if marker.emotion in high_arousal:
                arousal_sum += 0.8 * marker.intensity
            elif marker.emotion in low_arousal:
                arousal_sum += 0.3 * marker.intensity
            else:
                arousal_sum += 0.5 * marker.intensity
            count += 1
        
        return arousal_sum / count if count > 0 else 0.5
    
    def _generate_empathetic_response(
        self,
        markers: List[EmotionalMarker],
        context: Any
    ) -> Optional[str]:
        """Generate an empathetic response suggestion."""
        if not markers:
            return None
        
        dominant = max(markers, key=lambda m: m.intensity)
        
        empathy_templates = {
            EmotionType.JOY: "The user seems positive. Reinforce this energy with enthusiasm.",
            EmotionType.SADNESS: "The user may be experiencing difficulty. Approach with compassion and support.",
            EmotionType.ANGER: "The user appears frustrated. Acknowledge their concerns and offer solutions.",
            EmotionType.FEAR: "The user seems worried. Provide reassurance and clear information.",
            EmotionType.SURPRISE: "The user is surprised. Help them process and understand the situation.",
            EmotionType.DISGUST: "The user has strong negative reactions. Validate their perspective.",
            EmotionType.TRUST: "The user shows trust. Maintain reliability and transparency.",
            EmotionType.ANTICIPATION: "The user is eager. Channel this energy productively."
        }
        
        return empathy_templates.get(dominant.emotion)
    
    def _emotional_inference(
        self,
        text: str,
        markers: List[EmotionalMarker]
    ) -> Optional[str]:
        """Make inferences based on emotional content."""
        if not markers:
            return None
        
        # Check for emotional transitions
        if len(self.emotional_history) >= 2:
            prev = self.emotional_history[-1]
            current = self.state
            
            if prev.valence < 0 and current.valence > 0:
                return "Emotional shift detected: moving from negative to positive state"
            elif prev.valence > 0 and current.valence < 0:
                return "Emotional shift detected: moving from positive to negative state"
        
        # Check for mixed emotions
        if len(markers) >= 2:
            emotions = [m.emotion for m in markers]
            valences = [self.VALENCE_MAP.get(e, 0) for e in emotions]
            
            if max(valences) > 0.3 and min(valences) < -0.3:
                return "Mixed emotions detected - user may be experiencing ambivalence"
        
        # Intensity-based inference
        if markers and max(m.intensity for m in markers) > 0.8:
            return "Strong emotional intensity detected - this topic is important to the user"
        
        return None
    
    def _check_valence_consistency(self, thoughts: List[Any]) -> float:
        """Check if emotional valence is consistent across thoughts."""
        return 0.7  # Simplified - could analyze thought content
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current emotional state as dictionary."""
        return {
            "primary_emotion": self.state.primary_emotion.value,
            "intensity": self.state.intensity,
            "valence": self.state.valence,
            "arousal": self.state.arousal,
            "secondary_emotions": {e.value: v for e, v in self.state.secondary_emotions.items()}
        }
    
    def get_emotional_trajectory(self, count: int = 10) -> List[Dict]:
        """Get recent emotional history."""
        return [
            {
                "emotion": s.primary_emotion.value,
                "intensity": s.intensity,
                "valence": s.valence
            }
            for s in self.emotional_history[-count:]
        ]
