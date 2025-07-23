# Office Hours to Workshops Integration Plan

This document maps frequently asked questions from office hours to specific workshop chapters where they should be integrated.

## Format Example

### 1. Vector Database Selection Guide

**Source**: `cohort2/week2-summary.md`, `cohort3/week-2-1.md`

**Question**: "How do I choose between different vector databases like PostgreSQL with pgvector, LanceDB, ChromaDB, and Turbopuffer?"

**Answer Summary**:

- PostgreSQL with pgvector: Good for combining vector search with SQL queries and metadata filtering
- LanceDB: Excellent for experimenting with hybrid search (lexical + vector + re-ranker)
- Timescale pgvector_scale: Better for exhaustive search on large datasets
- ChromaDB, Turbopuffer: Other viable options depending on use case

**Target Chapter**: Chapter 1 (Kickstarting the Data Flywheel)

**What to Add**:

- New section after "Evaluation Tools" called "Vector Database Selection"
- Include comparison table with pros/cons
- Code examples showing LanceDB hybrid search implementation
- Decision tree for choosing based on use case

**Specific Location**: After the current evaluation tools section, before synthetic data generation

---

### 2. Document Parsing for Complex Layouts

**Source**: `cohort3/week-5-1.md`, `faq.md` (lines 599-607)

**Question**: "What's the best approach for parsing visual documents like quarterly reports with tables, images, and graphs?"

**Answer Summary**:

- Dockling: Free library, ~11 seconds per PDF
- Claude Sonnet: Good for extraction
- Reducto: 0.9 ± 0.1 accuracy vs Gemini's 0.84 ± 0.16
- Commercial tools worth the cost for time savings

**Target Chapter**: Chapter 5.2 (Implementing Multimodal Search)

**What to Add**:

- New subsection "Document Parsing Tool Comparison"
- Performance benchmarks for each tool
- Code example using Dockling
- Decision framework based on document types

**Specific Location**: After "The Document Processor" section, before "The Image Processor"

---

### 3. Chunking Very Long Documents (1,500+ pages)

**Source**: `cohort2/week3-summary.md`, `faq.md` (lines 288-297)

**Question**: "How do you approach chunking very long documents (1,500-2,000 pages)?"

**Answer Summary**:

- Start with page-level approach
- Use RAPTOR: cluster chunks, summarize clusters, use summaries for retrieval
- For legal docs, preprocess to colocate related content (laws with exemptions)
- Worth $10 in LLM calls for documents that don't change frequently

**Target Chapter**: Chapter 5.1 (Understanding Specialized Retrieval)

**What to Add**:

- New section "Handling Long Documents with RAPTOR"
- Step-by-step RAPTOR implementation
- Code for clustering and summarization
- Cost-benefit analysis example

**Specific Location**: After "Metadata Extraction Strategy" section

---

### 4. Fine-tuning Embedding Models

**Source**: `cohort2/week4-summary.md`, `faq.md` (lines 371-383)

**Question**: "What's the process for fine-tuning embedding models?"

**Answer Summary**:

- Good idea to train your own embedding model (not LLM)
- Costs ~$1.50 and 40 minutes on laptop
- 6,000 examples typically outperform closed-source models
- Useful for domain-specific concepts

**Target Chapter**: Chapter 2 (Converting Evaluations into Training Data)

**What to Add**:

- Detailed fine-tuning workflow with Sentence Transformers
- Cost and time benchmarks
- Example notebook for fine-tuning process
- When to fine-tune vs use pre-trained

**Specific Location**: Expand the "Fine-tuning Embeddings" section with practical implementation

---

### 5. Citation Generation and Attribution

**Source**: `cohort3/week-3-1.md`, Office Hours FAQ

**Question**: "How can we generate reliable citations and reduce error rates?"

**Answer Summary**:

- XML-based approaches with chunk IDs and text spans
- Fine-tuning can reduce errors from 4% to 0% with ~1,000 examples
- Handle medical abbreviations with hard negatives

**Target Chapter**: Chapter 3.3 (Quality of Life Improvements)

**What to Add**:

- Expand "Interactive Citations" with XML implementation
- Fine-tuning workflow for citation accuracy
- Code for chunk ID management
- Medical/technical abbreviation handling

**Specific Location**: Within the "Interactive Citations" section

---

### 6. Reasoning Models Integration

**Source**: `cohort3/week-5-2.md`, `faq.md` (lines 111-118)

**Question**: "What is your experience using reasoning models as the answer generator model?"

**Answer Summary**:

- Use O1/DeepSeek unless latency is a concern
- Stream thinking tokens to improve perceived latency
- "Think harder" button for user control
- Renders make system feel 45% faster

**Target Chapter**: Chapter 3.2 (Overcoming Latency)

**What to Add**:

- New section "Integrating Reasoning Models"
- Streaming thinking tokens implementation
- UI patterns for reasoning models
- Latency perception strategies

**Specific Location**: After "Streaming Structured Data" section

---

### 7. Cost Optimization Strategies

**Source**: `cohort2/week6-summary.md`, Multiple FAQ entries

**Question**: "How do we optimize costs while maintaining quality?"

**Answer Summary**:

- Token calculation before choosing approach
- Open source only 8x cheaper, may not justify engineering
- Focus on business value, not just cost savings
- Prompt caching can dramatically improve performance

**Target Chapter**: New Chapter 7 (Production Considerations)

**What to Add**:

- Cost calculation framework
- Token optimization strategies
- Prompt caching implementation (Anthropic vs OpenAI)
- ROI calculation examples

**Specific Location**: New chapter after Chapter 6

---

### 8. Multi-Agent vs Single-Agent Architecture

**Source**: `cohort3/week-4-2.md`, Office Hours discussions

**Question**: "When should we use multi-agent vs single-agent architectures?"

**Answer Summary**:

- Multi-agent works for read-only tasks
- Single-agent better when coordination needed
- Planning before execution improves reliability
- State machines effective for structured conversations

**Target Chapter**: Chapter 6.2 (Tool Interfaces and Implementation)

**What to Add**:

- Expanded section on architecture decisions
- State machine implementation example
- Planning patterns for complex workflows
- Coordination strategies

**Specific Location**: After "Dynamic Few-Shot Examples" section

---

### 9. Negative Feedback Collection

**Source**: `cohort3/week-2-2.md`, `faq.md` (lines 813-826)

**Question**: "How do we collect and validate negative feedback when documents aren't found?"

**Answer Summary**:

- Use flags when LLM can't find relevant documents
- Sample 1% of traffic for manual review
- Build Streamlit UI for labeling
- Easier to validate single chunk relevance than multiple

**Target Chapter**: Chapter 3.1 (Feedback Collection)

**What to Add**:

- Negative feedback detection implementation
- Streamlit labeling UI example
- Sampling strategies for review
- Integration with training data pipeline

**Specific Location**: After "Implicit Feedback" section

---

### 10. Multilingual RAG Implementation

**Source**: `cohort2/week5-summary.md`, `faq.md` (lines 610-618)

**Question**: "How do you handle multilingual RAG?"

**Answer Summary**:

- Cohere has best multilingual support
- Create synthetic questions in multiple languages
- Check recall rates across languages
- Avoid translation approach

**Target Chapter**: Chapter 5.2 (Implementing Multimodal Search)

**What to Add**:

- New section "Multilingual Search Strategies"
- Language detection and routing
- Multilingual evaluation framework
- Model selection for different languages

**Specific Location**: After multimodal search implementation

---

## Implementation Priority

1. **High Priority** (Most frequently asked):
   - Vector database selection (Chapter 1)
   - Fine-tuning embeddings (Chapter 2)
   - Citation generation (Chapter 3.3)
   - Long document handling (Chapter 5.1)

2. **Medium Priority** (Important for production):
   - Cost optimization (New Chapter 7)
   - Reasoning models (Chapter 3.2)
   - Document parsing tools (Chapter 5.2)
   - Negative feedback (Chapter 3.1)

3. **Lower Priority** (Specialized needs):
   - Multilingual support (Chapter 5.2)
   - Multi-agent architecture (Chapter 6.2)

## Next Steps

1. Create detailed outlines for each addition
2. Write code examples and implementations
3. Add evaluation metrics for each technique
4. Include cost-benefit analysis where applicable
5. Add decision trees for tool selection
