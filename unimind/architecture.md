# Unimind Cognitive Architecture

## Current State Analysis

### Existing Components
| Module | Location | Current Capability | Limitations |
|--------|----------|-------------------|-------------|
| Unimind Core | `unimind/core.py` | Basic module registry, reflection loop | No inter-module communication, no processing |
| Decision Matrix | `unimind/decision_matrix.py` | Weighted scoring | Static weights, no learning |
| Emotion Engine | `emotion/emotion_engine.py` | Stimulus-response mapping | Simple lookup, no valence/arousal model |
| Ethical Core | `guardian/ethical_core.py` | Keyword-based evaluation | No contextual reasoning |
| Fuzzy Logic | `guardian/fuzzy_logic.py` | Rule-based context evaluation | Limited rule set |
| Memory Logger | `memory_tree/memory_logger.py` | Event logging | No consolidation or retrieval intelligence |
| Personality Tracker | `introspection/personality_tracker.py` | Trait logging | No personality dynamics |

### Identified Gaps
1. **No Central Processing**: Modules don't process information together
2. **No Attention Mechanism**: Can't prioritize or focus on relevant information
3. **No Working Memory**: No short-term processing buffer
4. **No Consciousness Model**: No unified experience or self-model
5. **No Neural Connectivity**: Modules operate in isolation
6. **No AI Model Integration**: No hooks for LLMs or specialized models

---

## Proposed Brain-Inspired Architecture

### Brain Region Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                        UNIMIND CORTEX                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              PREFRONTAL CORTEX (Executive)              │    │
│  │  • Planning & Goal Management                           │    │
│  │  • Decision Making                                      │    │
│  │  • Working Memory Orchestration                         │    │
│  │  • Inhibition Control                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌──────────────┐  ┌─────────┴──────────┐  ┌──────────────┐     │
│  │  BROCA'S     │  │   ATTENTION        │  │  WERNICKE'S  │     │
│  │  (Language   │  │   SYSTEM           │  │  (Language   │     │
│  │   Production)│  │  • Selective       │  │   Comprehen.│     │
│  └──────────────┘  │  • Sustained       │  └──────────────┘     │
│         │          │  • Divided         │          │             │
│         └──────────┴───────────┬────────┴──────────┘             │
│                                │                                 │
│  ┌──────────────┐  ┌───────────┴──────────┐  ┌──────────────┐   │
│  │  TEMPORAL    │  │   WORKING MEMORY     │  │   PARIETAL   │   │
│  │  LOBE        │  │  • Central Executive │  │   LOBE       │   │
│  │  • Semantic  │  │  • Phonological Loop │  │  • Spatial   │   │
│  │    Memory    │  │  • Visuospatial Pad  │  │    Reasoning │   │
│  │  • Pattern   │  │  • Episodic Buffer   │  │  • Numeracy  │   │
│  └──────────────┘  └──────────────────────┘  └──────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────┴───────┐    ┌─────────┴─────────┐    ┌──────┴───────┐
│   LIMBIC      │    │    HIPPOCAMPUS    │    │  CEREBELLUM  │
│   SYSTEM      │    │                   │    │              │
│ ┌───────────┐ │    │  • Memory Consol. │    │  • Pattern   │
│ │ AMYGDALA  │ │    │  • Spatial Maps   │    │    Learning  │
│ │ • Fear    │ │    │  • Episodic Index │    │  • Motor     │
│ │ • Reward  │ │    │  • Replay/Dream   │    │    Control   │
│ │ • Valence │ │    │                   │    │  • Timing    │
│ └───────────┘ │    └───────────────────┘    └──────────────┘
│ ┌───────────┐ │              │
│ │ HYPOTHAL. │ │              │
│ │ • Drives  │ │     ┌────────┴────────┐
│ │ • States  │ │     │   BASAL GANGLIA │
│ └───────────┘ │     │  • Habit Loop   │
└───────────────┘     │  • Reward Pred. │
                      └─────────────────┘

                      ┌─────────────────┐
                      │   NEURAL BUS    │
                      │  (Connectivity) │
                      │  • Sync Signals │
                      │  • Data Routing │
                      │  • Broadcast    │
                      └─────────────────┘
```

### Module Responsibilities

| Brain Region | Primary Function | AI Model Integration |
|--------------|-----------------|---------------------|
| Prefrontal Cortex | Executive control, planning, decision-making | LLM for reasoning |
| Hippocampus | Memory consolidation, spatial mapping, recall | Vector embeddings |
| Amygdala | Emotional valence, fear/reward, motivation | Sentiment models |
| Cerebellum | Pattern learning, motor programs, timing | Seq2Seq models |
| Broca's Area | Language generation, speech production | Text generation |
| Wernicke's Area | Language comprehension, semantic parsing | NLU models |
| Temporal Lobe | Long-term semantic memory, object recognition | Knowledge graphs |
| Parietal Lobe | Spatial reasoning, attention, numeracy | Spatial transformers |
| Basal Ganglia | Habit formation, reward prediction, action selection | RL models |
| Attention System | Selective focus, salience detection | Attention mechanisms |
| Working Memory | Short-term buffer, cognitive manipulation | Context windows |

---

## Implementation Priority

### Phase 1: Core Infrastructure
1. Neural Bus (inter-module communication)
2. Advanced Unimind Core (orchestration)
3. Working Memory System

### Phase 2: Cognitive Modules
4. Prefrontal Cortex (executive)
5. Hippocampus (memory)
6. Amygdala (emotion)

### Phase 3: Specialized Processing
7. Cerebellum (learning)
8. Language Areas (Broca/Wernicke)
9. Attention System

### Phase 4: Integration
10. Consciousness Model
11. AI Model Hooks
12. Cross-module Learning
