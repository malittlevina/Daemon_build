#!/bin/bash

# Ensure dependencies are installed (minimal check)
if ! python3 -c "import psutil" &> /dev/null; then
    echo "Installing missing dependency: psutil"
    pip install psutil
fi

if ! python3 -c "import websockets" &> /dev/null; then
    echo "Installing missing dependency: websockets"
    pip install websockets
fi

# Ensure PYTHONPATH includes workspace
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Starting Unified Daemon..."
echo "--------------------------"
python3 main.py
