#!/bin/bash

# Get the current directory
CURRENT_DIR=$(pwd)

# Check if the 'venv' folder exists in the current directory
if [ -d "$CURRENT_DIR/venv" ]; then
  # Activate the virtual environment
  source "$CURRENT_DIR/venv/bin/activate"
  echo "Python3 environment activated from $CURRENT_DIR/venv"
else
  # If no virtual environment exists, create one
  echo "No virtual environment found. Creating one..."
  python -m venv "$CURRENT_DIR/venv"
  # Activate the new virtual environment
  source "$CURRENT_DIR/venv/bin/activate"
  echo "Python environment created and activated from $CURRENT_DIR/venv"
fi

# Force a prompt update by re-setting the prompt variable

