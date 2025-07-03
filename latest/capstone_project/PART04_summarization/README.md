# PART04: Summarization for Improved RAG

The solution to the alignment problem: using conversation summaries to dramatically improve retrieval for pattern-based queries.

## Overview

This part demonstrates how to fix the alignment issue discovered in PART03. By generating and embedding conversation summaries instead of just first messages, we can dramatically improve retrieval performance for queries that describe conversation patterns.

## The Problem We're Solving

From PART03's experiment:
- **V1 queries** (direct questions) → ~50% recall ✅
- **V2 queries** (pattern descriptions) → ~2% recall ❌

The root cause: V2 queries search for patterns across entire conversations, but we only embedded first messages.


for v1 and v2 queries and first messages we get 

│    Rolling Metrics (after 800 queries)              │
│ ┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┓           │
│ ┃ Metric              ┃     v1 ┃     v2 ┃           │
│ ┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━┩           │
│ │ Total Queries       │    339 │    461 │           │
│ │ Successful Searches │    339 │    461 │           │
│ │ Recall@1            │ 31.86% │  1.74% │           │
│ │ Recall@5            │ 53.98% │  8.68% │           │
│ │ Recall@10           │ 61.06% │ 12.15% │           │
│ │ Recall@20           │ 67.55% │ 16.27% │           │
│ │ Recall@30           │ 70.50% │ 18.44% │           │
│ │ Not Found           │    100 │    376 │           │
│ │ Search Errors       │      0 │      0 │           │
│ └─────────────────────┴────────┴────────┘   

but if we use an llm to rewrite the conversation into a summary, we get:

    v1 Queries vs v1 Summary    
           Embeddings           
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total v1 Queries    │    424 │
│ Successful Searches │    380 │
│ Recall@1            │ 35.61% │
│ Recall@5            │ 60.14% │
│ Recall@10           │ 66.75% │
│ Recall@20           │ 71.46% │
│ Recall@30           │ 73.11% │
│ Not Found           │     70 │
│ Search Errors       │     44 │
└─────────────────────┴────────┘

    v2 Queries vs v1 Summary    
           Embeddings           
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric              ┃  Value ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total v2 Queries    │    287 │
│ Successful Searches │    287 │
│ Recall@1            │  6.62% │
│ Recall@5            │ 13.59% │
│ Recall@10           │ 16.72% │
│ Recall@20           │ 22.65% │
│ Recall@30           │ 25.09% │
│ Not Found           │    215 │
│ Search Errors       │      0 │
└─────────────────────┴────────┘

its not good, but its an improvement and now we can start hill climbing this eval! 
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
