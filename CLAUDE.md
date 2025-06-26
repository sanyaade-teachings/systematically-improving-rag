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

1. **Email Sync Preparation Tool** (`prepare-email-sync.ts`): Interactive CLI for analyzing Maven CSV exports
   - **Auto-detects CSV files** in Downloads folder (sorted by most recent)
   - Imports all signups to a tracking table (deduplicates automatically)
   - Interactive selection of talk pairs for syncing
   - Shows email overlap analysis between talks
   - Creates sync groups in SQLite database
   - Features:
     - CSV auto-detection (no need to specify path)
     - Dry-run mode for testing
     - Sample email preview
     - Duplicate talk pair prevention
     - Complete signup history tracking
     - **Filters out already successfully processed emails** from sync groups
   - Commands:
     ```bash
     npm run prepare-sync                        # Auto-detect CSV from Downloads
     npm run prepare-sync -- --dry-run           # Dry run with auto-detection
     npm run prepare-sync -- --show-sample 20    # Preview 20 sample emails
     npm run prepare-sync -- path/to/export.csv  # Specify CSV manually
     ```

2. **Stagehand Script** (`stagehand.ts`): Browser automation for email signups
   - Uses Playwright-based automation via @browserbasehq/stagehand
   - SQLite database (`email_processing.db`) for tracking all data
   - Processes emails from sync groups created by prepare-sync
   - Features:
     - Dry-run mode for testing without submissions
     - Resume capability (skips already processed emails)
     - Sync group filtering
     - Configurable limits and delays
     - Database tracking with success/failure status
     - **Multiple safety mechanisms to prevent duplicate emails**:
       - Automatic deduplication on startup (removes duplicate records)
       - Random shuffling of processing order
       - Cross-table statistics showing parsed/unparsed counts
       - Warning when many emails are pending (possible failures)
       - Shows sample of emails before processing
     - **Enhanced logging** with color-coded status updates:
       - ✅ Green for successful submissions (marked as SUCCESS)
       - ❌ Red for failed submissions (marked as FAILED)
       - ⏭️ Yellow for skipped emails (already processed)
     - **Comprehensive statistics** at startup:
       - Signups table: total, processed, unprocessed
       - Processed emails: successful, failed, pending
       - Cross-reference between tables
     - Final summary shows counts for each status
   - Commands:
     ```bash
     npm run stagehand -- --dry-run --test  # Test with 3 emails
     npm run stagehand -- --limit 10        # Process 10 emails
     npm run stagehand -- --sync-group=1    # Process specific sync group
     npm run stagehand                      # Process all pending emails
     npm run stagehand -- --reset-db        # Clear database
     ```

3. **Export Talks Tool** (`export-talks.ts`): Export signups grouped by talk
   - Exports all signups to individual CSV files in `/data/` directory
   - One CSV per talk with slugified filename
   - Commands:
     ```bash
     npm run export-talks  # Export all talks to CSV files
     ```

4. **Database Schema** (`email_processing.db`):
   - `signups` table: Tracks all signups from CSV imports (unique email-URL pairs)
   - `sync_groups` table: Stores talk pairs selected for syncing
   - `processed_emails` table: Tracks email processing status
   - Automatic deduplication at every level

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
