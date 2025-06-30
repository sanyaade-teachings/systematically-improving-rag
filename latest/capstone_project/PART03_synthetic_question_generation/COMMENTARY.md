# Synthetic Query Generation: V1 vs V2 Analysis

## The Power of Prompt Engineering in RAG Systems

This project demonstrates a critical insight: **the prompt IS the product** when building with LLMs. By comparing two different approaches to synthetic query generation, we see how dramatically different results can emerge from subtle changes in prompting strategy.

## The Two Approaches

### V1: Search-Focused Generation
- **Perspective**: Product manager analyzing user search patterns
- **Goal**: Generate queries users might naturally type
- **Focus**: Specific terms, problems, and solutions from conversations
- **Example queries**: "how to fix Python import error", "ChatGPT won't answer my question"

### V2: Pattern-Focused Generation  
- **Perspective**: Research analyst studying conversation patterns
- **Goal**: Categorize conversation types and themes
- **Focus**: Abstract patterns rather than specific details
- **Example queries**: "conversations where AI refuses medical advice", "technical troubleshooting discussions"

Well, if you're someone building an application that's a search conversation history. There's no right answer, whether or not one or two is the correct way of doing things. But it really matters whether or not you know what your customer is going to ask. 

## The Dramatic Results

The recall metrics tell a compelling story:


                              Recall Metrics per Backend and Version                               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Backend / Version           ┃ Queries ┃ Recall@1 ┃ Recall@5 ┃ Recall@10 ┃ Recall@20 ┃ Recall@30 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ ChromaDB (v1)               │      67 │   28.36% │   49.25% │    53.73% │    62.69% │    64.18% │
│ ChromaDB (v2)               │      83 │    1.20% │    2.41% │     6.02% │    14.46% │    14.46% │
│ TurboPuffer ‑ Vector (v1)   │      67 │   26.87% │   49.25% │    61.19% │    62.69% │    67.16% │
│ TurboPuffer ‑ Vector (v2)   │      83 │    1.20% │    2.41% │     8.43% │    15.66% │    15.66% │
│ TurboPuffer ‑ FullText (v1) │      67 │   34.33% │   40.30% │    46.27% │    52.24% │    53.73% │
│ TurboPuffer ‑ FullText (v2) │      83 │    3.61% │    4.82% │     7.23% │     8.43% │     8.43% │
│ TurboPuffer ‑ Hybrid (v1)   │      67 │    0.00% │    0.00% │     0.00% │     0.00% │     0.00% │
│ TurboPuffer ‑ Hybrid (v2)   │      83 │    0.00% │    0.00% │     0.00% │     0.00% │     0.00% │
└─────────────────────────────┴─────────┴──────────┴──────────┴───────────┴───────────┴───────────┘

## Why Such Different Results?

The key insight: **we're only embedding the first user message** from each conversation, not the entire conversation history.

- V1 succeeds because it generates queries that match how users naturally phrase their initial questions
- V2 fails because it generates abstract patterns that require understanding the full conversation context
- This perfectly illustrates how your embedding strategy must align with your query generation approach

The solution here might be that we might want to do rag over the entire conversation. But this means a couple of things: How do we chunk conversations? Should we embed the whole thing? Or should we run a summarization of the conversation? 

If we summarize things, you can also imagine that this would require us to not only experiment on the query generation, but also the conversation summarization test.

## Deep Analysis: Full-Text vs Vector Search Behavior

### 1. Full-Text Search v1: High Initial Recall, Plateaus Quickly

**TurboPuffer Full-Text v1**: 34.33% → 40.30% → 46.27% → 52.24% → 53.73%

The full-text search achieves the **highest recall@1 (34.33%)** among all methods but shows minimal improvement as k increases. This happens because:

- **Exact term matching**: V1 queries contain specific terms that directly match the first user message (e.g., "Python import error")
- **Limited semantic understanding**: Full-text search can't identify conceptually related but differently-worded content
- **Front-loaded results**: The best matches are found immediately through keyword overlap, with diminishing returns for additional results

### 2. Vector Embeddings: Steady Improvement with k

**ChromaDB v1**: 28.36% → 49.25% → 53.73% → 62.69% → 64.18%
**TurboPuffer Vector v1**: 26.87% → 49.25% → 61.19% → 62.69% → 67.16%

Vector embeddings show consistent improvement as k increases because:

- **Semantic similarity**: Embeddings capture meaning beyond exact terms
- **Gradient of relevance**: Related conversations may use different terminology but similar concepts
- **Broader recall potential**: As k increases, the search can find conversations that are semantically related even if they don't share exact keywords

### 3. V2's Dramatic Difference: Vector vs Full-Text

**TurboPuffer Vector v2**: 1.20% → 2.41% → 8.43% → 15.66% → 15.66%
**TurboPuffer Full-Text v2**: 3.61% → 4.82% → 7.23% → 8.43% → 8.43%

The v2 results reveal a critical insight:

- **V2 queries are abstract patterns** like "conversations where AI refuses medical advice"
- **Vector search can partially recover** because embeddings capture thematic similarity even when exact terms don't match
- **Full-text search fails catastrophically** because abstract pattern queries rarely match the specific terms in first messages

The improvement in v2 vector search (1.20% → 15.66%) shows that while the initial recall is poor, semantic search can eventually find some thematically related conversations. Full-text search plateaus at 8.43% because it relies on literal term matching.

### The Fundamental Mismatch

The core issue is that **only the first user message is embedded**, but v2 generates queries about entire conversation patterns. This creates a fundamental retrieval mismatch:

- **V1 Success**: Queries match how users actually start conversations
- **V2 Failure**: Queries require understanding the full conversation arc

### Why This Matters for RAG Systems

1. **Embedding Strategy Must Match Query Patterns**
   - If users search for specific problems → embed initial messages
   - If users search for conversation patterns → embed full conversations or summaries

2. **Full-Text vs Vector Trade-offs**
   - Full-text excels at exact matches but has limited semantic reach
   - Vector search provides broader semantic coverage but may miss exact matches

3. **The k-parameter Reveals Search Method Characteristics**
   - Full-text: Best results are immediate, minimal benefit from larger k
   - Vector: Gradual improvement as k increases, capturing semantic neighbors 

## The Value of Rapid Prototyping with LLMs

Most of this code was actually written by an alum. One of the things we want to make sure we do is use cheap models, use async processing as much as possible, and cache the results. Notice I'm not using any vendors. I'm simply using disk cache and a SQLite database to keep track of everything going on. As I scale to multiple people, multiple teams, and many experiments, then I might decide to do something about it. 

## Key Takeaways

1. **Understand Your Users**: V1 works because it mirrors actual user behavior. V2 serves a different purpose entirely.

2. **Alignment is Critical**: Your embedding strategy, query generation, and search approach must all align. Mismatched strategies lead to poor performance.

3. **Prototype Rapidly**: With LLMs, you can test hypotheses in hours. Don't over-engineer before validating your approach.

4. **The Prompt is the Product**: In LLM applications, changing a few lines of prompt text can completely transform your system's behavior and effectiveness.

## Practical Implications

When building RAG systems:
- Start by understanding what your users are actually trying to find
- Ensure your embedding strategy matches your expected query types
- Test multiple prompting approaches before committing to one
- Use simple infrastructure for experimentation - complexity can come later

This project beautifully demonstrates that in the age of LLMs, the biggest gains often come not from better models or more data, but from better understanding of the problem space and more thoughtful prompt design.