# Systematically Improving RAG -- Cohort 2 Code

To install the requirements, run `pip install -r requirements.txt`
IF you are using `uv` to install the requirements, you can run `uv pip install -r requirements.txt`

Here is an overview of the notebooks by week:

**Week 1: RAG Evaluation Foundations**
- *Notebook 1:* Create synthetic evaluation data and establish core metrics (Precision/Recall)
- *Notebook 2:* Compare retrieval strategies (embedding vs hybrid search) using benchmarks 
- *Notebook 3:* Apply statistical validation techniques to verify improvements

**Week 2: Embedding Fine-tuning**
- *Notebook 1:* Generate synthetic transaction data for fine-tuning
- *Notebook 2:* Fine-tune Cohere's managed re-ranker service
- *Notebook 3:* Implement open-source fine-tuning using sentence-transformers

**Week 4: Query Understanding**
- *Notebook 1:* Generate diverse test queries and establish segmentation strategy
- *Notebook 2:* Use topic modeling (BERTopic) to discover query patterns
- *Notebook 3:* Build a classification system based on discovered patterns

**Week 5: Structured Data & Metadata**
- *Notebook 1:* Generate structured metadata using LLMs and implement validation
- *Notebook 2:* Combine metadata filtering with semantic search
- *Notebook 3:* Add SQL database access through safe query generation

**Week 6: Tool Selection**
- *Notebook 1:* Define and implement tool selection evaluation metrics
- *Notebook 2:* Create comprehensive test suite for tool selection
- *Notebook 3:* Improve performance through system prompts and few-shot examples

Each week builds on previous concepts while introducing new techniques:
- Week 1 establishes evaluation foundations
- Week 2 shows how to improve base retrieval
- Week 4 adds query understanding capabilities
- Week 5 introduces structured data handling
- Week 6 brings everything together in a multi-tool system

The progression moves from basic RAG capabilities to increasingly sophisticated features while maintaining focus on systematic evaluation and improvement.