# Week 2: Fine-tuning Embedding Models for Retrieval

## Notebooks Overview

### 1. Synthetic-Transactions.ipynb
This notebook focuses on generating and validating synthetic transaction data for fine-tuning embedding models.

**What You'll Do:**
- Create a Pydantic model (`Transaction`) to represent financial transaction data
- Generate realistic transaction descriptions using GPT models with instructor for structure
- Set up a manual review process using the included Streamlit app (`label.py`)
- Establish LanceDB tables for vector search evaluation
- Implement evaluation metrics (recall@k, MRR@k)
- Create train/eval splits for model training
- Visualize performance across different data splits

You'll build a high-quality dataset specifically designed for embedding fine-tuning.

### 2. Finetune Cohere.ipynb
This notebook demonstrates fine-tuning a Cohere re-ranker model for improved retrieval performance.

**What You'll Do:**
- Prepare training data with hard negatives for effective re-ranker training
- Upload dataset to Cohere and initiate model fine-tuning
- Evaluate the fine-tuned model against baselines using metrics from Week 1
- Visualize performance improvements through comparison charts
- Analyze where and why the fine-tuned model performs better

You'll experience how managed services can simplify the fine-tuning process while delivering significant performance gains.

### 3. Open Source Models.ipynb
This notebook explores fine-tuning open-source embedding models using sentence-transformers.

**What You'll Do:**
- Prepare datasets for triplet loss training with semi-hard negative mining
- Configure and train a BAAI/bge-base-en model with SentenceTransformerTrainer
- Use BatchSemiHardTripletLoss for effective training
- Push the fine-tuned model to Hugging Face Hub for sharing
- Conduct comprehensive evaluation comparing base vs. fine-tuned model performance
- Analyze trade-offs between managed and open-source approaches

You'll gain hands-on experience with open-source model fine-tuning techniques.

## Data Files and Assets
- `categories.json`: Contains 24 transaction categories with sample transactions
- `cleaned.jsonl`: Manually approved and labeled transaction examples
- `hard_negatives.png` and `semi-hard-negative.png`: Illustrations of training techniques
- `helpers.py`: Utility functions for calculating metrics and performing search
- `label.py`: Streamlit application for manual transaction labeling

## Technical Requirements
- Required libraries: sentence-transformers, lancedb, braintrust, pydantic, openai, cohere
- Hugging Face token with write access for model hosting (open-source approach)
- Cohere API key for managed service section
- GPU recommended for open-source fine-tuning

## Why These Notebooks Matter
These notebooks demonstrate two distinct approaches to improving embedding performance:
1. Managed services (Cohere): Simple API-based implementation with minimal engineering
2. Open-source (sentence-transformers): Complete control with self-hosting capabilities

Both approaches show significant performance gains (15-30% in MRR and recall), highlighting that domain-specific fine-tuning is one of the most effective ways to improve RAG system performance.