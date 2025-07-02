---
title: Talks and Presentations
description: Collection of talks, lightning lessons, and presentations from the Systematically Improving RAG Applications series
---

# Talks and Presentations

This section contains talks and presentations from the Systematically Improving RAG Applications series, featuring insights from industry experts and practitioners.

## Talks by Week

Our talks are organized to complement the workshop curriculum. Each week focuses on specific aspects of building and improving RAG systems.

### Week 1: Evaluation and Metrics Foundation

These talks focus on establishing evaluation frameworks and building feedback systems.

- **[Building Feedback Systems for AI Products](zapier-vitor-evals.md)** - Vitor from Zapier shares how they 4x'd their feedback collection through strategic UX changes
- **[Text Chunking Strategies](chromadb-anton-chunking.md)** - Anton from ChromaDB covers evaluation methods for chunking strategies

### Week 2: Training Data and Fine-Tuning

Learn about creating custom embedding models and fine-tuning for specific domains.

- **[Enterprise Search and Fine-tuning Embedding Models](glean-manav.md)** - Manav from Glean demonstrates how custom embedding models dramatically improve enterprise search

### Week 3: Deployment and Feedback Collection

Deployment strategies and production monitoring for RAG systems.

- **[Online Evals and Production Monitoring](online-evals-production-monitoring-ben-sidhant.md)** - Ben Hylak and Sidhant Bendre share their Trellis framework for monitoring AI systems at scale
- **[RAG Anti-patterns in the Wild](rag-antipatterns-skylar-payne.md)** - Skylar Payne identifies common mistakes teams make in production RAG systems

### Week 4: Query Analysis and Segmentation

Understanding user queries and routing them effectively.

- **[Query Routing for RAG Systems](query-routing-anton.md)** - Anton from ChromaDB explains data organization and query routing strategies

### Week 5: Specialized Retrieval Systems

Building specialized capabilities for different content types and use cases.

- **[Agentic RAG](colin-rag-agents.md)** - Colin Flaherty reveals when simple tools like grep outperform sophisticated embedding models
- **[Better RAG Through Better Data](reducto-docs-adit.md)** - Adit Abraham shares practical insights on document ingestion pipelines
- **[Encoder Stacking and Multi-Modal Retrieval](superlinked-encoder-stacking.md)** - Daniel from Superlinked on building retrieval for diverse data types
- **[Lexical Search in RAG Applications](john-lexical-search.md)** - John Berryman demonstrates how traditional search complements modern approaches

### Week 6: Advanced Topics and Innovation

Cutting-edge approaches and innovative techniques.

- **[Semantic Search Over the Web with Exa](semantic-search-exa-will-bryk.md)** - Will Bryk on building AI-first search engines
- **[Understanding Embedding Performance through Generative Evals](embedding-performance-generative-evals-kelly-hong.md)** - Kelly Hong presents custom evaluation methodologies
- **[RAG Without APIs: Browser-Based Retrieval](rag-without-apis-browser-michael-struwig.md)** - Michael Struwig's novel approach to secure data access

## All Talks

### Core RAG Concepts

#### [RAG Anti-patterns in the Wild](rag-antipatterns-skylar-payne.md)

Skylar Payne shares extensive experience identifying common RAG anti-patterns across different industries. This talk provides practical advice for improving AI systems through better data handling, retrieval, and evaluation practices, highlighting the most frequent mistakes teams make and concrete strategies to avoid them.

#### [Agentic RAG](colin-rag-agents.md)

Colin Flaherty (previously a founding engineer at Augment and co-author of Meta's Cicero AI) discusses autonomous coding agents and retrieval systems. This session explores how agentic approaches are transforming traditional RAG systems, revealing when simple tools like grep outperform sophisticated embedding models, and how agent persistence can overcome retrieval limitations.

### Search and Retrieval

#### [Semantic Search Over the Web with Exa](semantic-search-exa-will-bryk.md)

Will Bryk from Exa shares how AI is fundamentally changing search requirements. This talk covers the technical challenges of building a semantic search engine designed specifically for AI applications rather than human users, offering unique insights into the evolution of search technology.

#### [Lexical Search in RAG Applications](john-lexical-search.md)

John Berryman shares expertise on traditional search techniques and their application in RAG systems. This session explores how lexical search can complement modern vector-based approaches, covering inverted indexes, TF-IDF scoring, and hybrid search strategies.

#### [Enterprise Search and Fine-tuning Embedding Models](glean-manav.md)

Manav from Glean delivers an insightful lecture on enterprise search and fine-tuning embedding models. This session focuses on Glean's approach to optimizing AI through custom embedding models, handling company-specific language, and learning from user feedback.

#### [Encoder Stacking and Multi-Modal Retrieval](superlinked-encoder-stacking.md)

Daniel from Superlinked explores improving retrieval systems by applying lessons from recommender systems. This talk reveals insights about the limitations of current search approaches and how to build sophisticated retrieval architectures that handle diverse data types using specialized encoders.

### Data Organization and Processing

#### [Query Routing for RAG Systems](query-routing-anton.md)

Anton Troynikov from ChromaDB shares critical insights about organizing data for retrieval systems. This session covers data organization strategies, the limitations of the "big pile of records" approach, and effective query routing techniques.

#### [Text Chunking Strategies](chromadb-anton-chunking.md)

Anton from ChromaDB discusses their latest research on text chunking for RAG applications. The talk covers fundamentals of chunking strategies, evaluation methods, and practical tips for improving retrieval performance.

#### [Better RAG Through Better Data](reducto-docs-adit.md)

Adit Abraham (Co-founder & CEO of Reducto) shares practical insights on document ingestion pipelines that work in production environments. This conversation covers parsing complex documents, handling tables and forms, and optimizing data representation for language models.

### Evaluation and Monitoring

#### [Understanding Embedding Performance through Generative Evals](embedding-performance-generative-evals-kelly-hong.md)

Kelly Hong presents a deep dive into generative benchmarking - a novel approach to creating custom evaluation sets from your own data. Learn how to move beyond generic benchmarks to create evaluations that match your specific use case.

#### [Online Evals and Production Monitoring](online-evals-production-monitoring-ben-sidhant.md)

Ben Hylak and Sidhant Bendre deliver a comprehensive session on AI monitoring and production testing. They share their Trellis framework for identifying issues in AI systems before users notice them.

#### [Building Feedback Systems for AI Products](zapier-vitor-evals.md)

Vitor from Zapier discusses how they dramatically improved their feedback collection systems for AI products. This conversation reveals practical strategies for gathering, analyzing, and implementing user feedback to create a continuous improvement cycle.

### Innovative Approaches

#### [RAG Without APIs: Browser-Based Retrieval](rag-without-apis-browser-michael-struwig.md)

Michael Struwig presents a novel approach to RAG systems that leverages the browser as a data layer instead of traditional APIs. This technique enables secure, flexible AI-powered analysis tools that can access data without exposing it through conventional endpoints.

## About the Series

These talks are part of the "Systematically Improving RAG Applications" educational series, which focuses on practical approaches to building, monitoring, and improving RAG systems in production environments.

Each talk provides deep insights from industry experts who have built and scaled RAG systems in production. Topics range from fundamental concepts and common pitfalls to advanced techniques for document processing, evaluation, and production monitoring.

For more information about the broader curriculum, see the [main index](../index.md).

---

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>