#!/usr/bin/env bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_PATH="$SCRIPT_DIR/../.env"

# Check for .env
if [ ! -f "$ENV_PATH" ]; then
  echo "No .env file found at $ENV_PATH"
  exit 1
fi

# Read each non-comment line from .env.
# For bash/zsh, we can use export directly
while read -r line; do
  # Skip empty lines and comments
  if [[ -n "$line" && ! "$line" =~ ^# ]]; then
    export "$line"
  fi
done < "$ENV_PATH"

echo "Environment variables from $ENV_PATH have been set"

# Note: This script must be sourced, not executed
# Usage: source ./setup.sh
