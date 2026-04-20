#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

echo "[build] Configuring with CMake..."
mkdir -p "$BUILD_DIR"
cmake -S "$SCRIPT_DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release

echo "[build] Compiling..."
cmake --build "$BUILD_DIR" -- -j"$(nproc)"

echo "[build] Done. Binary: $BUILD_DIR/lab6"
