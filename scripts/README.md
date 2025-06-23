# Email Processing Scripts

This directory contains tools for managing email signups between Maven talks. The system uses a SQLite database to track emails and processing status, with comprehensive dry-run capabilities for safe testing.

## Overview

The workflow consists of two main scripts:
1. **prepare-email-sync.ts** - Analyzes CSV exports from Maven and identifies emails to sync
2. **stagehand.ts** - Processes the emails using browser automation

## Key Features

- **Auto-detection of CSV files** - No need to specify file paths
- **Complete signup tracking** - All signups are saved to database for history
- **Automatic deduplication** - Prevents duplicate email-URL pairs
- **Duplicate sync group prevention** - Can't create the same talk pair twice

## Quick Start

```bash
# 1. Export CSV from Maven to Downloads folder
# 2. Run prepare-sync (auto-detects latest CSV)
npm run prepare-sync

# 3. Select two talks to sync
# 4. Test processing (DRY RUN)
npm run stagehand -- --dry-run --test

# 5. Process emails (REAL)
npm run stagehand
```

## Prepare Email Sync Tool

This tool analyzes Maven CSV exports to identify which emails should be signed up for related talks.

### Features
- **CSV Auto-detection** - Automatically finds Maven CSV files in Downloads folder
- **Signup tracking** - Imports all signups to database for complete history
- Interactive talk selection
- Email overlap analysis  
- Dry-run mode for safety
- Sample email preview
- Duplicate prevention at all levels

### Usage

```bash
# Auto-detect CSV (recommended - finds latest file in Downloads)
npm run prepare-sync

# Auto-detect with dry run
npm run prepare-sync -- --dry-run

# Auto-detect with sample preview
npm run prepare-sync -- --show-sample 20

# Manual CSV path (if needed)
npm run prepare-sync -- path/to/export.csv

# Combine options
npm run prepare-sync -- --dry-run --show-sample 10
```

### Options
- `--dry-run` - Simulate without saving to database
- `--show-sample <n>` - Preview n sample emails (default: 10)
- No path argument - Auto-detects CSV files from Downloads folder

### Auto-detection
The tool searches for files matching `*lightning_lesson_signups*.csv` in your Downloads folder and:
- Shows files sorted by most recent modification date
- Displays previously imported files
- Allows manual path entry if needed

## Stagehand Email Processor

Processes emails from the database using browser automation.

### Features
- Database-driven processing
- Dry-run mode for testing
- Resume capability
- Sync group filtering
- Comprehensive error tracking

### Usage

```bash
# Process all pending emails (DRY RUN)
npm run stagehand -- --dry-run

# Process with limit (DRY RUN)
npm run stagehand -- --dry-run --limit 10

# Process specific sync group
npm run stagehand -- --sync-group=1

# Real processing
npm run stagehand

# Reset database
npm run stagehand -- --reset-db
```

### Options
- `--dry-run` - Test without submitting forms
- `--test` - Process only 3 emails
- `--limit <n>` - Process n emails
- `--sync-group=<id>` - Process specific sync group
- `--reset-db` - Clear all records

### Environment Variables
```bash
DRY_RUN=true npm run stagehand
LIMIT=25 npm run stagehand
DELAY_MS=3000 npm run stagehand
```

## Database Schema

The system uses SQLite with three main tables:

```sql
-- Signups table (tracks all imports)
CREATE TABLE signups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  talk_title TEXT NOT NULL,
  talk_url TEXT NOT NULL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL,
  imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  csv_filename TEXT,
  UNIQUE(email, talk_url)  -- Prevents duplicate email-URL pairs
);

-- Sync groups table
CREATE TABLE sync_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  talk1_title TEXT NOT NULL,
  talk1_url TEXT NOT NULL,
  talk2_title TEXT NOT NULL,
  talk2_url TEXT NOT NULL,
  overlap_count INTEGER,
  missing_from_talk1 INTEGER,
  missing_from_talk2 INTEGER,
  status TEXT DEFAULT 'pending'
);

-- Processed emails table
CREATE TABLE processed_emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  maven_url TEXT NOT NULL,
  talk_title TEXT NOT NULL,
  processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  success BOOLEAN NOT NULL,
  error_message TEXT,
  dry_run BOOLEAN DEFAULT FALSE,
  sync_group_id INTEGER,
  UNIQUE(email, maven_url),
  FOREIGN KEY (sync_group_id) REFERENCES sync_groups(id)
);
```

### Key Features
- **Automatic deduplication** - UNIQUE constraints prevent duplicate email-URL pairs
- **Complete history** - All signups are tracked in signups table
- **Sync tracking** - Processed emails are linked to sync groups

## Safe Testing Workflow

1. **Analyze with dry run**
   ```bash
   npm run prepare-sync -- --dry-run --show-sample 20 export.csv
   ```

2. **Create sync group**
   ```bash
   npm run prepare-sync -- export.csv
   ```

3. **Test with dry run**
   ```bash
   npm run stagehand -- --dry-run --limit 5
   ```

4. **Process small batch**
   ```bash
   npm run stagehand -- --limit 10
   ```

5. **Process remaining**
   ```bash
   npm run stagehand
   ```

## Export Talks Tool

Export all signups grouped by talk into individual CSV files.

### Usage

```bash
# Export all talks to /data/ directory
npm run export-talks
```

This will:
- Create a `/data/` directory in the project root
- Export one CSV file per talk with slugified filenames
- Each CSV contains: email, talk_title, talk_url, source, created_at, imported_at

Example output files:
- `data/rag-in-the-age-of-agents-swe-bench-as-a-case-study.csv`
- `data/lessons-on-retrieval-for-autonomous-coding-agents.csv`

## Troubleshooting

- **Resume after failure**: Just run the command again - processed emails are tracked
- **Check database stats**: `npm run stagehand -- --dry-run --limit 0`
- **Clear and start over**: `npm run stagehand -- --reset-db`
- **Database location**: `scripts/email_processing.db`

## Files

- `prepare-email-sync.ts` - CLI tool for analyzing CSV and creating sync groups
- `stagehand.ts` - Browser automation for processing emails
- `export-talks.ts` - Export signups grouped by talk to CSV files
- `lib/database.ts` - Shared database module and types
- `lib/utils.ts` - Common utility functions (slugify, logger, etc.)
- `email_processing.db` - SQLite database (created automatically)
- `/data/` - Directory containing exported CSV files (git-ignored)

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
