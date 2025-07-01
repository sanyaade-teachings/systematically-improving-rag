#!/bin/bash

# Script to convert Jupyter notebooks to markdown files
# - Converts all .ipynb files in /latest/ directory to .md files
# - Prefixes output files with week/directory name (e.g., week1_notebook.md)
# - Places converted files in /md/ directory
# - Ensures /md/ directory is git-ignored

set -e

echo "🔄 Starting notebook to markdown conversion..."
echo

# Check if nbconvert is installed
if ! python -c "import nbconvert" 2>/dev/null; then
    echo "Installing nbconvert..."
    uv add nbconvert
    echo "✓ nbconvert installed successfully"
else
    echo "✓ nbconvert is already installed"
fi
echo

# Clean up and create md directory
if [ -d "md" ]; then
    rm -rf md
    echo "✓ Cleaned up existing md directory"
fi
mkdir md
echo "✓ Created directory: $(pwd)/md"
echo

# Update .gitignore
if [ ! -f .gitignore ] || ! grep -q "^/md/$" .gitignore; then
    echo "# Converted markdown files" >> .gitignore
    echo "/md/" >> .gitignore
    echo "✓ Added /md/ directory to .gitignore"
else
    echo "✓ /md/ directory is already in .gitignore"
fi
echo

# Check if latest directory exists
if [ ! -d "latest" ]; then
    echo "✗ 'latest' directory not found"
    exit 1
fi

# Find notebooks
notebooks=$(find latest -name "*.ipynb" | wc -l)
echo "✓ Found $notebooks notebook(s) in latest/"

if [ "$notebooks" -eq 0 ]; then
    echo "No notebooks found to convert."
    exit 0
fi

echo
echo "Converting notebooks:"

successful=0
while IFS= read -r -d '' notebook; do
    echo "  Converting $notebook..."
    
    # Extract week/directory prefix from path
    week_dir=$(echo "$notebook" | cut -d'/' -f2)
    notebook_name=$(basename "$notebook" .ipynb)
    output_name="${week_dir}_${notebook_name}"
    
    if jupyter nbconvert --to markdown --output-dir md --output "$output_name" "$notebook" 2>/dev/null; then
        echo "  ✓ $notebook -> md/${output_name}.md"
        ((successful++))
    else
        echo "  ✗ Failed to convert $notebook"
    fi
done < <(find latest -name "*.ipynb" -print0)

echo
echo "✅ Conversion complete!"
echo "   $successful/$notebooks notebooks converted successfully"
echo "   Markdown files saved in: $(pwd)/md"
echo "   Directory is git-ignored" 