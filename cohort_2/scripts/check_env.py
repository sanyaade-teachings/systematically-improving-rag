#!/usr/bin/env python3
import os
import sys

# Check if required API keys are set
required_keys = ["OPENAI_API_KEY", "BRAINTRUST_API_KEY", "COHERE_API_KEY", "HF_TOKEN"]
missing_vars = [key for key in required_keys if not os.environ.get(key)]

if missing_vars:
    print("Missing environment variables:")
    for var in missing_vars:
        print(f"  - {var}")
    print("\nSet these with:")
    print("  export VARIABLE_NAME=value  # bash/zsh")
    print("  set -x VARIABLE_NAME value  # fish")
    sys.exit(1)

print("All required API keys are set.")
