# unimind/regions/amygdala.py
# Amygdala - Emotional processing, fear/reward, motivation, valence tagging

import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import math


class EmotionType(Enum):
    """Primary emotions."""
    JOY = "joy"
    SADNESS = "sadness"
    FEAR = "fear"
    ANGER = "anger"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    # Secondary/complex emotions
    CURIOSITY = "curiosity"
    PRIDE = "pride"
    FRUSTRATION = "frustration"
    CONTENTMENT = "contentment"
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"


class MotivationalState(Enum):
    """Motivational/drive states."""
    EXPLORING = "exploring"         # Seeking novelty
    ACHIEVING = "achieving"         # Goal pursuit
    RESTING = "resting"             # Energy conservation
    CONNECTING = "connecting"       # Social bonding
    PROTECTING = "protecting"       # Self-preservation
    LEARNING = "learning"           # Knowledge acquisition


@dataclass
class EmotionalState:
    """Current emotional state representation."""
    # Core dimensions (Russell's circumplex model)
    valence: float = 0.0            # -1 (negative) to 1 (positive)
    arousal: float = 0.5            # 0 (calm) to 1 (excited)
    
    # Primary emotions (Plutchik's wheel)
    emotions: Dict[str, float] = field(default_factory=dict)
    
    # Dominant emotion
    dominant_emotion: Optional[EmotionType] = None
    
    # Mood (longer-term emotional state)
    mood_valence: float = 0.0
    mood_stability: float = 0.5
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "dominant_emotion": self.dominant_emotion.value if self.dominant_emotion else None,
            "emotions": self.emotions,
            "mood_valence": self.mood_valence,
            "mood_stability": self.mood_stability
        }


@dataclass
class EmotionalMemoryTag:
    """Emotional tag attached to a memory."""
    memory_id: str
    valence: float
    arousal: float
    emotions: Dict[str, float]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RewardSignal:
    """A reward/punishment signal."""
    signal_id: str
    value: float                    # -1 to 1
    source: str
    trigger: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class Amygdala:
    """
    Amygdala module - Emotional processing center.
    
    Responsible for:
    - Emotional state tracking (valence, arousal, discrete emotions)
    - Fear and reward processing
    - Emotional tagging of memories
    - Motivation and drive management
    - Emotional influence on cognition
    - Threat/opportunity detection
    """
    
    def __init__(self, neural_bus=None):
        self.neural_bus = neural_bus
        
        # Current emotional state
        self.state = EmotionalState()
        
        # Emotional memory tags
        self.memory_tags: Dict[str, EmotionalMemoryTag] = {}
        
        # Reward history
        self.reward_history: deque = deque(maxlen=100)
        self.cumulative_reward: float = 0.0
        
        # Fear associations (learned fears)
        self.fear_associations: Dict[str, float] = {}  # stimulus -> fear_level
        
        # Reward associations (learned rewards)
        self.reward_associations: Dict[str, float] = {}  # stimulus -> reward_expectation
        
        # Motivational state
        self.motivation = MotivationalState.EXPLORING
        self.drive_levels: Dict[str, float] = {
            "curiosity": 0.7,
            "achievement": 0.5,
            "social": 0.3,
            "safety": 0.2
        }
        
        # Emotional regulation
        self.regulation_strength = 0.5  # How much to regulate emotions
        
        # State history
        self.state_history: deque = deque(maxlen=50)
        
        # AI model hook
        self.sentiment_model = None
        
        # Capabilities
        self.capabilities = [
            "emotion_detection", "valence_tagging", "fear_processing",
            "reward_processing", "motivation", "threat_detection"
        ]
        
        # Register with neural bus
        if self.neural_bus:
            self._register_with_bus()
            
        print("[Amygdala] Emotional processing initialized.")
        
    def _register_with_bus(self):
        """Register with neural bus."""
        self.neural_bus.register_region(
            region_id="amygdala",
            name="Amygdala",
            module_type="limbic",
            capabilities=self.capabilities,
            handler=self._handle_signal
        )
        
    def _handle_signal(self, signal) -> Optional[Any]:
        """Handle incoming neural signals."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        payload = signal.payload
        
        if signal.signal_type == SignalType.QUERY:
            capability = payload.get("capability")
            if capability == "emotion_detection":
                return self._handle_emotion_query(payload.get("data", {}))
            elif capability == "valence_tagging":
                return self._handle_tagging_query(payload.get("data", {}))
                
        elif signal.signal_type == SignalType.REWARD:
            self.process_reward(
                value=payload.get("reward", 0),
                source=signal.source,
                trigger=payload.get("goal_id", "unknown")
            )
            
        elif signal.signal_type == SignalType.EXCITATORY:
            # Process stimulus for emotional content
            if "content" in payload:
                self.process_stimulus(payload["content"], payload.get("context", {}))
                
        return None
        
    def _handle_emotion_query(self, data: Dict) -> Any:
        """Handle emotion detection query."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        if "analyze" in data:
            result = self.analyze_emotional_content(data["analyze"])
            return NeuralSignal(
                signal_id=f"amyg_emotion",
                signal_type=SignalType.RESPONSE,
                source="amygdala",
                target=None,
                payload={"analysis": result}
            )
        elif "state" in data:
            return NeuralSignal(
                signal_id=f"amyg_state",
                signal_type=SignalType.RESPONSE,
                source="amygdala",
                target=None,
                payload={"state": self.state.to_dict()}
            )
        return None
        
    def _handle_tagging_query(self, data: Dict) -> Any:
        """Handle valence tagging query."""
        from unimind.neural_bus import NeuralSignal, SignalType
        
        if "memory_id" in data and "content" in data:
            tag = self.tag_memory(data["memory_id"], data["content"])
            return NeuralSignal(
                signal_id=f"amyg_tag",
                signal_type=SignalType.RESPONSE,
                source="amygdala",
                target=None,
                payload={"tag": {"memory_id": tag.memory_id, "valence": tag.valence}}
            )
        return None
        
    def set_sentiment_model(self, model: Any):
        """Set the sentiment analysis model."""
        self.sentiment_model = model
        print("[Amygdala] Sentiment model configured.")
        
    def analyze_emotional_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze emotional content of text.
        
        Args:
            content: Text to analyze
            
        Returns:
            Emotional analysis results
        """
        # Use sentiment model if available
        if self.sentiment_model:
            try:
                result = self.sentiment_model.analyze(content)
                # Normalize result format
                return {
                    "valence": result.get("score", 0.0),
                    "arousal": 0.5,
                    "emotions": {},
                    "dominant": result.get("sentiment", "neutral")
                }
            except:
                pass
                
        # Fallback to keyword-based analysis
        content_lower = content.lower()
        
        # Simple emotion keyword detection
        emotion_keywords = {
            EmotionType.JOY: ["happy", "joy", "wonderful", "great", "excellent", "love", "excited"],
            EmotionType.SADNESS: ["sad", "unhappy", "depressed", "sorry", "loss", "miss"],
            EmotionType.FEAR: ["afraid", "fear", "scared", "worried", "anxious", "danger"],
            EmotionType.ANGER: ["angry", "mad", "furious", "hate", "annoyed", "frustrated"],
            EmotionType.SURPRISE: ["surprised", "unexpected", "amazing", "wow", "shocked"],
            EmotionType.DISGUST: ["disgusting", "gross", "horrible", "awful"],
            EmotionType.TRUST: ["trust", "believe", "reliable", "honest", "faith"],
            EmotionType.ANTICIPATION: ["expect", "hope", "looking forward", "anticipate", "wait"],
            EmotionType.CURIOSITY: ["curious", "wonder", "interesting", "question", "explore"],
        }
        
        detected_emotions = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                detected_emotions[emotion.value] = min(1.0, score * 0.3)
                
        # Calculate valence
        positive_emotions = [EmotionType.JOY, EmotionType.TRUST, EmotionType.ANTICIPATION]
        negative_emotions = [EmotionType.SADNESS, EmotionType.FEAR, EmotionType.ANGER, EmotionType.DISGUST]
        
        pos_score = sum(detected_emotions.get(e.value, 0) for e in positive_emotions)
        neg_score = sum(detected_emotions.get(e.value, 0) for e in negative_emotions)
        
        valence = (pos_score - neg_score) / max(pos_score + neg_score, 1)
        
        # Calculate arousal
        high_arousal = [EmotionType.FEAR, EmotionType.ANGER, EmotionType.SURPRISE, EmotionType.EXCITEMENT]
        arousal = sum(detected_emotions.get(e.value, 0) for e in high_arousal) / 4
        
        return {
            "valence": valence,
            "arousal": arousal,
            "emotions": detected_emotions,
            "dominant": max(detected_emotions.keys(), key=lambda k: detected_emotions[k]) if detected_emotions else None
        }
        
    def process_stimulus(self, stimulus: Any, context: Dict = None):
        """
        Process an incoming stimulus for emotional content.
        
        Args:
            stimulus: The stimulus to process
            context: Additional context
        """
        # Analyze emotional content
        analysis = self.analyze_emotional_content(str(stimulus))
        
        # Check for fear associations
        stimulus_str = str(stimulus).lower()
        for trigger, fear_level in self.fear_associations.items():
            if trigger in stimulus_str:
                analysis["valence"] -= fear_level * 0.5
                analysis["arousal"] = min(1.0, analysis["arousal"] + fear_level * 0.3)
                
        # Check for reward associations
        for trigger, reward_level in self.reward_associations.items():
            if trigger in stimulus_str:
                analysis["valence"] += reward_level * 0.3
                
        # Update emotional state
        self._update_state(analysis)
        
        # Broadcast emotional update
        if self.neural_bus:
            self.neural_bus.emit_broadcast(
                source="amygdala",
                payload={
                    "emotion_update": self.state.to_dict(),
                    "stimulus_analysis": analysis
                },
                priority="normal"
            )
            
    def _update_state(self, analysis: Dict):
        """Update emotional state based on analysis."""
        # Smooth update with regulation
        alpha = 1 - self.regulation_strength
        
        self.state.valence = self.state.valence * (1 - alpha) + analysis["valence"] * alpha
        self.state.arousal = self.state.arousal * (1 - alpha) + analysis["arousal"] * alpha
        
        # Update emotions
        for emotion, intensity in analysis.get("emotions", {}).items():
            current = self.state.emotions.get(emotion, 0)
            self.state.emotions[emotion] = current * (1 - alpha) + intensity * alpha
            
        # Update dominant emotion
        if self.state.emotions:
            dominant = max(self.state.emotions.keys(), key=lambda k: self.state.emotions[k])
            self.state.dominant_emotion = EmotionType(dominant)
            
        # Update mood (slower change)
        self.state.mood_valence = self.state.mood_valence * 0.95 + self.state.valence * 0.05
        
        self.state.timestamp = datetime.now().isoformat()
        self.state_history.append(self.state.to_dict())
        
    def process_reward(self, value: float, source: str, trigger: str):
        """
        Process a reward or punishment signal.
        
        Args:
            value: Reward value (-1 to 1)
            source: Where the reward came from
            trigger: What triggered the reward
        """
        signal = RewardSignal(
            signal_id=f"rew_{int(time.time() * 1000)}",
            value=value,
            source=source,
            trigger=trigger
        )
        
        self.reward_history.append(signal)
        self.cumulative_reward += value
        
        # Update emotional state
        if value > 0:
            self.state.valence = min(1.0, self.state.valence + value * 0.3)
            self.state.emotions["joy"] = self.state.emotions.get("joy", 0) + value * 0.2
        else:
            self.state.valence = max(-1.0, self.state.valence + value * 0.3)
            self.state.emotions["frustration"] = self.state.emotions.get("frustration", 0) + abs(value) * 0.2
            
        # Learn reward association
        trigger_lower = trigger.lower()
        if value > 0.3:
            self.reward_associations[trigger_lower] = self.reward_associations.get(trigger_lower, 0) + value * 0.1
        elif value < -0.3:
            # Negative rewards can become fear associations
            self.fear_associations[trigger_lower] = self.fear_associations.get(trigger_lower, 0) + abs(value) * 0.1
            
        print(f"[Amygdala] Processed reward: {value:.2f} from {source}")
        
    def tag_memory(self, memory_id: str, content: str) -> EmotionalMemoryTag:
        """
        Tag a memory with emotional information.
        
        Args:
            memory_id: ID of the memory to tag
            content: Memory content to analyze
            
        Returns:
            EmotionalMemoryTag
        """
        analysis = self.analyze_emotional_content(content)
        
        tag = EmotionalMemoryTag(
            memory_id=memory_id,
            valence=analysis["valence"],
            arousal=analysis["arousal"],
            emotions=analysis.get("emotions", {})
        )
        
        self.memory_tags[memory_id] = tag
        return tag
        
    def get_memory_tag(self, memory_id: str) -> Optional[EmotionalMemoryTag]:
        """Get emotional tag for a memory."""
        return self.memory_tags.get(memory_id)
        
    def learn_fear(self, stimulus: str, intensity: float = 0.5):
        """Learn a fear association."""
        self.fear_associations[stimulus.lower()] = min(1.0, intensity)
        print(f"[Amygdala] Learned fear: {stimulus} ({intensity:.2f})")
        
    def extinguish_fear(self, stimulus: str, amount: float = 0.2):
        """Reduce a fear association (extinction)."""
        key = stimulus.lower()
        if key in self.fear_associations:
            self.fear_associations[key] = max(0, self.fear_associations[key] - amount)
            if self.fear_associations[key] < 0.1:
                del self.fear_associations[key]
                
    def check_threat(self, stimulus: str) -> Tuple[bool, float]:
        """
        Check if stimulus is a threat.
        
        Returns:
            Tuple of (is_threat, threat_level)
        """
        stimulus_lower = stimulus.lower()
        
        # Check fear associations
        max_fear = 0.0
        for trigger, level in self.fear_associations.items():
            if trigger in stimulus_lower:
                max_fear = max(max_fear, level)
                
        return max_fear > 0.3, max_fear
        
    def update_motivation(self):
        """Update motivational state based on drives and emotions."""
        # Calculate drive influence
        if self.state.valence < -0.3:
            # Negative emotion -> protection mode
            self.motivation = MotivationalState.PROTECTING
        elif self.state.arousal > 0.7 and self.state.valence > 0:
            # High arousal positive -> achieving
            self.motivation = MotivationalState.ACHIEVING
        elif self.drive_levels["curiosity"] > 0.6:
            self.motivation = MotivationalState.EXPLORING
        elif self.state.arousal < 0.3:
            self.motivation = MotivationalState.RESTING
        else:
            self.motivation = MotivationalState.LEARNING
            
    def get_emotional_influence(self) -> Dict[str, float]:
        """
        Get how emotions should influence cognition.
        
        Returns influence weights for different cognitive processes.
        """
        influence = {
            "attention_to_threats": 0.0,
            "risk_aversion": 0.5,
            "exploration": 0.5,
            "social_approach": 0.5,
            "memory_encoding_boost": 0.0
        }
        
        # Fear increases threat attention
        fear_level = self.state.emotions.get("fear", 0)
        influence["attention_to_threats"] = fear_level
        
        # Negative valence increases risk aversion
        if self.state.valence < 0:
            influence["risk_aversion"] = 0.5 + abs(self.state.valence) * 0.3
            
        # Positive valence increases exploration
        if self.state.valence > 0:
            influence["exploration"] = 0.5 + self.state.valence * 0.3
            
        # High arousal boosts memory encoding
        influence["memory_encoding_boost"] = self.state.arousal * 0.5
        
        return influence
        
    def regulate(self, target_valence: float = 0.0, target_arousal: float = 0.5):
        """
        Attempt emotional regulation toward target state.
        
        Args:
            target_valence: Target valence (-1 to 1)
            target_arousal: Target arousal (0 to 1)
        """
        # Gradual regulation
        self.state.valence += (target_valence - self.state.valence) * self.regulation_strength * 0.1
        self.state.arousal += (target_arousal - self.state.arousal) * self.regulation_strength * 0.1
        
        # Reduce extreme emotions
        for emotion in self.state.emotions:
            self.state.emotions[emotion] *= (1 - self.regulation_strength * 0.1)
            
    def get_state(self) -> EmotionalState:
        """Get current emotional state."""
        return self.state
        
    def get_status(self) -> Dict[str, Any]:
        """Get amygdala status."""
        return {
            "current_state": self.state.to_dict(),
            "motivation": self.motivation.value,
            "drive_levels": self.drive_levels,
            "fear_associations": len(self.fear_associations),
            "reward_associations": len(self.reward_associations),
            "cumulative_reward": self.cumulative_reward,
            "memory_tags": len(self.memory_tags),
            "regulation_strength": self.regulation_strength
        }
