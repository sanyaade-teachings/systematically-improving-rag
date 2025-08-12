# Week 4: Topic Modeling and Query Classification

## Notebooks Overview

### 1. Generate Dataset.ipynb

This notebook focuses on creating a realistic dataset of user queries based on Klarna's FAQ documents.

**What You'll Do:**

- Generate diverse synthetic questions using instructor and OpenAI
- Create queries with varied personas (angry customer, confused user, etc.)
- Implement intent variation (seeking information, reporting issues, etc.)
- Calculate embedding similarity to ensure dataset diversity
- Add citations linking questions to source documents
- Store the output in structured JSONL format for further analysis

You'll build a comprehensive dataset that simulates real user behavior with diverse intents and communication styles.

### 2. Topic Modelling.ipynb

This notebook applies unsupervised learning to discover patterns in user queries.

**What You'll Do:**

- Configure and apply BERTopic for unsupervised topic discovery
- Set up embedding model, UMAP, and HDBSCAN for effective clustering
- Visualize topic similarities and relationships
- Analyze satisfaction scores by topic to identify pain points
- Create matrices showing relationship between topics and satisfaction
- Identify the "danger zone" of high-volume, low-satisfaction query areas

You'll gain insights into natural query patterns that can guide system improvements.

### 3. Classifier.ipynb

This notebook develops a systematic approach to categorize and track queries over time.

**What You'll Do:**

- Define a classification taxonomy using YAML configuration
- Implement a classifier using instructor and Pydantic for validation
- Categorize queries by type, intent, and complexity
- Test the classifier on sample queries
- Examine different categorization strategies (multi-label vs. hierarchical)
- Create a foundation for ongoing query monitoring

You'll build a system to categorize incoming queries that provides actionable analytics.

## Data Files and Assets

- `data/md/`: Klarna FAQ pages converted to markdown format
- `data/questions.jsonl`: Base questions extracted from FAQ pages
- `data/cleaned.jsonl`: Processed dataset with synthetic queries
- `categories.yml`: Classification schema defining query types
- `config.yml`: Configuration for query generation with personas/intents
- `assets/matrix.png`: Visualization of topic-satisfaction relationship

## Technical Requirements

- Required libraries: BERTopic, sentence-transformers, UMAP, HDBSCAN, instructor, pydantic, yaml
- OpenAI API access for query generation and classification
- Basic understanding of dimensionality reduction and clustering concepts

## Why These Notebooks Matter

Together, these notebooks provide a systematic approach to understanding and improving RAG applications through query pattern analysis:

1. First, generate realistic test data that mimics actual user behavior
2. Then, discover natural patterns in queries through unsupervised learning
3. Finally, build a classifier that categorizes queries for ongoing monitoring

## This data-driven approach helps identify which query areas need improvement most urgently, allowing targeted enhancements rather than making random changes.

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
