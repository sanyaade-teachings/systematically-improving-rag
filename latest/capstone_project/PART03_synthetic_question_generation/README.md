# PART03: Synthetic Question Generation

A critical experiment demonstrating how query generation strategy must align with embedding strategy for effective RAG systems.

## Overview

This part reveals a fundamental principle of RAG systems through a controlled experiment: **the way you generate queries must match what you've actually embedded**. We demonstrate this by comparing two different approaches to generating synthetic test queries.

## The Experiment

### Two Query Generation Strategies

1. **V1: Product Manager Approach** (`compute_synth_questions.py --prompt-version v1`)
   - Generates queries that mimic how users might search
   - Focuses on specific terms and direct questions
   - Example: "How do I set up authentication in Next.js?"

2. **V2: Research Analyst Approach** (`compute_synth_questions.py --prompt-version v2`)
   - Generates queries that describe conversation patterns
   - Focuses on themes and discussion topics
   - Example: "Find conversations about debugging authentication issues"

### Shocking Results

- **V1 Performance**: ~50% recall@5
- **V2 Performance**: ~2% recall@5

This 25x difference in performance reveals a critical insight!

## Key Insight: The Alignment Problem

The dramatic performance gap occurs because:

1. **What We Embedded**: Only the first message of each conversation (from PART02)
2. **What V1 Queries**: Direct questions similar to first messages
3. **What V2 Queries**: Descriptions of entire conversation patterns

V1 succeeds because its queries align with what's actually in the vector database. V2 fails because it's searching for patterns that aren't captured in our embeddings.

## Scripts and Components

### Core Scripts

- `compute_synth_questions.py` - Generates synthetic queries using both strategies
- `compute_recall.py` - Evaluates retrieval performance for generated queries
- `search_app.py` - Streamlit UI for interactive exploration

### Supporting Files

- `src/generation_prompts.py` - The two prompt strategies that make all the difference
- `src/db.py` - SQLite storage for queries and results
- `src/cache.py` - Caching system for API calls
- `src/dataloader.py` - WildChat data loading utilities
- `notebooks/review_examples.ipynb` - Analyze generated examples

### Additional Documentation

- `COMMENTARY.md` - Deep dive into why this happens and what it means

## Usage

### Generate Synthetic Queries

```bash
# Generate V1 queries (product manager style)
python compute_synth_questions.py --prompt-version v1 --limit 100

# Generate V2 queries (research analyst style)  
python compute_synth_questions.py --prompt-version v2 --limit 100
```

### Evaluate Performance

```bash
# Test V1 queries
python compute_recall.py --query-version v1

# Test V2 queries
python compute_recall.py --query-version v2
```

### Explore Results

```bash
# Launch interactive UI
streamlit run search_app.py
```

## Configuration

Set environment variables:
```bash
# Required
export OPENAI_API_KEY="your-key"

# Optional (depending on vector DB)
export TURBOPUFFER_API_KEY="your-key"
```

## What This Teaches Us

### 1. Alignment is Everything
Your query generation strategy must match your embedding strategy. If they're misaligned, even the best vector database won't help.

### 2. Test with Realistic Queries
Synthetic queries should mimic how real users will search. V1 works because it generates queries similar to actual user messages.

### 3. Understand Your Embeddings
Know exactly what you're embedding. Our simplified approach (first message only) creates clear limitations.

### 4. Prompt Engineering Matters
The difference between V1 and V2 is just the prompt template, yet it causes a 25x performance difference.

## Lessons for Production RAG

1. **Design queries and embeddings together** - They're two sides of the same coin
2. **Test with multiple query styles** - Different users search differently  
3. **Monitor alignment in production** - Track which query types succeed/fail
4. **Consider hybrid approaches** - Maybe you need multiple embedding strategies

## Next Steps

After understanding the alignment problem, proceed to:
- **PART04**: Learn how summarization can fix the alignment issue for V2 queries
- **Review the notebook**: See specific examples of generated queries
- **Read COMMENTARY.md**: Deeper analysis of the experimental results

This experiment demonstrates that RAG success isn't just about having good embeddings or smart queries - it's about ensuring they work together.

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
