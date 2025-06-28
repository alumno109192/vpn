#!/bin/bash
# VPN Manager Launcher Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Use the system Python3 to run Main.py
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 Main.py "$@"
