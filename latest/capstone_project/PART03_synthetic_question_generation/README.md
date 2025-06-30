# PART03: Synthetic Question Generation

Scripts that generate synthetic queries to evaluate RAG system performance.

## The Experiment

Two different query generation approaches demonstrate how prompt design dramatically affects retrieval performance:

- `generate_synthetic_questions_v1.py` - Generates queries as a product manager would (focusing on specific search terms)
- `generate_synthetic_questions_v2.py` - Generates queries as a research analyst would (focusing on conversation patterns)

## Key Insight

V1 achieves ~50% recall while V2 achieves ~2% recall. This massive difference reveals a critical alignment issue: our embeddings only include the first message of conversations (from PART02), so V1 queries that mimic first messages work well, while V2 queries that describe entire conversations fail.

## Other Files

- `dao.py` - Data access interface for different backends
- `prompts.py` - The prompt templates that make all the difference
- `utils.py` - Shared utilities for embedding and retrieval
- `search_app.py` - Streamlit UI for exploring the results
- `COMMENTARY.md` - Detailed analysis of why this happens

The scripts generate queries, test them against your vector database, and calculate recall@k metrics. Results are cached in SQLite for analysis.