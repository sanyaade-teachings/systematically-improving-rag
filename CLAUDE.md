# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a hybrid Python/TypeScript project focused on documenting RAG (Retrieval-Augmented Generation) applications. The main component is a MkDocs-based documentation site with additional TypeScript scripts for automation.

## Setup and Build Commands

### Python/Documentation (Primary)
```bash
# Install dependencies (using uv as preferred)
uv pip install -e .
# Alternative: pip install -r requirements.txt

# Build documentation
mkdocs build

# Serve locally with hot-reload (port 8000)
mkdocs serve

# Format markdown files
mdformat docs/

# Lint Python code
ruff check .
ruff format .
```

### TypeScript/Scripts
```bash
# Install dependencies
bun install

# Run main script
bun run index.ts

# Run Stagehand email automation
npm run stagehand
# With options: npm run stagehand -- --dry-run --test
```

## High-Level Architecture

### Documentation System (Core)
The project is primarily a comprehensive learning resource about building production RAG systems, structured as:

- **Workshops** (`/docs/workshops/`): 6-chapter course covering RAG implementation from evaluation to multimodal approaches
- **Office Hours** (`/docs/office-hours/`): Session summaries from cohorts, containing Q&A and practical insights
- **Talks** (`/docs/talks/`): Conference presentation summaries on RAG patterns and best practices
- **Resources** (`/docs/misc/`): Learning goals, key takeaways, and supplementary materials

The documentation uses MkDocs with Material theme, featuring:
- Mermaid diagram support
- Code syntax highlighting with copy buttons
- Admonitions for notes/warnings
- Math rendering with MathJax
- Google Analytics integration

### Automation Scripts (`/scripts/`)
The scripts directory contains tools for processing Maven talk signup data:

1. **Email Analysis Notebook** (`email_scripts.ipynb`): Jupyter notebook for analyzing email signups
   - Reads CSV export from Maven (talk signups)
   - Identifies email overlap between different talks
   - Generates `missing_emails.jsonl` with emails that should be signed up for related talks

2. **Stagehand Script** (`stagehand.ts`): Browser automation for email signups
   - Uses Playwright-based automation via @browserbasehq/stagehand
   - SQLite database (`email_processing.db`) for tracking processed emails
   - Processes emails from `missing_emails.jsonl`
   - Features:
     - Dry-run mode for testing without submissions
     - Resume capability (skips already processed emails)
     - Configurable limits and delays
     - Database tracking with success/failure status
   - Commands:
     ```bash
     npm run stagehand -- --dry-run --test  # Test with 3 emails
     npm run stagehand -- --limit 10        # Process 10 emails
     npm run stagehand                      # Process all emails
     npm run stagehand -- --reset-db        # Clear database
     ```

## Project Structure

- `/docs/` - All documentation content
- `/scripts/` - TypeScript automation scripts
- `/site/` - Generated static site (git-ignored)
- `mkdocs.yml` - Complete MkDocs configuration
- `pyproject.toml` - Python dependencies and tooling
- `package.json` - TypeScript/JavaScript dependencies
- `tsconfig.json` - TypeScript compiler configuration

## Documentation Style Guidelines

- Use Markdown for all documentation files
- Follow Material theme conventions for admonitions and extensions
- Use descriptive filenames in kebab-case (e.g., `learning-goals.md`)
- Organize content hierarchically with proper headings (h1, h2, h3)
- Include code examples with appropriate syntax highlighting
- Keep sentences and paragraphs concise and focused
- Use relative links for internal documentation references

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
