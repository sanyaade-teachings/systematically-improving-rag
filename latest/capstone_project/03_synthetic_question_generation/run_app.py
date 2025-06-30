#!/usr/bin/env python3
"""
Simple script to run the Streamlit app for synthetic question generation
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Set up environment
    current_dir = Path(__file__).parent
    app_path = current_dir / "streamlit_app.py"
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable is not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        print("The app will still run but won't be able to generate questions.\n")
    
    # Run Streamlit
    try:
        print(f"🚀 Starting Streamlit app...")
        print(f"📁 App location: {app_path}")
        print("🌐 The app will open in your browser automatically")
        print("🛑 Press Ctrl+C to stop the app\n")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.headless", "false",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n👋 Stopping the app...")
    except Exception as e:
        print(f"❌ Error running the app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 