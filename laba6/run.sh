#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BINARY="$SCRIPT_DIR/build/lab6"

if [ ! -f "$BINARY" ]; then
    echo "[run] Binary not found. Running build first..."
    bash "$SCRIPT_DIR/build.sh"
fi

# Optional: pass camera index as first argument (default 0)
CAM_INDEX="${1:-0}"
echo "[run] Starting with camera index $CAM_INDEX"
"$BINARY" "$CAM_INDEX"
