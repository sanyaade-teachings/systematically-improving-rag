# PART04: Summarization for Improved RAG

Scripts that demonstrate how synthetic summarization can dramatically improve recall for pattern-based queries (V2) by aligning the embedding strategy with the query style.

## The Problem

From PART03, we learned:
- V1 queries (specific search terms) achieve ~50% recall
- V2 queries (pattern descriptions) achieve only ~2% recall
- The mismatch occurs because we only embed first messages, but V2 queries describe entire conversations

## The Solution

Generate conversation summaries that capture the full context, then embed these summaries instead of just first messages.

## Scripts

- `compute_summaries.py` - Generates summaries using two approaches:
  - **V1**: Concise, search-optimized summaries (2-3 sentences)
  - **V2**: Comprehensive pattern-focused summaries (4-6 sentences)

- `load_summaries_to_db.py` - Loads summaries into vector databases (ChromaDB, TurboPuffer)

- `compute_recall_with_summaries.py` - Tests V2 queries against summary embeddings to show improvement

## Key Files

- `src/summarization_prompts.py` - Two summarization strategies
- `src/db.py` - SQLite storage for summaries
- `src/cache.py` - Caching system (copied from PART03)
- `src/dataloader.py` - WildChat data loader (copied from PART03)

## Expected Results

When using summary embeddings:
- V2 queries should achieve 30-50% recall (up from ~2%)
- Demonstrates how aligning embedding strategy with query style is critical
- Shows trade-offs between different summarization approaches

## Running the Pipeline

1. Generate summaries:
   ```bash
   python compute_summaries.py --limit 500
   ```

2. Load summaries into vector DB:
   ```bash
   python load_summaries_to_db.py v2 --drop
   ```

3. Test recall with V2 queries:
   ```bash
   python compute_recall_with_summaries.py --summary-version v2
   ```

## Key Insight

The dramatic improvement in V2 recall demonstrates that the embedding strategy must match the query generation approach. When queries look for patterns across entire conversations, embeddings must capture that full context.
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
