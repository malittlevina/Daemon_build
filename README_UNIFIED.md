# Unified AI Daemon

This is a modular, embodied, and intrinsically motivated AI daemon. It combines a procedural world engine, physical sensors, advanced NLU, and a unified cognitive architecture (`Unimind`).

## Architecture

The system is organized into "Faculties" managed by `Unimind`:

1.  **World (Embodiment in Virtual Space)**
    *   **WorldEngine**: Runs a procedural simulation (Locations, Entities, Physics, Weather).
    *   **SpatialServer**: Allows connection to external 3D engines (Unity/Unreal).
2.  **Perception (Embodiment in Physical Space)**
    *   **SensorManager**: Manages Vision (Webcam/VLM) and Audio sensors.
    *   **CuriosityModule**: Detects "surprising" events in both virtual and physical worlds to trigger learning.
3.  **Motivation (Will)**
    *   **DriveSystem**: Manages internal drives (Curiosity, Competence, Coherence).
    *   **Autonomous Agent**: Triggers actions automatically when drives are critical.
4.  **Logic & Knowledge (Reason)**
    *   **LAM**: Large Action Model for planning.
    *   **Codex**: Knowledge base and Curriculum system (Narrative, Code, Science).
    *   **CodeMaster**: Design pattern generation and code review.
5.  **Expression**
    *   **AvatarEngine**: Manages the AI's "Face" (ASCII) based on mood.
    *   **PersonalityEngine**: Modulates text response tone based on drives.

## Getting Started

1.  **Run the Daemon**:
    ```bash
    ./run.sh
    ```
2.  **Commands**:
    *   `status`: Show system health and internal state reflection.
    *   `explore world`: Interact with the procedural world.
    *   `generate pattern [name]`: Generate code scaffolding (e.g., "singleton").
    *   `what is [topic]`: Query knowledge (e.g., "what is the hero's journey").
    *   `good job` / `bad job`: Reinforce behavior.

## Training

*   **Ingest Data**: `ingest /path/to/folder`
*   **Expand Curriculum**: Add JSON files to `codex/curriculums/`.

## Interoperability

To connect a 3D engine (Unity/Unreal), connect a WebSocket client to `ws://localhost:8765` and send `world_update` JSON packets.
