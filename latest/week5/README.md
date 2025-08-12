# Week 5: Structured Data and Metadata Enhancement

## Overview

This week addresses a fundamental limitation of pure semantic search: the inability to handle queries with specific constraints or requirements. While semantic search excels at finding conceptually similar content, it struggles with queries like "red sneakers under $100" or "invoices from Q3 2023." By incorporating structured metadata and database integration, you can build RAG systems that handle these complex, real-world queries effectively.

The approach combines the strengths of multiple retrieval methods: vector search for semantic understanding, metadata filtering for specific constraints, SQL queries for database information, and structured extraction from documents. This multi-modal retrieval strategy enables your RAG system to answer questions that would be impossible with semantic search alone, dramatically expanding its practical utility.

## Learning Objectives

By the end of this week, you'll be able to:

- Extract structured metadata from unstructured content using multimodal LLMs
- Implement hybrid retrieval combining vector search with metadata filtering
- Safely integrate SQL generation for database queries in RAG systems
- Parse PDF documents while maintaining citation capabilities
- Build query understanding systems that route to appropriate retrieval methods
- Validate extracted data against predefined schemas
- Measure performance improvements from structured data integration

## Notebooks

### 1. Generate Dataset.ipynb

**Purpose**: Extract structured metadata from product images and descriptions using multimodal AI

**What You'll Learn**:

- Defining structured taxonomies for consistent metadata
- Using multimodal LLMs for image analysis
- Pydantic validation for schema enforcement
- Building datasets that combine visual and textual information

**What You'll Build**:

- Product taxonomy with categories and attributes
- Metadata extraction pipeline for clothing items
- Validated dataset ready for hybrid retrieval

### 2. Metadata Filtering.ipynb

**Purpose**: Implement hybrid retrieval combining semantic search with structured metadata filtering

**What You'll Learn**:

- Query understanding for extracting filter criteria
- Implementing hybrid search in LanceDB
- Comparing pure semantic vs. hybrid approaches
- Optimizing retrieval for constraint-based queries

**What You'll Build**:

- Hybrid retrieval system with metadata filtering
- Query parser extracting structured constraints
- Performance comparisons showing improvement areas

### 3. Text-2-SQL.ipynb

**Purpose**: Safely integrate SQL generation for handling queries requiring database access

**What You'll Learn**:

- Safe SQL generation with read-only constraints
- Query routing between retrieval and database access
- Combining results from multiple data sources
- Building realistic test databases with synthetic data

**What You'll Build**:

- SQLite database with inventory and user data
- Safe Text-2-SQL system with validation
- Hybrid query answering combining retrieval and SQL

### 4. PDF-Parser.ipynb

**Purpose**: Extract structured information from PDFs while maintaining precise citation capabilities

**What You'll Learn**:

- PDF parsing with layout preservation
- Bounding box tracking for visual citations
- Structured extraction from forms and tables
- Schema validation for extracted data

**What You'll Build**:

- PDF parsing system with citation support
- Structured data extractor for invoices
- Visual reference system for source attribution

## Key Concepts

- **Hybrid Retrieval**: Combining vector search with metadata filtering for constraint-based queries
- **Query Understanding**: Parsing natural language to extract structured constraints and filters
- **Schema Validation**: Ensuring extracted data conforms to predefined structures
- **Safe SQL Generation**: Creating database queries with security constraints and validation
- **Multimodal Extraction**: Using vision-language models to extract structured data from images
- **Citation Tracking**: Maintaining references to exact locations in source documents
- **Query Routing**: Determining which retrieval method(s) to use based on query type

## Prerequisites

### Knowledge Requirements

- Understanding of vector search from previous weeks
- Basic SQL knowledge for database queries
- Familiarity with structured data concepts (schemas, validation)

### Technical Requirements

- Python packages: `instructor`, `pydantic`, `lancedb`, `openai`, `sqlite3`, `faker`, `poppler-utils`, `docling`, `pillow`
- API keys: OpenAI API access with GPT-4o and GPT-4o-mini
- Hardware: No GPU required
- System: Poppler installed for PDF processing

## Project Structure

```text
week5/
├── README.md
├── Generate Dataset.ipynb
├── Metadata Filtering.ipynb
├── Text-2-SQL.ipynb
├── PDF-Parser.ipynb
├── data/
│   ├── invoice.pdf
│   ├── products/
│   └── database/
├── taxonomy.yml
├── init.sql
└── helpers.py
```

## Datasets

- **ClothingControlV2**: Product images from Hugging Face for metadata extraction exercises
- **Product Database**: Synthetic inventory with stock levels, pricing, and user order history
- **Invoice Samples**: PDF documents demonstrating structured extraction challenges

## Expected Outcomes

After completing this week's materials, you'll have:

1. A multimodal metadata extraction pipeline for product data
2. Hybrid retrieval system outperforming pure semantic search by 20-40% on constraint queries
3. Safe Text-2-SQL integration for database queries
4. PDF parsing system with precise citation capabilities
5. Understanding of when to apply each retrieval method

## Common Issues and Solutions

### Issue 1: Metadata extraction producing inconsistent results

**Solution**: Refine your taxonomy to be more specific and add validation rules. Use few-shot examples in your extraction prompts.

### Issue 2: SQL injection concerns with Text-2-SQL

**Solution**: Always use read-only database connections and validate generated SQL against a whitelist of allowed operations.

### Issue 3: PDF parsing missing content or layout

**Solution**: Ensure Poppler is properly installed. For complex PDFs, consider using different extraction modes in docling.

## Next Steps

- Complete notebooks in order as concepts build progressively
- Experiment with different metadata schemas for your use case
- Review Week 6 to see how tool selection extends these concepts
- Consider implementing hybrid retrieval in your production systems

## Additional Resources

- [LanceDB Hybrid Search Documentation](https://lancedb.github.io/lancedb/hybrid_search/)
- [Pydantic Data Validation](https://docs.pydantic.dev/)
- [SQL Injection Prevention](https://owasp.org/www-community/attacks/SQL_Injection)
- [Docling PDF Parser](https://github.com/DS4SD/docling)

---

## **Note**: The techniques in this week are essential for production RAG systems. Real-world queries often contain specific constraints that pure semantic search cannot handle, making structured data integration a critical capability.

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
