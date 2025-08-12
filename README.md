# Systematically Improving RAG Applications

A comprehensive course teaching data-driven approaches to building and improving Retrieval-Augmented Generation (RAG) systems. This repository contains course materials, code examples, and a companion book.

## 🎓 Take the Course

All of this material is supported by the **Systematically Improving RAG Course**.

[**Click here to get 20% off →**](https://maven.com/applied-llms/rag-playbook?promoCode=EBOOK)

## Course Overview

This course teaches you how to systematically improve RAG applications through:

- Data-driven evaluation and metrics
- Embedding fine-tuning and optimization
- Query understanding and routing
- Structured data integration
- Production deployment strategies

### The RAG Flywheel

The core philosophy centers around the "RAG Flywheel" - a continuous improvement cycle that emphasizes:

1. **Measure**: Establish benchmarks and evaluation metrics
2. **Analyze**: Understand failure modes and user patterns
3. **Improve**: Apply targeted optimizations
4. **Iterate**: Continuous refinement based on real-world usage

## Repository Structure

```text
.
├── cohort_1/        # First cohort materials (6 weeks)
├── cohort_2/        # Second cohort materials (weeks 0-6)
├── latest/          # Current course version with latest updates
│   ├── week0/       # Getting started with Jupyter, LanceDB, and evals
│   ├── week1/       # RAG evaluation foundations
│   ├── week2/       # Embedding fine-tuning
│   ├── week4/       # Query understanding and routing
│   ├── week5/       # Structured data and metadata
│   ├── week6/       # Tool selection and product integration
│   ├── case_study/  # Comprehensive WildChat project
│   └── extra_kura/  # Advanced notebooks on clustering and classifiers
├── docs/            # MkDocs documentation source
│   ├── workshops/   # Detailed chapter guides (0-7) aligned with course weeks
│   ├── talks/       # Industry expert presentations and case studies
│   ├── office-hours/# Q&A summaries from cohorts 2 and 3
│   ├── assets/      # Images and diagrams for documentation
│   └── misc/        # Additional learning resources
├── data/            # CSV files from industry talks
├── md/              # Markdown conversions of notebooks
└── mkdocs.yml       # Documentation configuration
```

## Course Structure: Weekly Curriculum & Book Chapters

The course follows a 6-week structure where each week corresponds to specific workshop chapters in the companion book:

### Week 1: Starting the Flywheel

- **Book Coverage**: Chapter 0 (Introduction) + Chapter 1 (Starting the Flywheel with Data)
- **Topics**:
  - Shifting from static implementations to continuously improving products
  - Overcoming the cold-start problem through synthetic data generation
  - Establishing meaningful metrics aligned with business goals
  - RAG as a recommendation engine wrapped around language models

### Week 2: From Evaluation to Enhancement

- **Book Coverage**: Chapter 2 (From Evaluation to Product Enhancement)
- **Topics**:
  - Transforming evaluation insights into concrete improvements
  - Fine-tuning embeddings with Cohere and open-source models
  - Re-ranking strategies and targeted capability development

### Week 3: User Experience Design

- **Book Coverage**: Chapter 3 (UX - 3 parts)
  - Part 1: Design Principles
  - Part 2: Feedback Collection
  - Part 3: Iterative Improvement
- **Topics**:
  - Building interfaces that delight users and gather feedback
  - Creating virtuous cycles of improvement
  - Continuous refinement based on user interaction

### Week 4: Query Understanding & Topic Modeling

- **Book Coverage**: Chapter 4 (Topic Modeling - 2 parts)
  - Part 1: Analysis - Segmenting users and queries
  - Part 2: Prioritization - High-value opportunities
- **Topics**:
  - Query classification with BERTopic
  - Pattern discovery in user queries
  - Creating improvement roadmaps based on usage patterns

### Week 5: Multimodal & Structured Data

- **Book Coverage**: Chapter 5 (Multimodal - 2 parts)
  - Part 1: Understanding different content types
  - Part 2: Implementation strategies
- **Topics**:
  - Working with documents, images, tables, and structured data
  - Metadata filtering and Text-to-SQL integration
  - PDF parsing and multimodal embeddings

### Week 6: Architecture & Product Integration

- **Book Coverage**: Chapter 6 (Architecture - 3 parts)
  - Part 1: Intelligent routing to specialized components
  - Part 2: Building and integrating specialized tools
  - Part 3: Creating unified product experiences
- **Topics**:
  - Tool evaluation and selection
  - Performance optimization strategies
  - Streaming implementations and production deployment

### Capstone Project

A comprehensive project using the WildChat dataset that covers:

- Data exploration and understanding
- Vector database integration (ChromaDB, LanceDB, Turbopuffer)
- Synthetic question generation
- Summarization strategies
- Complete test suite implementation

## Technologies Used

- **LLM APIs**: OpenAI, Anthropic, Cohere
- **Vector Databases**: LanceDB, ChromaDB, Turbopuffer
- **ML/AI Frameworks**: Sentence-transformers, BERTopic, Transformers
- **Evaluation Tools**: Braintrust, Pydantic-evals
- **Monitoring**: Logfire, production monitoring strategies
- **Data Processing**: Pandas, NumPy, BeautifulSoup, SQLModel
- **Visualization**: Matplotlib, Seaborn, Streamlit
- **CLI Framework**: Typer + Rich for interactive command-line tools
- **Document Processing**: Docling for PDF parsing and analysis

## Course Book & Documentation

The `/docs` directory contains a comprehensive book built with MkDocs that serves as the primary learning resource:

### Book Structure

- **Introduction & Core Concepts**: The RAG Flywheel philosophy and product-first thinking
- **Workshop Chapters (0-6)**: Detailed guides that map directly to each course week
- **Office Hours**: Q&A summaries from Cohorts 2 and 3 with real-world implementation insights
- **Industry Talks**: Expert presentations including:
  - RAG Anti-patterns in the Wild
  - Semantic Search Over the Web
  - Understanding Embedding Performance
  - Online Evals and Production Monitoring
  - RAG Without APIs (Browser-based approaches)

### Key Themes in the Book

1. **Product-First Thinking**: Treating RAG as an evolving product, not a static implementation
2. **Data-Driven Improvement**: Using metrics, evaluations, and user feedback to guide development
3. **Systematic Approach**: Moving from ad-hoc tweaking to structured improvement processes
4. **User-Centered Design**: Focusing on user value and experience, not just technical capabilities
5. **Continuous Learning**: Building systems that improve with every interaction

To build and view the documentation:

```bash
# Serve documentation locally (live reload)
mkdocs serve

# Build static documentation
mkdocs build
```

## Getting Started

### Prerequisites
- Python 3.11 (required - the project uses specific features from this version)
- `uv` package manager (recommended) or `pip`

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv install
   
   # Or using pip
   pip install -e .
   ```
3. Start with `/latest/week0/` for the most up-to-date content
4. Follow the notebooks in sequential order within each week
5. Reference the corresponding book chapters in `/docs` for deeper understanding

### Code Quality

Before committing changes, run:
```bash
# Format and fix code issues
uv run ruff check --fix --unsafe-fixes .
uv run ruff format .
```

## Philosophy

This course emphasizes:

- **Systematic Improvement**: Data-driven approaches over guesswork
- **Product Thinking**: Building RAG systems that solve real problems
- **Practical Application**: Real-world datasets and examples
- **Evaluation-First**: Measure before and after every change
- **Continuous Learning**: The field evolves rapidly; the flywheel helps you adapt

## Additional Resources

- Industry talk transcripts in `/data/`
- Office hours recordings summaries in `/docs/office_hours/`
- Advanced notebooks in `/latest/extra_kura/` for clustering and classification topics
- Complete case study implementation in `/latest/case_study/`

## License

This is educational material for the "Systematically Improving RAG Applications" course.

---

## 📧 Free Email Course

Want to learn more about RAG? Take our free email course and get the latest news and information about RAG techniques and best practices.

[**Sign up for the free RAG Crash Course →**](https://fivesixseven.ck.page/rag-crash-course){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
