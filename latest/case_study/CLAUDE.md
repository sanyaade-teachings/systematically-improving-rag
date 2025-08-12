# Case Study: Systematically Improving RAG

## Project Overview

This case study demonstrates how to systematically identify and solve alignment problems in RAG (Retrieval-Augmented Generation) systems. Through concrete experiments with real data, we show how different query strategies lead to dramatically different retrieval performance, and how to bridge these gaps through intelligent system design.

## Goals and Objectives

### Primary Goals

1. **Demonstrate the Alignment Problem**: Show how misalignment between queries and embeddings causes RAG systems to fail
2. **Test Solutions Systematically**: Evaluate multiple approaches (summaries, full conversations) to solve alignment issues
3. **Provide Reproducible Results**: Create a framework others can use to diagnose and fix their own RAG systems
4. **Illustrate the Improvement Flywheel**: Show how synthetic data → evaluation → improvement creates better systems

### Key Learnings

- Why pattern-focused queries fail when searching content-focused embeddings (50% performance gap)
- How different summary techniques can bridge the alignment gap
- The power of iterative prompt engineering (achieving 358% improvement)
- Trade-offs between compute at ingestion time vs query time

## Quick Start Commands

### Initial Setup

```bash
# Install dependencies
uv pip install -e .

# Load conversations from WildChat dataset
uv run python main.py load-wildchat --limit 100  # Start small
uv run python main.py load-wildchat --limit 1000  # Full dataset

# Code quality checks
uv run ruff check --fix --unsafe-fixes .
uv run ruff format .
```

### Generate Synthetic Queries

```bash
# Generate v1 queries (content-focused: "What is X?")
uv run python main.py generate-questions --version v1 --limit 100

# Generate v2 queries (pattern-focused: "conversations about X")
uv run python main.py generate-questions --version v2 --limit 100
```

### Create Embeddings

```bash
# Embed conversation first messages
uv run python main.py embed-conversations --embedding-model text-embedding-3-small

# Embed summaries (after generating them)
uv run python main.py embed-summaries --technique v5 --embedding-model text-embedding-3-small
```

### Run Evaluations

```bash
# Evaluate v1 queries against conversations
uv run python main.py evaluate --question-version v1 --embedding-model text-embedding-3-small

# Evaluate v2 queries against conversations
uv run python main.py evaluate --question-version v2 --embedding-model text-embedding-3-small

# Evaluate with reranking
uv run python main.py evaluate --question-version v2 --embedding-model text-embedding-3-small --reranker cohere/rerank-english-v3.0 --reranker-n 60

# Evaluate against summaries with reranking
uv run python main.py evaluate --question-version v2 --embedding-model text-embedding-3-small --target-type summary --target-technique v4 --reranker cohere/rerank-english-v3.0 --reranker-n 60

# Check statistics
uv run python main.py stats
```

## Pipeline Commands (Recommended Workflow)

### Part 02: Discover the Alignment Problem

```bash
# Full pipeline for 100 conversations
uv run python pipelines/setup.py populate --limit 100
uv run python pipelines/generation.py questions --version v1 --limit 100
uv run python pipelines/generation.py questions --version v2 --limit 100
uv run python pipelines/indexing.py embed-conversations --embedding-model text-embedding-3-small
uv run python pipelines/evaluation.py evaluate --question-version v1 --embedding-model text-embedding-3-small --limit 100
uv run python pipelines/evaluation.py evaluate --question-version v2 --embedding-model text-embedding-3-small --limit 100
```

### Part 03: Test Summary Solutions

```bash
# Generate different summary types
uv run python pipelines/generation.py summarize --technique v1 --limit 100  # Search-optimized
uv run python pipelines/generation.py summarize --technique v3 --limit 100  # Balanced
uv run python pipelines/generation.py summarize --technique v4 --limit 100  # Pattern-optimized
uv run python pipelines/generation.py summarize --technique v5 --limit 100  # Hybrid (best)

# Embed and evaluate summaries
uv run python pipelines/indexing.py embed-summaries --technique v5 --embedding-model text-embedding-3-small
uv run python pipelines/evaluation.py evaluate-summary --question-version v2 --summary-version v5 --embedding-model text-embedding-3-small --limit 100
```

### Part 04: Test Reranking Solutions

```bash
# Baseline evaluation (no reranking)
uv run python main.py evaluate \
  --question-version v2 \
  --embedding-model text-embedding-3-small \
  --limit 100 \
  --experiment-id part4_100_baseline \
  --reranker none

# Cohere reranking with different candidate counts
uv run python main.py evaluate \
  --question-version v2 \
  --embedding-model text-embedding-3-small \
  --limit 100 \
  --experiment-id part4_100_cohere_60 \
  --reranker cohere/rerank-english-v3.0 \
  --reranker-n 60

uv run python main.py evaluate \
  --question-version v2 \
  --embedding-model text-embedding-3-small \
  --limit 100 \
  --experiment-id part4_100_cohere_100 \
  --reranker cohere/rerank-english-v3.0 \
  --reranker-n 100

# SentenceTransformers reranking comparison
uv run python main.py evaluate \
  --question-version v2 \
  --embedding-model text-embedding-3-small \
  --limit 100 \
  --experiment-id part4_100_st_60 \
  --reranker sentence-transformers/cross-encoder/ms-marco-MiniLM-L-6-v2 \
  --reranker-n 60

# Test reranking on aligned data (summaries)
uv run python main.py evaluate \
  --question-version v2 \
  --embedding-model text-embedding-3-small \
  --target-type summary \
  --target-technique v4 \
  --limit 100 \
  --experiment-id part4_100_summaries_cohere \
  --reranker cohere/rerank-english-v3.0 \
  --reranker-n 60
```

### v5 Optimization Workflow (Iterative Improvement)

```bash
# 1. Modify v5 prompt in core/summarization.py
# 2. Generate new summaries
uv run python pipelines/generation.py summarize --technique v5 --limit 100

# 3. Create embeddings
uv run python pipelines/indexing.py embed-summaries --technique v5 --embedding-model text-embedding-3-small

# 4. Evaluate performance
uv run python pipelines/evaluation.py evaluate-summary --question-version v2 --summary-version v5 --embedding-model text-embedding-3-small --limit 100
uv run python pipelines/evaluation.py evaluate-summary --question-version v1 --summary-version v5 --embedding-model text-embedding-3-small --limit 100

# 5. Check results quickly
echo "v2:"; cat data/results/eval_v2_summary_v5_text-embedding-3-small.json | jq '.metrics.recall_at_1'
echo "v1:"; cat data/results/eval_v1_summary_v5_text-embedding-3-small.json | jq '.metrics.recall_at_1'

# 6. Analyze failures
cat data/results/eval_v2_summary_v5_text-embedding-3-small.json | jq '.detailed_results[] | select(.found == false) | .query' | head -10
```

## Data Analysis Commands

### Check Database Status

```bash
# Summary counts by technique
sqlite3 data/rag_study.db "SELECT technique, COUNT(*) FROM summaries GROUP BY technique;"

# Question counts by version
sqlite3 data/rag_study.db "SELECT version, COUNT(*) FROM questions GROUP BY version;"

# Evaluation results summary
sqlite3 data/rag_study.db "SELECT question_version, embeddings_type, embedding_model, AVG(CASE WHEN rank = 1 THEN 1.0 ELSE 0.0 END) as recall_at_1 FROM evaluations WHERE found = 1 GROUP BY question_version, embeddings_type, embedding_model;"
```

### Analyze Failure Patterns

```bash
# Find consistently failing conversations
sqlite3 data/rag_study.db <<EOF
SELECT
  q.conversation_hash,
  COUNT(DISTINCT e.id) as failure_count,
  GROUP_CONCAT(DISTINCT q.text, ' | ') as failed_queries
FROM evaluations e
JOIN questions q ON e.question_id = q.id
WHERE e.found = 0
  AND e.embeddings_type = 'summaries'
  AND e.target_technique = 'v5'
GROUP BY q.conversation_hash
ORDER BY failure_count DESC
LIMIT 10;
EOF
```

### Quick Performance Matrix

```bash
# Create performance comparison
for v in v1 v3 v4 v5; do
  echo "=== $v summaries ==="
  echo -n "v1 queries: "
  cat data/results/eval_v1_summary_${v}_text-embedding-3-small.json 2>/dev/null | jq '.metrics.recall_at_1' || echo "N/A"
  echo -n "v2 queries: "
  cat data/results/eval_v2_summary_${v}_text-embedding-3-small.json 2>/dev/null | jq '.metrics.recall_at_1' || echo "N/A"
done
```

## Troubleshooting

### Clear ChromaDB Cache

```bash
# If embeddings seem stale or wrong
rm -rf data/embeddings/chromadb/
```

### Reset Database

```bash
# Start fresh (warning: deletes all data)
rm -rf data/
uv run python main.py load-wildchat --limit 100
```

### Check Embedding Status

```bash
# See what embeddings exist
ls -la data/embeddings/summaries/
ls -la data/embeddings/conversations/
```

## Key Files and Structure

```
case_study/
├── core/                      # Core functionality
│   ├── db.py                 # Database models and setup
│   ├── embeddings.py         # Embedding generation and storage
│   ├── evaluation.py         # Evaluation metrics and logic
│   ├── summarization.py      # Summary generation (v1-v5)
│   └── synthetic_queries.py  # Query generation (v1, v2)
├── pipelines/                 # High-level pipeline scripts
│   ├── setup.py              # Data loading and setup
│   ├── generation.py         # Generate queries and summaries
│   ├── indexing.py           # Create embeddings
│   └── evaluation.py         # Run evaluations
├── teaching/                  # Documentation and analysis
│   ├── part02/               # Alignment problem discovery
│   └── part03/               # Solutions and optimization
└── data/                      # Generated data (git-ignored)
    ├── rag_study.db          # SQLite database
    ├── results/              # JSON evaluation results
    └── embeddings/           # Vector embeddings
```

## Expected Results

### Part 02: The Alignment Problem

- **v1 queries**: ~55-62% Recall@1 (good performance)
- **v2 queries**: ~11-12% Recall@1 (terrible performance)
- **Gap**: 44-50% performance difference

### Part 03: Summary Solutions

- **v1 summaries**: 60.7% v1, 17.1% v2 (content-focused)
- **v3 summaries**: 61.9% v1, 21.0% v2 (balanced)
- **v4 summaries**: 45.7% v1, 24.9% v2 (pattern-focused)
- **v5 summaries**: 82.0% v1, 55.0% v2 (optimized hybrid - best!)

### Part 04: Reranking Solutions

- **Baseline (no reranking)**: 12.0% Recall@1, 41.0% Recall@30
- **Cohere + 60 docs**: 11.0% Recall@1, 48.0% Recall@30 (modest improvement)
- **Cohere + 100 docs**: 11.0% Recall@1, 50.0% Recall@30 (diminishing returns)
- **SentenceTransformers + 60 docs**: 9.0% Recall@1, 38.0% Recall@30 (worse than Cohere)
- **Key Insight**: Alignment (42.5% → 70.4%) beats reranking (70.4% → 70.6%) by 167x

## Tips for Claude Code Users

1. **Start Small**: Use `--limit 10` or `--limit 100` for quick iterations
2. **Use Pipelines**: Pipeline scripts handle the workflow better than individual commands
3. **Check Stats Often**: Run `uv run python main.py stats` to see current state
4. **Iterate on Prompts**: The v5 optimization shows how powerful iterative improvement can be
5. **Analyze Failures**: Failed queries teach more than successful ones

## Connection to Workshops

This case study demonstrates key concepts from the workshop series:

- **Chapter 0**: The improvement flywheel in action
- **Chapter 1**: Synthetic data for cold-start evaluation
- **Chapter 2**: Converting evaluation insights into improvements
- **Chapter 4**: Analyzing query patterns to identify opportunities

## Next Steps

1. **Try Different Embeddings**: Test with your preferred embedding models
2. **Modify Prompts**: Experiment with v5 prompt variations
3. **Add Your Data**: Replace WildChat with your domain-specific conversations
4. **Test HyDE**: Implement query-time optimization as an alternative
5. **Production Deploy**: Use these insights to improve your RAG system

## Remember: The goal isn't perfect recall, but understanding and solving alignment problems systematically.

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
