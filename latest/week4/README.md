# Week 4: Topic Modeling and Query Classification

## Overview

This week shifts focus from improving retrieval mechanics to understanding user behavior through query analysis. By applying topic modeling and classification techniques to user queries, you can identify patterns that reveal where your RAG system struggles most. This data-driven approach helps prioritize improvements based on actual user needs rather than technical assumptions.

The methodology combines unsupervised learning to discover natural query clusters with supervised classification to track patterns over time. By analyzing the relationship between query topics and user satisfaction, you can identify high-impact areas for improvement - queries that are both frequent and problematic. This systematic approach ensures your optimization efforts target the areas that will benefit users most.

## Learning Objectives

By the end of this week, you'll be able to:

- Generate realistic synthetic queries that simulate diverse user behaviors
- Apply BERTopic for unsupervised discovery of query patterns
- Visualize topic relationships and their correlation with user satisfaction
- Build query classifiers using structured taxonomies
- Identify high-volume, low-satisfaction query areas requiring attention
- Create monitoring systems for ongoing query pattern analysis
- Make data-driven decisions about where to focus RAG improvements

## Notebooks

### 1. Generate Dataset.ipynb

**Purpose**: Create a realistic dataset of user queries simulating diverse behaviors and intents

**What You'll Learn**:

- Synthetic query generation with persona and intent variation
- Ensuring dataset diversity through embedding similarity checks
- Structured data generation with citations and metadata
- Simulating realistic user communication patterns

**What You'll Build**:

- Comprehensive query dataset with varied personas and intents
- Citation system linking queries to source documents
- Diverse test set representing real user behavior patterns

### 2. Topic Modelling.ipynb

**Purpose**: Apply unsupervised learning to discover natural patterns and pain points in user queries

**What You'll Learn**:

- BERTopic configuration for effective topic discovery
- Dimensionality reduction with UMAP and clustering with HDBSCAN
- Topic visualization and relationship analysis
- Correlating topics with user satisfaction metrics

**What You'll Build**:

- Topic model revealing natural query clusters
- Satisfaction analysis by topic area
- Visualizations identifying high-impact improvement areas

### 3. Classifier.ipynb

**Purpose**: Build a systematic query classification system for ongoing monitoring and analysis

**What You'll Learn**:

- Taxonomy design for query categorization
- Structured classification using instructor and Pydantic
- Multi-label vs. hierarchical classification strategies
- Building monitoring systems for production use

**What You'll Build**:

- YAML-based classification taxonomy
- Query classifier with validation
- Foundation for ongoing query analytics

## Key Concepts

- **Topic Modeling**: Unsupervised discovery of themes and patterns in text data
- **BERTopic**: State-of-the-art topic modeling using transformers and clustering
- **Persona-based Generation**: Creating synthetic data that reflects different user types and moods
- **Intent Classification**: Categorizing queries by their underlying purpose or goal
- **Satisfaction Correlation**: Linking query patterns to user satisfaction metrics
- **UMAP**: Dimensionality reduction technique preserving local and global structure
- **HDBSCAN**: Density-based clustering algorithm for finding topics of varying sizes

## Prerequisites

### Knowledge Requirements

- Basic understanding of clustering and dimensionality reduction
- Familiarity with classification concepts
- Understanding of embeddings from previous weeks

### Technical Requirements

- Python packages: `bertopic`, `sentence-transformers`, `umap-learn`, `hdbscan`, `instructor`, `pydantic`, `pyyaml`, `pandas`, `matplotlib`
- API keys: OpenAI API access for generation and classification
- Hardware: No GPU required (CPU sufficient for BERTopic inference)

## Project Structure

```text
week4/
├── README.md
├── Generate Dataset.ipynb
├── Topic Modelling.ipynb
├── Classifier.ipynb
├── data/
│   ├── md/                  # Klarna FAQ pages
│   ├── questions.jsonl      # Base questions
│   └── cleaned.jsonl        # Synthetic queries
├── assets/
│   └── matrix.png           # Topic-satisfaction viz
├── categories.yml           # Classification taxonomy
└── config.yml               # Generation config
```

## Datasets

- **Klarna FAQ Pages**: Real customer service documentation providing a foundation for query generation
- **Synthetic Queries**: Generated dataset with diverse personas, intents, and communication styles
- **Topic Clusters**: Discovered patterns showing natural groupings of user queries

## Expected Outcomes

After completing this week's materials, you'll have:

1. A diverse synthetic query dataset reflecting realistic user behaviors
2. Topic model revealing natural patterns in how users ask questions
3. Identification of high-priority areas (frequent queries with low satisfaction)
4. Query classification system for ongoing monitoring
5. Data-driven insights about where to focus RAG improvements

## Common Issues and Solutions

### Issue 1: BERTopic producing too many or too few topics

**Solution**: Adjust min_topic_size and min_samples parameters. Start with min_topic_size=10 and adjust based on your dataset size.

### Issue 2: Poor topic quality or unclear topic labels

**Solution**: Experiment with different embedding models and ensure your dataset has sufficient diversity. Consider using nr_topics parameter to merge similar topics.

### Issue 3: Classifier producing inconsistent categorizations

**Solution**: Refine your taxonomy to reduce ambiguity. Add more specific examples in your classification prompts.

## Next Steps

- Complete notebooks in sequence to build understanding progressively
- Analyze which topics correlate with lowest satisfaction scores
- Review Week 5 to learn how structured metadata can address identified pain points
- Consider implementing the classification system in production for ongoing monitoring

## Additional Resources

- [BERTopic Documentation](https://maartengr.github.io/BERTopic/)
- [UMAP: Uniform Manifold Approximation and Projection](https://arxiv.org/abs/1802.03426)
- [HDBSCAN Documentation](https://hdbscan.readthedocs.io/)
- [Understanding User Intent in Search](https://www.searchenginejournal.com/search-intent/)

---

## **Note**: This week's analysis techniques are applicable beyond RAG systems. The same approach can help understand user behavior in any text-based application, making these skills broadly valuable for product improvement.

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
