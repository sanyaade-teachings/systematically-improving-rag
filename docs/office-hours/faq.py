#!/usr/bin/env python3
"""
Script to parse office hours markdown files and extract structured FAQ data.
Outputs: faq.yaml with question/answer pairs and metadata.
"""

import os
import json
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


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
                'question': qa['question'],
                'answer': qa['answer'],
                'key_takeaway': qa['key_takeaway']
            })
        
        return result
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []


def main():
    """Main function to process all office hours files."""
    script_dir = Path(__file__).parent
    all_faq_data = []
    
    # Process cohort2 files
    cohort2_dir = script_dir / 'cohort2'
    if cohort2_dir.exists():
        for md_file in cohort2_dir.glob('*.md'):
            print(f"Processing {md_file}")
            faq_data = process_markdown_file(md_file)
            all_faq_data.extend(faq_data)
    
    # Process cohort3 files
    cohort3_dir = script_dir / 'cohort3'
    if cohort3_dir.exists():
        for md_file in cohort3_dir.glob('*.md'):
            print(f"Processing {md_file}")
            faq_data = process_markdown_file(md_file)
            all_faq_data.extend(faq_data)
    
    # Sort by cohort, week, session, then question order
    all_faq_data.sort(key=lambda x: (x['cohort'], x['week'], x['session']))
    
    # Save to YAML
    output_file = script_dir / 'faq.yaml'
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(all_faq_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\nProcessed {len(all_faq_data)} Q&A pairs")
    print(f"Saved to {output_file}")
    
    # Print summary statistics
    cohorts = set(item['cohort'] for item in all_faq_data)
    for cohort in sorted(cohorts):
        cohort_data = [item for item in all_faq_data if item['cohort'] == cohort]
        weeks = set(item['week'] for item in cohort_data)
        print(f"Cohort {cohort}: {len(cohort_data)} Q&A pairs across {len(weeks)} weeks")


if __name__ == "__main__":
    main()
