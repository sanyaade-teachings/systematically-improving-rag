#!/usr/bin/env python3
"""
Simple script to format markdown files in the project.
Usage:
    python format_docs.py          # Format all markdown files
    python format_docs.py --check  # Check if files need formatting
"""
import subprocess
import sys
from pathlib import Path

def main():
    check_mode = "--check" in sys.argv
    
    # Find all markdown files in docs/ and root
    markdown_files = []
    docs_path = Path("docs")
    root_path = Path(".")
    
    if docs_path.exists():
        markdown_files.extend(docs_path.rglob("*.md"))
    
    # Add root level markdown files
    markdown_files.extend(root_path.glob("*.md"))
    
    if not markdown_files:
        print("No markdown files found")
        return
    
    cmd = ["uv", "run", "mdformat"]
    if check_mode:
        cmd.append("--check")
    
    cmd.extend(str(f) for f in markdown_files)
    
    print(f"{'Checking' if check_mode else 'Formatting'} {len(markdown_files)} markdown files...")
    result = subprocess.run(cmd)
    
    if check_mode and result.returncode != 0:
        print("Some files need formatting. Run without --check to format them.")
    elif not check_mode:
        print("Formatting complete!")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main() 