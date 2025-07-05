---
title: The RAG Flywheel
description: Data-Driven Product Development for AI Applications
authors:
  - Jason Liu
date: 2025-04-10
---

# The RAG Flywheel

## Data-Driven Product Development for AI Applications

*A systematic approach to building self-improving AI systems*

!!! abstract "About This Book"
    This book provides a structured approach to evolving Retrieval-Augmented Generation (RAG) from a technical implementation into a continuously improving product. You'll learn to combine product thinking with data science principles to create AI systems that deliver increasing value over time.
    
    Most teams focus on the latest models and algorithms while missing the fundamentals: understanding their data, measuring performance, and systematically improving based on user feedback. This resource shows you the proven approach used by companies like Zapier, Glean, and Exa.

## The RAG Improvement Flywheel

At the core of this book is the RAG improvement flywheel - a continuous cycle that transforms user interactions into product enhancements:

```mermaid
graph TD
    A[Synthetic Data & Evaluation] --> B[Learning from Evaluations]
    B --> C[UX Design & Feedback Collection]
    C --> D[User Segmentation & Analysis]
    D --> E[Building Specialized Capabilities]
    E --> F[Unified Product Architecture]
    F --> A

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#dfd,stroke:#333,stroke-width:2px
```

!!! tip "Beyond Technical Implementation"
    This book goes beyond teaching you how to implement RAG. It shows you how to think about RAG as a product that continuously evolves to meet user needs and deliver business value.

## Table of Contents

### Workshop Series

| Chapter | Title | Focus Area | Key Outcomes |
|---------|-------|------------|-------------|
| [Introduction](workshops/chapter0.md) | Beyond Implementation to Improvement | Product Mindset | Shift from technical to product thinking |
| [Chapter 1](workshops/chapter1.md) | Starting the Flywheel | Evaluation & Metrics | Build synthetic data and evaluation frameworks |
| [Chapter 2](workshops/chapter2.md) | From Evaluation to Enhancement | Fine-tuning & Training | Convert evaluations into training data |
| [Chapter 3.1](workshops/chapter3-1.md) | Feedback Collection | User Experience | Design feedback mechanisms that users actually use |
| [Chapter 3.2](workshops/chapter3-2.md) | Streaming & Performance | User Experience | Implement streaming and reduce perceived latency |
| [Chapter 3.3](workshops/chapter3-3.md) | Quality Improvements | User Experience | Citations, chain-of-thought, and validation |
| [Chapter 4.1](workshops/chapter4-1.md) | Topic Modeling | User Analysis | Find patterns in user feedback and queries |
| [Chapter 4.2](workshops/chapter4-2.md) | Prioritization | User Analysis | Turn insights into strategic action plans |
| [Chapter 5.1](workshops/chapter5-1.md) | Specialized Retrieval | Architecture | Build specialized capabilities for different content |
| [Chapter 5.2](workshops/chapter5-2.md) | Multimodal Search | Architecture | Handle documents, images, tables, and SQL |
| [Chapter 6.1](workshops/chapter6-1.md) | Query Routing | Architecture | Route queries to specialized components |
| [Chapter 6.2](workshops/chapter6-2.md) | Tool Implementation | Architecture | Build interfaces and routers |
| [Chapter 6.3](workshops/chapter6-3.md) | Continuous Improvement | Architecture | Measure and improve systematically |

### Expert Talks

#### Foundation and Evaluation

**[Building Feedback Systems for AI Products](talks/zapier-vitor-evals.md)** - Vitor (Zapier)  
Simple UX changes increased feedback collection from 10 to 40+ submissions per day (4x improvement). Game-changing insight: specific feedback questions like "Did this run do what you expected?" dramatically outperform generic "How did we do?" prompts.

**[Text Chunking Strategies](talks/chromadb-anton-chunking.md)** - Anton (ChromaDB)  
Why chunking remains critical even with infinite context windows due to embedding model limitations and retrieval performance. Surprising discovery: default chunking strategies in popular libraries often produce terrible results for specific datasets.

**[Understanding Embedding Performance through Generative Evals](talks/embedding-performance-generative-evals-kelly-hong.md)** - Kelly Hong  
Generative benchmarking for creating custom evaluation sets from your own data. Surprising finding: model rankings on custom benchmarks often contradict MTEB rankings, showing that public benchmark performance doesn't guarantee real-world success.

#### Training and Fine-Tuning

**[Enterprise Search and Fine-tuning Embedding Models](talks/glean-manav.md)** - Manav (Glean)  
Custom embedding models for each customer achieve 20% performance improvements over 6 months through continuous learning. Counter-intuitive insight: smaller, fine-tuned models often outperform larger general-purpose models for company-specific terminology.

**[Fine-tuning Re-rankers and Embedding Models for Better RAG Performance](talks/fine-tuning-rerankers-embeddings-ayush-lancedb.md)** - Ayush (LanceDB)  
Re-rankers provide 12-20% retrieval improvement with minimal latency penalty, making them "low-hanging fruit" for RAG optimization. Even small 6M parameter models show significant improvements.

#### Production and Monitoring

**[Online Evals and Production Monitoring](talks/online-evals-production-monitoring-ben-sidhant.md)** - Ben & Sidhant  
Trellis framework for managing AI systems with millions of users. Critical discovery: traditional error monitoring (like Sentry) doesn't work for AI since there's no exception when models produce bad outputs.

**[RAG Anti-patterns in the Wild](talks/rag-antipatterns-skylar-payne.md)** - Skylar Payne  
90% of teams adding complexity to RAG systems see worse performance when properly evaluated. Major discovery: silent failures in document processing can eliminate 20%+ of corpus without detection.

#### Query Analysis and Data Organization

**[Query Routing for RAG Systems](talks/query-routing-anton.md)** - Anton (ChromaDB)  
Why the "big pile of records" approach reduces recall due to approximate nearest neighbor algorithms. When filtering large indexes, compute budget is wasted on irrelevant nodes.

#### Specialized Retrieval Systems

**[Agentic RAG](talks/colin-rag-agents.md)** - Colin Flaherty  
Surprising findings from top SWE-Bench performance: simple tools like grep and find outperformed sophisticated embedding models due to agent persistence and course-correction capabilities.

**[Better RAG Through Better Data](talks/reducto-docs-adit.md)** - Adit (Reducto)  
Hybrid computer vision + VLM pipelines outperform pure approaches for document parsing. Critical finding: even 1-2 degree document skews can dramatically impact extraction quality.

**[Encoder Stacking and Multi-Modal Retrieval](talks/superlinked-encoder-stacking.md)** - Daniel (Superlinked)  
LLMs as "pilots that see the world as strings" fundamentally can't understand numerical relationships. Solution: mixture of specialized encoders for different data types rather than forcing everything through text embeddings.

**[Lexical Search in RAG Applications](talks/john-lexical-search.md)** - John Berryman  
Why semantic search struggles with exact matching, product IDs, and specialized terminology. Lexical search provides efficient simultaneous filtering and rich metadata that helps LLMs make better decisions.

#### Advanced Topics and Innovation

**[Semantic Search Over the Web with Exa](talks/semantic-search-exa-will-bryk.md)** - Will Bryk (Exa)  
Why AI systems need fundamentally different search engines than humans. Vision for "perfect search" includes test-time compute where complex queries may take hours or days.

**[RAG Without APIs: Browser-Based Retrieval](talks/rag-without-apis-browser-michael-struwig.md)** - Michael (OpenBB)  
Browser-as-data-layer for secure financial data access without traditional API redistribution. Innovation: stateless agent protocol enables remote function execution in browser.

## Quick Wins: High-Impact RAG Improvements

Based on real-world implementations, here are proven improvements you can implement quickly:

!!! success "Top 5 Quick Wins"
    1. **Change Feedback Copy** : Replace "How did we do?" with "Did we answer your question?"
    2. **Use Markdown Tables** : Format structured data as markdown tables instead of JSON/CSV or XML when tables are complex and multiple columns / headers are needed. 
    3. **Add Streaming Progress** : Show "Searching... Analyzing... Generating..." with progress
    4. **Implement Page-Level Chunking** : For documentation, respect page boundaries, and use page-level chunking. Humans tend to create semantically coherent chunks at the page level.

!!! tip "Medium-Term Improvements (2-4 weeks)"
    - **Fine-tune embeddings**: $1.50 and 40 minutes for 6-10% improvement
    - **Add re-ranker**: 15-20% retrieval improvement
    - **Build specialized tools**: 10x better for specific use cases
    - **Implement contextual retrieval**: 30% better context understanding
    - **Create Slack feedback integration**: 5x more enterprise feedback

## Workshop Series

### Foundation: Metrics & Evaluation

**[Introduction: Beyond Implementation to Improvement](workshops/chapter0.md)**  
Shifting from technical implementation to product-focused continuous improvement. Understanding RAG as a recommendation engine wrapped around language models and the improvement flywheel.

**[Chapter 1: Kickstarting the Data Flywheel with Synthetic Data](workshops/chapter1.md)**  
Common pitfalls in AI development, leading vs. lagging metrics, understanding precision and recall for retrieval evaluation, and synthetic data generation techniques.

**[Chapter 2: Converting Evaluations into Training Data for Fine-Tuning](workshops/chapter2.md)**  
Why generic embeddings fall short, converting evaluation examples into effective few-shot prompts, contrastive learning, and re-rankers as cost-effective enhancement strategies.

### User Experience & Feedback

**[Chapter 3.1: Feedback Collection - Building Your Improvement Flywheel](workshops/chapter3-1.md)**  
Making feedback visible and engaging (increasing rates from <1% to >30%), proven copy patterns, segmented feedback, and enterprise feedback collection.

**[Chapter 3.2: Overcoming Latency - Streaming and Interstitials](workshops/chapter3-2.md)**  
Psychology of waiting, implementing streaming responses for 30-40% higher feedback collection, skeleton screens and meaningful interstitials.

**[Chapter 3.3: Quality of Life Improvements](workshops/chapter3-3.md)**  
Interactive citations, chain of thought reasoning for 8-15% accuracy improvements, validation patterns as safety nets, and strategic rejection.

### Analysis & Specialization

**[Chapter 4.1: Topic Modeling and Analysis](workshops/chapter4-1.md)**  
Moving from individual feedback to systematic pattern identification, topics vs. capabilities, and transforming "make the AI better" into specific priorities.

**[Chapter 4.2: Prioritization and Roadmapping](workshops/chapter4-2.md)**  
Impact/effort prioritization using 2x2 frameworks, failure mode analysis, and building strategic roadmaps based on user behavior patterns.

### Advanced Architecture

**[Chapter 5.1: Understanding Specialized Retrieval](workshops/chapter5-1.md)**  
Why monolithic approaches reach limits, two complementary strategies (extracting metadata vs. creating synthetic text), and two-level measurement.

**[Chapter 5.2: Implementing Multimodal Search](workshops/chapter5-2.md)**  
Advanced document retrieval, image search challenges, table search dual approach, SQL generation using RAG playbook, and RAPTOR hierarchical summarization.

**[Chapter 6.1: Query Routing Foundations](workshops/chapter6-1.md)**  
The API mindset, organizational structure, evolution from monolithic to modular architecture, and performance formula.

**[Chapter 6.2: Tool Interfaces and Implementation](workshops/chapter6-2.md)**  
Designing tool interfaces, router implementation using structured outputs, dynamic example selection, and tool portfolio design.

**[Chapter 6.3: Performance Measurement and Improvement](workshops/chapter6-3.md)**  
Measuring tool selection effectiveness, dual-mode UI, user feedback as training data, and creating improvement flywheel.

## How to Use This Resource

**For Beginners**: Start with the [Introduction](workshops/chapter0.md) to understand the product mindset, then work through the chapters sequentially.

**For Quick Wins**: Jump to the [Quick Wins section](#quick-wins-high-impact-rag-improvements) above for immediate improvements you can implement today.

**For Specific Problems**: Check the [FAQ](office-hours/faq.md) for answers to common questions, or browse talks by topic in the table above.

**For Complete Implementation**: Follow the full workshop series from Chapter 1 through 6.3 to build a comprehensive self-improving RAG system.

## Key Insights Across All Content

**Most Important Finding**: Teams that iterate fastest on data examination consistently outperform those focused on algorithmic sophistication.

**Most Underutilized Techniques**: Fine-tuning embeddings and re-rankers are more accessible and impactful than most teams realize.

**Biggest Mistake**: 90% of teams add complexity that makes their RAG systems worse. Start simple, measure everything, improve systematically.

**Critical Success Factors**:
- Establish evaluation frameworks before building
- Design feedback collection into your UX from day one
- Understand your users and their query patterns
- Build specialized tools for different content types
- Create unified routing that feels seamless to users

## Frequently Asked Questions

Top questions from office hours:

- **"Is knowledge graph RAG production ready?"** Probably not. [See why →](office-hours/faq.md#is-knowledge-graph-rag-production-ready-by-now-do-you-recommend-it)
- **"How do we handle time-based queries?"** Use PostgreSQL with pgvector-scale. [Learn more →](office-hours/faq.md#how-do-we-introduce-a-concept-of-time-and-vector-search-to-answer-questions-like-whats-the-latest-news-without-needing-to-move-to-a-graph-database)
- **"Should we use DSPy for prompt optimization?"** It depends. [See when →](office-hours/faq.md#what-is-your-take-on-dspy-should-we-use-it)
- **"Would you recommend ColBERT models?"** Test against your baseline first. [See approach →](office-hours/faq.md#would-you-recommend-using-colbert-models-or-other-specialized-retrieval-approaches)

[Browse All FAQ](office-hours/faq.md){ .md-button } [View Office Hours](office-hours/){ .md-button }

## For Product Leaders, Engineers, and Data Scientists

!!! info "What You'll Learn"

    **For Product Leaders**
    - How to establish metrics that align with business outcomes
    - Frameworks for prioritizing AI product improvements  
    - Approaches to building product roadmaps for RAG applications
    - Methods for communicating AI improvements to stakeholders

    **For Engineers**
    - Implementation patterns that facilitate rapid iteration
    - Architectural decisions that enable continuous improvement
    - Techniques for building modular, specialized capabilities
    - Approaches to technical debt management in AI systems
    
    **For Data Scientists**
    - Methods for creating synthetic evaluation datasets
    - Techniques for segmenting and analyzing user queries
    - Frameworks for measuring retrieval effectiveness
    - Approaches to continuous learning from user interactions

## Navigate by Topic

**Evaluation & Metrics**: [Chapter 1](workshops/chapter1.md) • [Kelly Hong Talk](talks/embedding-performance-generative-evals-kelly-hong.md) • [Vitor Zapier Talk](talks/zapier-vitor-evals.md)

**Fine-tuning & Training**: [Chapter 2](workshops/chapter2.md) • [Ayush LanceDB Talk](talks/fine-tuning-rerankers-embeddings-ayush-lancedb.md) • [Manav Glean Talk](talks/glean-manav.md)

**User Experience**: [Chapter 3 Series](workshops/chapter3-1.md) • [Streaming Guide](workshops/chapter3-2.md) • [Quality Improvements](workshops/chapter3-3.md)

**Architecture & Routing**: [Chapter 6 Series](workshops/chapter6-1.md) • [Anton Query Routing](talks/query-routing-anton.md) • [Multi-modal Retrieval](talks/superlinked-encoder-stacking.md)

**Production & Monitoring**: [Ben & Sidhant Talk](talks/online-evals-production-monitoring-ben-sidhant.md) • [RAG Anti-patterns](talks/rag-antipatterns-skylar-payne.md)


## About the Author

Jason Liu brings practical experience from his work at Facebook, Stitch Fix, and as a consultant for companies like HubSpot, Zapier, and many others. His background spans computer vision, recommendation systems, and RAG applications across diverse domains.

!!! quote "Author's Philosophy"
   "The most successful AI products aren't the ones with the most sophisticated models, but those built on disciplined processes for understanding users, measuring performance, and systematically improving. This resource will show you how to create not just a RAG application, but a product that becomes more valuable with every interaction."

---

## Getting Started

Begin your journey by reading the [Introduction](workshops/chapter0.md) or jump directly to [Chapter 1](workshops/chapter1.md) to start building your evaluation framework and data foundation.

If you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
