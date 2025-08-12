# RAG Evaluation Summary: 1000 Conversations

## Executive Summary

We evaluated 3 embedding models on 1000 conversations from the WildChat dataset, demonstrating a severe alignment problem between query types and embedding strategies. V1 queries (content-focused) achieve 54-62% Recall@1, while V2 queries (pattern-focused) only achieve 11-12% Recall@1 - a 42-50% performance gap.

## Experimental Setup

- **Dataset**: 995 unique conversations (some duplicates removed)
- **Questions Generated**:
  - V1: 4,935 content-focused questions
  - V2: 5,950 pattern-focused questions
- **Embeddings**: Only first message of each conversation
- **Models Tested**:
  - sentence-transformers/all-MiniLM-L6-v2 (384 dims)
  - text-embedding-3-large (3072 dims)
  - text-embedding-3-small (1536 dims)

## Results

### Full Recall Metrics

| Model                  | Type | Recall@1 | Recall@5 | Recall@10 | Recall@30 |
| ---------------------- | ---- | -------- | -------- | --------- | --------- |
| text-embedding-3-large | V1   | 62.5%    | 80.6%    | 85.0%     | 90.6%     |
| text-embedding-3-large | V2   | 12.2%    | 25.3%    | 32.6%     | 45.7%     |
| text-embedding-3-small | V1   | 58.7%    | 77.5%    | 82.7%     | 88.8%     |
| text-embedding-3-small | V2   | 11.3%    | 23.0%    | 29.7%     | 42.1%     |
| sentence-transformers  | V1   | 54.8%    | 73.1%    | 78.8%     | 85.8%     |
| sentence-transformers  | V2   | 10.7%    | 21.0%    | 26.9%     | 38.2%     |

### Key Findings

1. **Massive Performance Gap**: V2 queries perform 42-50% worse than V1 across all models
2. **Model Ranking Consistency**: text-embedding-3-large > text-embedding-3-small > sentence-transformers
3. **Diminishing Returns**: The best model (3-large) only improves V1 by 7.7% and V2 by 1.5% over the smallest model
4. **Alignment Matters More Than Model Quality**: Even the best model fails on misaligned queries

## The Alignment Problem Explained

**V1 Success**: Content-focused queries match what we embed

- Query: "Why did Hurricane Florence weaken?"
- Embedding: "Why did Hurricane Florence weaken when it hit the coast?"
- Result: 62.5% Recall@1 ✓

**V2 Failure**: Pattern-focused queries don't match single-message embeddings

- Query: "conversations with factual questions about weather events"
- Embedding: "Why did Hurricane Florence weaken when it hit the coast?"
- Result: 12.2% Recall@1 ✗

## Cost-Benefit Analysis

| Model                  | Embedding Size | V1 Performance | V2 Performance | Recommendation                       |
| ---------------------- | -------------- | -------------- | -------------- | ------------------------------------ |
| sentence-transformers  | 384 dims       | Good (54.8%)   | Poor (10.7%)   | Best value for aligned queries       |
| text-embedding-3-small | 1536 dims      | Better (58.7%) | Poor (11.3%)   | Balanced choice                      |
| text-embedding-3-large | 3072 dims      | Best (62.5%)   | Poor (12.2%)   | Marginal gains don't justify 8x size |

## Recommendations

1. **Fix Alignment First**: Before upgrading models, ensure queries match embeddings
2. **For V1-style Queries**: Even sentence-transformers delivers acceptable performance
3. **For V2-style Queries**: Must embed full conversations or generate pattern-aware summaries
4. **Model Selection**: Start with sentence-transformers; upgrade only if alignment is good

## Conclusion

## This experiment proves that **alignment beats model sophistication**. A 384-dimensional model with good alignment (V1) outperforms a 3072-dimensional model with poor alignment (V2) by over 40%. Focus on alignment before investing in larger models.

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
