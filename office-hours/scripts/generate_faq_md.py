#!/usr/bin/env python3
"""
Script to parse office hours markdown files and generate a comprehensive FAQ.md file.
Outputs: faq.md formatted as a standard docs page with proper navigation.
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict


def extract_frontmatter_and_content(file_content: str) -> tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and remaining content from markdown."""
    if not file_content.startswith('---'):
        return {}, file_content
    
    parts = file_content.split('---', 2)
    if len(parts) < 3:
        return {}, file_content
    
    try:
        frontmatter = yaml.safe_load(parts[1])
        content = parts[2].strip()
        return frontmatter or {}, content
    except yaml.YAMLError:
        return {}, file_content


def extract_questions_and_answers(content: str) -> List[Dict[str, str]]:
    """Extract question/answer pairs from markdown content."""
    # Split content by ## headings (questions)
    sections = re.split(r'\n## ', content)
    
    qa_pairs = []
    
    for i, section in enumerate(sections):
        if i == 0:
            # Skip the first section (usually intro text before first question)
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # First line is the question
        question = lines[0].strip()
        
        # Rest is the answer
        answer_lines = lines[1:]
        answer = '\n'.join(answer_lines).strip()
        
        # Extract key takeaway if present
        key_takeaway = ""
        takeaway_match = re.search(r'\*\*\*Key Takeaway:\*\*\*\s*(.*?)(?=\n\n|\n##|\Z)', answer, re.DOTALL)
        if takeaway_match:
            key_takeaway = takeaway_match.group(1).strip()
        
        qa_pairs.append({
            'question': question,
            'answer': answer,
            'key_takeaway': key_takeaway
        })
    
    return qa_pairs


def process_markdown_file(file_path: Path) -> List[Dict[str, Any]]:
    """Process a single markdown file and extract FAQ data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body = extract_frontmatter_and_content(content)
        
        # Extract metadata with defaults
        cohort = frontmatter.get('cohort', 0)
        week = frontmatter.get('week', 0)
        session = frontmatter.get('session', 1)
        title = frontmatter.get('title', f'Week {week}')
        
        # Handle session field that might be string or int
        if isinstance(session, str):
            # Extract number from session string like "1" or "Office Hour 1"
            session_match = re.search(r'(\d+)', session)
            session = int(session_match.group(1)) if session_match else 1
        
        qa_pairs = extract_questions_and_answers(body)
        
        # Add metadata to each Q&A pair
        result = []
        for qa in qa_pairs:
            result.append({
                'cohort': int(cohort),
                'week': int(week),
                'session': int(session),
                'title': title,
                'question': qa['question'],
                'answer': qa['answer'],
                'key_takeaway': qa['key_takeaway']
            })
        
        return result
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def generate_markdown_faq(all_faq_data: List[Dict[str, Any]]) -> str:
    """Generate a formatted markdown FAQ document."""
    
    # Start building the markdown
    md_content = """---
title: Frequently Asked Questions
description: Comprehensive FAQ compiled from all office hours sessions across cohorts
---

# Frequently Asked Questions

This comprehensive FAQ is compiled from all office hours sessions across multiple cohorts.

!!! tip "Quick Navigation"
    Use your browser's search (Ctrl+F) to find specific terms or questions, or browse through the questions below.

"""
    
    # Add all Q&A pairs as flat list
    for item in all_faq_data:
        question = item['question']
        answer = item['answer']
        key_takeaway = item['key_takeaway']
        
        # Clean up the question (remove any markdown artifacts)
        question = question.strip('# ').strip()
        
        md_content += f"## {question}\n\n"
        md_content += f"{answer}\n\n"
        
        # Add key takeaway if present
        if key_takeaway:
            md_content += f"!!! success \"Key Takeaway\"\n"
            md_content += f"    {key_takeaway}\n\n"
        
        md_content += "---\n\n"
    
    # Add footer
    md_content += """
## Additional Resources

- [Office Hours Overview](index.md)
- [Workshop Materials](../workshops/index.md)
- [Talks and Presentations](../talks/index.md)

## Contributing

Found an error or want to suggest improvements to these FAQs? The source files are located in the office hours documentation and can be regenerated using the `generate_faq_md.py` script.
"""
    
    return md_content


def main():
    """Main function to process all office hours files and generate FAQ.md."""
    script_dir = Path(__file__).parent
    office_hours_dir = script_dir.parent  # Go up one level to office-hours directory
    all_faq_data = []
    
    # Process cohort2 files
    cohort2_dir = office_hours_dir / 'cohort2'
    if cohort2_dir.exists():
        for md_file in cohort2_dir.glob('*.md'):
            print(f"Processing {md_file}")
            faq_data = process_markdown_file(md_file)
            all_faq_data.extend(faq_data)
    
    # Process cohort3 files
    cohort3_dir = office_hours_dir / 'cohort3'
    if cohort3_dir.exists():
        for md_file in cohort3_dir.glob('*.md'):
            print(f"Processing {md_file}")
            faq_data = process_markdown_file(md_file)
            all_faq_data.extend(faq_data)
    
    # Sort by cohort, week, session, then question order
    all_faq_data.sort(key=lambda x: (x['cohort'], x['week'], x['session']))
    
    # Generate markdown FAQ
    markdown_content = generate_markdown_faq(all_faq_data)
    
    # Save to FAQ.md
    output_file = office_hours_dir / 'faq.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"\nProcessed {len(all_faq_data)} Q&A pairs")
    print(f"Generated FAQ saved to {output_file}")
    
    # Print summary statistics
    cohorts = set(item['cohort'] for item in all_faq_data)
    for cohort in sorted(cohorts):
        cohort_data = [item for item in all_faq_data if item['cohort'] == cohort]
        weeks = set(item['week'] for item in cohort_data)
        print(f"Cohort {cohort}: {len(cohort_data)} Q&A pairs across {len(weeks)} weeks")


if __name__ == "__main__":
    main()
