#!/usr/bin/env python3
"""
Script to convert Jupyter notebooks to markdown files.
- Converts all .ipynb files in /latest/ directory to .md files
- Prefixes output files with week/directory name (e.g., week1_notebook.md)
- Places converted files in /md/ directory
- Ensures /md/ directory is git-ignored
"""

import sys
import subprocess
from pathlib import Path
import shutil


def ensure_nbconvert_installed():
    """Check if nbconvert is installed, install if not."""
    try:
        import nbconvert
        print("✓ nbconvert is already installed")
    except ImportError:
        print("Installing nbconvert...")
        try:
            subprocess.check_call(["uv", "add", "nbconvert"])
            print("✓ nbconvert installed successfully")
        except subprocess.CalledProcessError:
            print("✗ Failed to install nbconvert")
            sys.exit(1)


def clean_and_create_md_directory():
    """Clean up and create the /md directory."""
    md_dir = Path("md")
    
    # Remove entire directory if it exists to clean up all files and subdirectories
    if md_dir.exists():
        shutil.rmtree(md_dir)
        print("✓ Cleaned up existing md directory")
    
    md_dir.mkdir()
    print(f"✓ Created directory: {md_dir.absolute()}")
    return md_dir


def update_gitignore():
    """Add /md/ directory to .gitignore if not already present."""
    gitignore_path = Path(".gitignore")
    md_ignore_line = "/md/"
    
    existing_content = gitignore_path.read_text() if gitignore_path.exists() else ""
    
    if md_ignore_line in existing_content:
        print("✓ /md/ directory is already in .gitignore")
        return
    
    with gitignore_path.open("a") as f:
        if existing_content and not existing_content.endswith('\n'):
            f.write('\n')
        f.write(f"# Converted markdown files\n{md_ignore_line}\n")
    
    print("✓ Added /md/ directory to .gitignore")


def find_notebooks():
    """Find all Jupyter notebook files in the latest directory."""
    latest_dir = Path("latest")
    
    if not latest_dir.exists():
        print("✗ 'latest' directory not found")
        return []
    
    notebooks = list(latest_dir.rglob("*.ipynb"))
    print(f"✓ Found {len(notebooks)} notebook(s) in latest/")
    return notebooks


def get_output_filename(notebook_path):
    """Generate output filename with week/directory prefix."""
    path_parts = notebook_path.parts
    if len(path_parts) > 1 and path_parts[0] == "latest":
        prefix = path_parts[1]  # week1, week2, extra_kura, etc.
        return f"{prefix}_{notebook_path.stem}.md"
    return f"{notebook_path.stem}.md"


def convert_notebook_to_markdown(notebook_path, md_dir):
    """Convert a single notebook to markdown."""
    try:
        md_filename = get_output_filename(notebook_path)
        output_path = md_dir / md_filename
        
        cmd = [
            sys.executable, "-m", "nbconvert",
            "--to", "markdown",
            "--output-dir", str(md_dir),
            "--output", md_filename.replace(".md", ""),
            str(notebook_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  ✓ {notebook_path} -> {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to convert {notebook_path}: {e}")
        return False


def main():
    """Main function to orchestrate the conversion process."""
    print("🔄 Starting notebook to markdown conversion...\n")
    
    ensure_nbconvert_installed()
    print()
    
    md_dir = clean_and_create_md_directory()
    print()
    
    update_gitignore()
    print()
    
    notebooks = find_notebooks()
    if not notebooks:
        print("No notebooks found to convert.")
        return
    print()
    
    print("Converting notebooks:")
    successful_conversions = sum(
        convert_notebook_to_markdown(notebook, md_dir) 
        for notebook in notebooks
    )
    
    print(f"\n✅ Conversion complete!")
    print(f"   {successful_conversions}/{len(notebooks)} notebooks converted successfully")
    print(f"   Markdown files saved in: {md_dir.absolute()}")
    print(f"   Directory is git-ignored")


if __name__ == "__main__":
    main() 