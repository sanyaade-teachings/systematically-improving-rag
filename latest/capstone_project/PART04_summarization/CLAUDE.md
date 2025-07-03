# Systematically Improving RAG - Summarization Experiments

## Project Overview

This project demonstrates systematic improvements in retrieval-augmented generation (RAG) through iterative refinement of query generation and summarization strategies. The experiments achieved a 3x improvement in recall performance by addressing the fundamental challenge of matching user queries to relevant documents.

## Getting Started

### Step 1: Load Data into Vector Databases

```bash
# From the capstone_project directory

# Load conversation data into TurboPuffer (default: 10k conversations)
uv run python PART02_loading_data_into_db/load_to_turbopuffer.py load \
  --namespace-name wildchat_10k \
  --limit 10000 \
  --batch-size 50 \
  --language English \
  --min-length 30 \
  --reset

# Alternative: Load into ChromaDB
uv run python PART02_loading_data_into_db/load_to_chromadb.py main \
  --cloud \
  --collection-name wildchat-10k \
  --limit 10000 \
  --batch-size 25 \
  --language English \
  --min-length 30 \
  --reset
```

### Step 2: Generate Synthetic Questions

```bash
# Generate synthetic queries using different strategies
# V1: Content-focused queries
uv run python PART03_synthetic_question_generation/compute_synth_questions.py run \
  --limit 500 \
  --query-version v1 \
  --concurrency 50

# V2: Pattern-based queries  
uv run python PART03_synthetic_question_generation/compute_synth_questions.py run \
  --limit 500 \
  --query-version v2 \
  --concurrency 50

# V3: Specific pattern queries with satisfaction signals
uv run python PART03_synthetic_question_generation/compute_synth_questions.py run \
  --limit 500 \
  --query-version v3 \
  --concurrency 50

# Compute recall metrics for baseline queries
uv run python PART03_synthetic_question_generation/compute_recall.py run \
  --query-version v2 \
  --backend turbopuffer \
  --search-type vector
```

### Step 3: Generate and Load Summaries

```bash
# Generate summaries with different strategies (V1-V5)
uv run python PART04_summarization/compute_summaries.py run \
  --limit 10000 \
  --concurrency 50 \
  --version both  # or v1, v2, v3, v4, v5

# Load summaries into TurboPuffer
uv run python PART04_summarization/load_summaries_to_turbopuffer.py load \
  --prefix wildchat-synthetic-summaries \
  --version v4 \
  --batch-size 50 \
  --reset

# Or load into ChromaDB
uv run python PART04_summarization/load_summaries_to_chromadb.py load \
  --prefix wildchat-synthetic-summaries \
  --version v4 \
  --batch-size 50 \
  --reset \
  --local  # Add for local ChromaDB

# Compute recall with summarized documents
uv run python PART04_summarization/compute_recall_with_summaries.py run \
  --query-version v2 \
  --summary-version v4 \
  --no-cache  # For fresh results

# Analyze failure patterns
uv run python PART04_summarization/analyze_failures.py analyze \
  --query-version v2 \
  --summary-version v4
```

## Key Findings

### 1. Query Generation Evolution

#### V1 - Content-Focused Queries (66.75% Recall@10)

- Direct, keyword-heavy queries mimicking natural search behavior
- Example: "How to build a REST API with Node.js and Express"
- Best for known-item search

#### V2 - Pattern-Based Queries (15.57% Recall@10)

- Abstract, categorical queries for finding conversation types
- Example: "conversations involving role-playing with fictional characters"
- Too generic for precise retrieval in large datasets

#### V3 - Specific Pattern Queries (62.95% Recall@10)

- Combines patterns with specific details and satisfaction signals
- Example: "frustrated user Docker PostgreSQL connection refused error"
- 274% improvement in Recall@1 over V2

### 2. Summarization Strategy Evolution

- **V1**: Concise 2-3 sentence summaries with keywords
- **V2/V3**: Comprehensive 22-point analysis framework  
- **V4**: Pattern-optimized summaries aligned with query patterns

### 3. Critical Discovery: The Specificity Problem

V2 queries weren't failing - they were finding topically relevant content, just not the specific target. In a dataset with hundreds of similar conversations, generic patterns were insufficient.

### 4. Key Insights

1. **Query-Summary Alignment is Critical**: Mismatched strategies yield poor results
2. **Satisfaction Signals Matter**: "frustrated", "successfully", "satisfied" provide crucial context
3. **Multiple Strategies Needed**: Different query types serve different search purposes
4. **Iterative Refinement Works**: Each experiment informed the next

## Performance Results

| Query Version | Recall@1 | Recall@5 | Recall@10 | Recall@30 |
|---------------|----------|----------|-----------|-----------|
| V2            | 7.67%    | 16.34%   | 21.64%    | 30.45%    |
| V3            | 28.69%   | 53.20%   | 62.95%    | 71.87%    |
| **Improvement** | **+274%** | **+226%** | **+191%** | **+136%** |

## Future Vision: Analysis Agent

The ultimate goal is building an automated analysis agent that can:
- Detect failure patterns in AI conversations
- Analyze usage patterns for successful interactions
- Discover edge cases and recovery patterns
- Generate hypotheses for continuous improvement

## Technical Details

- **Dataset**: WildChat (11,000+ conversations)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Database**: TurboPuffer
- **Query Generation**: GPT-4.1-nano
- **Evaluation**: Recall@K metrics with exact conversation matching

## Lessons for RAG Implementation

1. Start with baseline measurements
2. Analyze failures systematically
3. Test hypotheses iteratively
4. Align query and document representations
5. Include user satisfaction signals in retrieval
6. Balance specificity with coverage

This work demonstrates that systematic experimentation and failure analysis can lead to substantial improvements in RAG system performance.

## Running the Full Pipeline

```bash
# From the capstone_project directory
# 1. Install dependencies
uv pip install -e .

# 2. Load initial data (10k conversations)
uv run python PART02_loading_data_into_db/load_to_turbopuffer.py load --reset

# 3. Generate synthetic queries (all versions)
uv run python PART03_synthetic_question_generation/compute_synth_questions.py run --query-version v1
uv run python PART03_synthetic_question_generation/compute_synth_questions.py run --query-version v2
uv run python PART03_synthetic_question_generation/compute_synth_questions.py run --query-version v3

# 4. Test baseline recall
uv run python PART03_synthetic_question_generation/compute_recall.py run --query-version v1
uv run python PART03_synthetic_question_generation/compute_recall.py run --query-version v2

# 5. Generate summaries (all versions)
uv run python PART04_summarization/compute_summaries.py run --version v1
uv run python PART04_summarization/compute_summaries.py run --version v2
uv run python PART04_summarization/compute_summaries.py run --version v3
uv run python PART04_summarization/compute_summaries.py run --version v4

# 6. Load best performing summaries (V4)
uv run python PART04_summarization/load_summaries_to_turbopuffer.py load --version v4 --reset

# 7. Test recall with summaries
uv run python PART04_summarization/compute_recall_with_summaries.py run --query-version v2 --summary-version v4
uv run python PART04_summarization/compute_recall_with_summaries.py run --query-version v3 --summary-version v4

# 8. Analyze failure patterns
uv run python PART04_summarization/analyze_failures.py analyze --query-version v3 --summary-version v4

# 9. Interactive search interface
uv run python PART03_synthetic_question_generation/search_app.py
```

## Environment Variables

Set these before running:

```bash
export OPENAI_API_KEY="your-openai-key"
export TURBOPUFFER_API_KEY="your-turbopuffer-key"
export CHROMA_API_KEY="your-chroma-key"  # If using ChromaDB cloud
```
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
