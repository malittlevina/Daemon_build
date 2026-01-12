# AI-Native Operating System Architecture

## Overview
This system is designed as a cognitive, event-driven operating system where a central "daemon" acts as the conscious entity, coordinating various "brain modules" via a central event bus (`Unimind`).

## Core Components

### 1. Unimind (The Kernel / Event Bus)
- **Location**: `unimind/core.py`
- **Role**: The central nervous system.
- **Function**:
    - Registers all modules.
    - Routes events (`emit`/`subscribe`) between subsystems.
    - Triggers reflection cycles.

### 2. The Daemon (The Runtime)
- **Location**: `main.py`
- **Role**: The main process loop.
- **Function**:
    - Initializes the system.
    - Captures User Input and Sensor Data.
    - Feeds data into `Unimind`.
    - Manages the lifecycle of background threads.

### 3. Brain Modules
- **EmotionEngine** (`emotion/`): Reacts to system events (e.g., success, errors, user praise) to update internal state.
- **NLUEngine** (`nlu/`): Parses natural language into Intents or Scrolls.
- **Codex** (`codex/`): Long-term memory store (vector DB + logs).
- **Personality** (`introspection/`): Tracks psychological state.

### 4. Scrolls (LAM - Large Action Model)
- **Location**: `scrolls/`
- **Role**: The "Hands" of the AI.
- **Function**:
    - Executes concrete tasks (e.g., "scan wifi", "optimize self").
    - **Self-Coding**: Can dynamically generate new scrolls (`scrolls/library/`) at runtime based on user needs.

### 5. ThothBridge & Apps
- **Location**: `bridge/` and `apps/`
- **Role**: Interface to external applications.
- **Function**:
    - Loads apps from `apps/`.
    - Provides a bi-directional communication channel between the AI daemon and apps.

### 6. Device Integration
- **Location**: `sensors/`
- **Role**: The "Senses".
- **Function**:
    - `DeviceScanner` continuously monitors Bluetooth, WiFi, and NFC.
    - Emits `device_detected` events to `Unimind`.

## Data Flow
1. **Stimulus**: User types a command OR DeviceScanner finds a device.
2. **Event**: `Unimind` receives `input_received` or `device_detected`.
3. **Reaction**:
    - `EmotionEngine` updates mood.
    - `NLUEngine` interprets intent.
4. **Action**: `ScrollEngine` executes the matching Scroll (Action).
5. **Memory**: Result is logged to `Codex`.

## How to Verify
- Run `python main.py`.
- Type `devices` to see real-time sensor data.
- Type `create scroll <name> : <task>` to test self-coding.
- Check `logs/` for memory trails.
