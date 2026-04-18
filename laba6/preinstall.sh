#!/bin/bash
set -e
echo "[preinstall] Installing dependencies..."
sudo apt update
sudo apt install -y libopencv-dev cmake build-essential libv4l-dev v4l-utils
echo "[preinstall] Done."
