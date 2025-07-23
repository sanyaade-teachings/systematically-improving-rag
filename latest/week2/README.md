# Week 2: Fine-tuning Embedding Models for Retrieval

## Overview

This week focuses on one of the most impactful ways to improve RAG system performance: fine-tuning embedding models for your specific domain. Generic embedding models are trained on broad internet data and may not capture the nuances of your particular use case. By fine-tuning these models with domain-specific data, you can achieve significant improvements in retrieval quality.

You'll explore two complementary approaches to fine-tuning: using managed services like Cohere that handle the infrastructure complexity for you, and open-source solutions using sentence-transformers that give you complete control over the process. Both approaches demonstrate 15-30% improvements in key retrieval metrics, making fine-tuning one of the highest-ROI optimizations for RAG systems.

## Learning Objectives

By the end of this week, you'll be able to:

- Generate high-quality synthetic training data for embedding fine-tuning
- Implement manual review processes to ensure training data quality
- Fine-tune embedding models using both managed services and open-source tools
- Create effective training datasets with hard and semi-hard negatives
- Evaluate fine-tuned models against baselines using established metrics
- Deploy fine-tuned models to production environments
- Make informed decisions between managed and self-hosted approaches

## Notebooks

### 1. Synthetic-Transactions.ipynb

**Purpose**: Generate and validate high-quality synthetic transaction data for embedding model fine-tuning

**What You'll Learn**:

- Structured data generation using Pydantic models and instructor
- Quality control through manual review processes
- Dataset preparation techniques for embedding training
- Evaluation setup with proper train/eval splits

**What You'll Build**:

- Synthetic transaction dataset with realistic descriptions
- Manual review interface using Streamlit
- Evaluation pipeline with LanceDB for measuring improvements

### 2. Finetune Cohere.ipynb

**Purpose**: Fine-tune a Cohere re-ranker model using managed services for simplified deployment

**What You'll Learn**:

- Hard negative mining techniques for effective training
- Working with Cohere's fine-tuning API
- Comparative evaluation of base vs. fine-tuned models
- Performance analysis and visualization techniques

**What You'll Build**:

- Fine-tuned Cohere re-ranker model
- Training dataset with carefully selected hard negatives
- Performance comparison visualizations

### 3. Open Source Models.ipynb

**Purpose**: Fine-tune open-source embedding models with complete control over the training process

**What You'll Learn**:

- Triplet loss training with semi-hard negative mining
- SentenceTransformerTrainer configuration and usage
- Model deployment to Hugging Face Hub
- Trade-offs between managed services and self-hosted solutions

**What You'll Build**:

- Fine-tuned BAAI/bge-base-en embedding model
- Training pipeline using sentence-transformers
- Deployable model on Hugging Face Hub

## Key Concepts

- **Hard Negatives**: Training examples that are similar but incorrect, forcing the model to learn fine distinctions
- **Semi-Hard Negatives**: Moderately challenging negative examples that provide optimal learning signals
- **Triplet Loss**: Training objective that brings positive examples closer while pushing negatives away
- **Domain Adaptation**: Specializing general models for specific use cases through fine-tuning
- **Re-ranker Models**: Second-stage models that reorder initial retrieval results for better precision

## Prerequisites

### Knowledge Requirements

- Understanding of embedding models and vector similarity
- Basic knowledge of model training concepts (loss functions, epochs, batch size)
- Familiarity with the evaluation metrics from Week 1

### Technical Requirements

- Python packages: `sentence-transformers`, `lancedb`, `braintrust`, `pydantic`, `openai`, `cohere`, `streamlit`
- API keys: OpenAI API access, Cohere API key, Hugging Face token with write access
- Hardware: GPU recommended for open-source fine-tuning (CPU possible but slower)

## Project Structure

```text
week2/
├── README.md
├── Synthetic-Transactions.ipynb
├── Finetune Cohere.ipynb
├── Open Source Models.ipynb
├── data/
│   ├── categories.json
│   ├── cleaned.jsonl
│   └── training_data/
├── assets/
│   ├── hard_negatives.png
│   └── semi-hard-negative.png
├── helpers.py
└── label.py
```

## Datasets

- **Transaction Categories**: 24 financial transaction types with sample descriptions for generating training data
- **Cleaned Transactions**: Manually reviewed and approved transaction examples ensuring high-quality training signals
- **Training Pairs**: Query-document pairs with hard negatives for effective model fine-tuning

## Expected Outcomes

After completing this week's materials, you'll have:

1. A high-quality domain-specific training dataset with validated examples
2. Fine-tuned embedding models showing 15-30% improvement in retrieval metrics
3. Experience with both managed (Cohere) and open-source (sentence-transformers) approaches
4. Deployed models ready for production use
5. Clear understanding of when to use managed services vs. self-hosted solutions

## Common Issues and Solutions

### Issue 1: Low quality synthetic data affecting model performance

**Solution**: Use the manual review process (label.py) to filter out poor examples. Quality matters more than quantity for fine-tuning.

### Issue 2: Overfitting on small datasets

**Solution**: Ensure sufficient dataset diversity and use proper validation splits. Monitor validation metrics during training.

### Issue 3: GPU memory errors during open-source training

**Solution**: Reduce batch size or use gradient accumulation. Consider using smaller base models if memory is limited.

## Next Steps

- Complete notebooks in order to build upon concepts progressively
- Compare performance gains between Cohere and open-source approaches
- Review Week 3 content to prepare for advanced retrieval techniques
- Experiment with different negative sampling strategies

## Additional Resources

- [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084)
- [Cohere Rerank Documentation](https://docs.cohere.com/docs/reranking)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [Efficient Natural Language Response Suggestion for Smart Reply](https://arxiv.org/abs/1705.00652)

---

## **Note**: Ensure you've completed Week 1's evaluation framework before starting these notebooks. The metrics and benchmarking tools from Week 1 are essential for measuring the improvements achieved through fine-tuning.

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
