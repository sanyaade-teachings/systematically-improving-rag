#!/usr/bin/env python3
"""
Script to remove all instances of the subscription script from markdown files.
"""

import os
import re
from pathlib import Path

def remove_subscription_script(file_path):
    """Remove the subscription script pattern from a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the subscription script section
        # This matches the pattern: ---\n\nIF you want to get discounts...\n\n<script...>\n
        pattern = r'\n---\n\nIF you want to get discounts and 6 day email source on the topic make sure to subscribe to\n\n<script async data-uid="010fd9b52b" src="https://fivesixseven\.kit\.com/010fd9b52b/index\.js"></script>\n'
        
        # Remove the pattern
        new_content = re.sub(pattern, '', content)
        
        # If content changed, write it back
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all markdown files."""
    # Find all markdown files
    markdown_files = list(Path('.').rglob('*.md'))
    
    print(f"Found {len(markdown_files)} markdown files")
    
    modified_count = 0
    for file_path in markdown_files:
        if remove_subscription_script(file_path):
            print(f"Modified: {file_path}")
            modified_count += 1
    
    print(f"\nTotal files modified: {modified_count}")

if __name__ == "__main__":
    main() 