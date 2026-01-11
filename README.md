# ThothOS Daemon Build (Prometheus)

This is the official Prometheus daemon build (v2_origin), an intelligent AI agent running on ThothOS. It includes:

## Core Features
- ✅ **Unimind Cognitive Architecture** (brain-inspired modular cognition)
- ✅ **Voice Listener** (real-time symbolic command parsing)
- ✅ **Scroll Engine** (ritual triggers and symbolic routines)
- ✅ **Emotion Engine** (emotional modeling for interactions)
- ✅ **Prometheus Specialties** (multi-domain skill sets)
- ✅ **Sensor Input** (camera vision + voice ambient tone)
- ✅ **Memory Tree Logger** (life memory timeline system)
- ✅ **Reflection Journal** (self-coding + evolution logs)
- ✅ **Codex Ingestion** (PDF/web summarization knowledge)
- ✅ **Multi-language Code Execution** (Python, Rust, Julia)
- ✅ **AR/XR Subsystem** (augmented, virtual, and mixed reality support)
- ✅ **LAM Training System** (Language-Action Model with reinforcement learning)

## Unimind Cognitive Architecture

The daemon features an advanced brain-inspired cognitive architecture with specialized modules that communicate via a neural bus system.

### Brain Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     UNIMIND CORTEX                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           PREFRONTAL CORTEX (Executive)             │    │
│  │  • Planning & Goal Management                       │    │
│  │  • Decision Making                                  │    │
│  │  • Inhibition Control                               │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│  ┌──────────┐    ┌───────┴───────┐    ┌──────────┐          │
│  │ WORKING  │    │   ATTENTION   │    │ THOUGHT  │          │
│  │ MEMORY   │────│    SYSTEM     │────│  STREAM  │          │
│  └──────────┘    └───────────────┘    └──────────┘          │
└─────────────────────────────────────────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───┴───────┐      ┌────────┴────────┐      ┌──────┴───────┐
│HIPPOCAMPUS│      │    AMYGDALA     │      │  CEREBELLUM  │
│• Episodic │      │ • Emotions      │      │ • Motor      │
│  Memory   │      │ • Fear/Reward   │      │   Programs   │
│• Spatial  │      │ • Motivation    │      │ • Patterns   │
│  Maps     │      │ • Valence       │      │ • Timing     │
└───────────┘      └─────────────────┘      └──────────────┘
                            │
              ┌─────────────┴─────────────┐
              │        NEURAL BUS         │
              │  (Inter-module signals)   │
              └───────────────────────────┘
```

### Neural Bus (`unimind/neural_bus.py`)
- Priority-based signal routing
- Pub/sub messaging between brain regions
- Broadcast and targeted signals
- Attention modulation
- Synchronization pulses

### Cortex (`unimind/cortex.py`)
- Central cognitive orchestration
- Working memory (Baddeley's model)
- Goal management
- Cognitive state tracking
- Consciousness levels (unconscious → meta-aware)

### Prefrontal Cortex (`unimind/regions/prefrontal_cortex.py`)
- **Executive Function**: Goal-directed planning
- **Decision Making**: Multi-criteria option evaluation
- **Inhibition**: Response suppression rules
- **Cognitive Flexibility**: Task switching
- **Planning**: Multi-step plan generation

### Hippocampus (`unimind/regions/hippocampus.py`)
- **Episodic Memory**: Experience storage and retrieval
- **Semantic Network**: Concept and knowledge graphs
- **Spatial Maps**: Cognitive maps for navigation
- **Memory Consolidation**: Short-term to long-term transfer
- **Pattern Completion**: Recall from partial cues

### Amygdala (`unimind/regions/amygdala.py`)
- **Emotional State**: Valence/arousal tracking
- **Discrete Emotions**: Joy, sadness, fear, anger, etc.
- **Fear Learning**: Threat association
- **Reward Processing**: Positive reinforcement
- **Motivation**: Drive state management
- **Emotional Memory Tags**: Valence tagging of memories

### Cerebellum (`unimind/regions/cerebellum.py`)
- **Motor Programs**: Action sequence learning
- **Timing Models**: Duration prediction
- **Error-Based Learning**: Refinement from mistakes
- **Pattern-Pattern Association**: Input-output learning
- **Procedural Memory**: Skill storage

### AI Model Integration (`unimind/ai_models.py`)
Each brain region can connect to specialized AI models:

| Region | AI Model Type | Purpose |
|--------|--------------|---------|
| Prefrontal Cortex | LLM | Reasoning, planning |
| Hippocampus | Embeddings | Semantic memory search |
| Amygdala | Sentiment | Emotion detection |
| Broca's Area | LLM | Language generation |
| Wernicke's Area | NLU | Language understanding |

### Example Usage

```python
from unimind.ai_models import create_connected_brain

# Create complete brain with all regions connected
brain = create_connected_brain()

# Access cortex for high-level thinking
result = brain['cortex'].think("How should I approach this problem?")

# Use prefrontal cortex for planning
plan = brain['prefrontal_cortex'].create_plan("Complete the project")

# Store episodic memory
brain['hippocampus'].store_episodic("Learned about neural networks", importance=0.8)

# Process emotional content
brain['amygdala'].process_stimulus("This is exciting!")

# Learn motor program
brain['cerebellum'].learn_motor_program("task_routine", actions=[...])

# Introspect on cognitive state
state = brain['cortex'].introspect()
```

## AR/XR Capabilities
The daemon now includes full AR/VR/MR support with immersive training capabilities:

### XR Engine (`xr/xr_engine.py`)
- Multi-mode XR sessions (AR, VR, MR, Passthrough)
- Device abstraction (headsets, glasses, phone AR, simulation)
- Session management and event logging
- Symbolic state integration

### AR Overlay Manager (`xr/ar_overlay.py`)
- Text, image, 3D model, and holographic overlays
- World-locked, head-locked, and surface-anchored content
- HUD elements and navigation waypoints
- Training highlight and annotation overlays

### Spatial Anchor System (`xr/spatial_anchor.py`)
- World-space anchor creation and tracking
- Plane and surface detection
- Semantic location labeling
- Persistent anchors across sessions
- Spatial map import/export

### Gesture Interface (`xr/gesture_interface.py`)
- Hand gesture recognition (pinch, grab, point, swipe, etc.)
- Body gesture detection (nod, shake, lean)
- Customizable gesture-to-action bindings
- Hand tracking state management

### XR Training Module (`xr/xr_training.py`)
- Immersive guided training scenarios
- Multi-domain training (technical, mechanical, creative, safety)
- Step-by-step instruction with AR overlays
- Real-time feedback and skill assessment
- Skill progression tracking
- Built-in and custom scenario support

### XR Scroll Commands
- `start xr session` - Start AR/VR/MR session
- `end xr session` - End current XR session
- `start xr training <scenario>` - Begin training scenario
- `end xr training` - End training session
- `create ar overlay` - Create AR info panel
- `clear ar overlays` - Remove overlays
- `place spatial anchor` - Place world anchor
- `show training scenarios` - List available training
- `xr status` - Get XR subsystem status

## LAM (Language-Action Model) Training System

The daemon includes a comprehensive learning system that enables continuous improvement through multiple training paradigms.

### LAM Core (`lam/lam_core.py`)
- Pattern-based action selection from input text
- Confidence-weighted exploration/exploitation
- Reinforcement learning from outcomes
- Automatic pattern persistence and recall

### Action Registry (`lam/action_registry.py`)
- Centralized action registration and discovery
- Action composition and sequencing
- Precondition/postcondition checking
- Built-in actions for all daemon capabilities

### Experience Memory (`lam/experience_memory.py`)
- Episodic memory storage and retrieval
- Similarity-based memory search
- Memory decay and consolidation
- Failure pattern detection
- Lesson extraction from experiences

### Skill Tree (`lam/skill_tree.py`)
- Hierarchical skill representation
- Experience-based leveling system (Novice → Master)
- Skill prerequisites and unlocking
- Learning paths with progression tracking
- Cross-domain skill transfer

### Behavior Trainer (`lam/behavior_trainer.py`)
- **Reinforcement Learning**: Learn from reward signals
- **Imitation Learning**: Learn from demonstrations
- **Curriculum Learning**: Progressive difficulty stages
- **Experience Replay**: Offline learning from memory
- Policy management and optimization

### LAM Planner (`lam/lam_planner.py`)
- Unified interface for all LAM subsystems
- Automatic action selection and execution
- Real-time feedback integration
- Performance analysis and recommendations

### Training Modes
1. **Supervised**: Learn from labeled input-action pairs
2. **Reinforcement**: Learn from reward/penalty feedback
3. **Imitation**: Learn by observing demonstrations
4. **Curriculum**: Structured progressive learning
5. **Self-supervised**: Learn from self-generated tasks

### Curriculum Stages
| Level | Name | Focus |
|-------|------|-------|
| 1 | Basic Responses | Simple input-response patterns |
| 2 | Task Execution | Single-step task execution |
| 3 | Context Awareness | Context-dependent responses |
| 4 | Multi-Step Planning | Complex task planning |
| 5 | XR Integration | AR/VR/XR specific behaviors |
| 6 | Advanced Reasoning | Problem solving and synthesis |
| 7 | Self-Improvement | Meta-learning and optimization |

### LAM Scroll Commands
- `lam train [mode]` - Run training session (curriculum, replay, reinforcement)
- `lam learn <input> <action_type>` - Teach a new pattern
- `lam feedback <reward> [text]` - Provide feedback (-1 to 1)
- `lam status` - View training progress and statistics
- `lam skills` - Show skill tree and proficiency
- `lam curriculum` - View curriculum stages
- `lam recall <query>` - Recall similar past experiences
- `lam replay [batch_size]` - Run experience replay learning

### Example Usage

```python
from lam import get_planner

# Get the LAM planner
planner = get_planner()

# Teach a new pattern
planner.learn_from_demonstration(
    input_text="what's the weather like",
    correct_action={"type": "query", "params": {"source": "weather"}}
)

# Process input and get action
result = planner.plan_next_action("what's the weather like")
print(result["message"])

# Provide feedback
planner.provide_feedback(reward=0.8, feedback_text="Good response")

# Check progress
progress = planner.get_training_progress()
print(f"Curriculum Level: {progress['curriculum_stage']['level']}")
```

## Installation
```bash
git clone https://github.com/andysmomstoys/Daemon_build.git
cd Daemon_build
bash dev/install_mac.sh  # or install_linux.sh
python3 main.py
