# RAG Documentation & Maven Email Sync Tools

This project contains comprehensive documentation about building production RAG systems, along with automation tools for managing Maven talk signups.

## Documentation Site

To build and serve the MkDocs documentation:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Serve documentation locally
mkdocs serve

# Build static site
mkdocs build
```

## Email Sync Tools

### Quick Start

```bash
# Install dependencies
npm install

# Prepare email sync (auto-detects CSV files)
npm run sync

# Process emails with Stagehand
npm run stagehand

# Export talks to CSV
npm run export-talks
```

### Features

- **Auto-detection** of Maven CSV exports from Downloads folder
- **Database tracking** prevents duplicate email submissions
- **Random shuffling** to minimize accidental duplicates
- **Color-coded logging** for clear status updates:
  - ✅ Successfully processed emails
  - ❌ Failed submissions
  - ⏭️ Skipped (already processed)
- **Safety mechanisms** at multiple levels

### Commands

```bash
# Email sync preparation
npm run sync                        # Auto-detect CSV
npm run sync -- --dry-run           # Test without saving
npm run sync -- --show-sample 20    # Preview 20 emails

# Stagehand processing
npm run stagehand                   # Process all pending
npm run stagehand -- --dry-run      # Test mode
npm run stagehand -- --limit 10     # Process 10 emails
npm run stagehand -- --sync-group=1 # Specific sync group

# Export to CSV
npm run export-talks                # Export all talks
```

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
