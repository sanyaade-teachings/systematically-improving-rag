# Week 5: Structured Data and Metadata Enhancement

## Notebooks Overview

### 1. Generate Dataset.ipynb

This notebook demonstrates how to extract structured metadata from product images and descriptions.

**What You'll Do:**

- Define a product taxonomy in YAML format (categories, subcategories, attributes)
- Analyze clothing images from the irow/ClothingControlV2 dataset
- Use multimodal LLMs (GPT-4o) to identify clothing items and their attributes
- Extract structured product metadata (material, occasion, size, etc.)
- Implement Pydantic validation to ensure metadata conforms to taxonomy
- Upload the generated dataset to Hugging Face for sharing

You'll learn how to consistently extract structured metadata that enhances retrieval capabilities.

### 2. Metadata Filtering.ipynb

This notebook shows how to combine semantic search with structured metadata filtering.

**What You'll Do:**

- Ingest product data into LanceDB with embedded metadata
- Implement query understanding to extract filtering criteria
- Compare three retrieval approaches:
  1. Pure semantic search
  2. Pure metadata filtering
  3. Combined approach (vector + metadata)
- Evaluate performance using recall and MRR metrics
- Demonstrate how metadata filtering handles queries semantic search struggles with
- Improve product descriptions for better retrieval

You'll see how structured metadata dramatically improves retrieval for queries with specific requirements.

### 3. Text-2-SQL.ipynb

This notebook explores integrating database queries into RAG systems.

**What You'll Do:**

- Set up a SQLite database with product inventory and user data
- Generate synthetic user profiles and order history with Faker
- Create stock levels for products
- Implement safe SQL generation using read-only connections
- Build a system that determines when SQL queries are needed vs. retrieval
- Combine retrieval results with database query results
- Test the system with complex queries requiring both approaches

You'll learn how to safely integrate SQL generation to handle queries that require database access.

### 4. PDF-Parser.ipynb

This notebook focuses on extracting structured information from PDF documents with citation capabilities.

**What You'll Do:**

- Process PDF documents to extract text and layout information
- Implement bounding box tracking for visual citations
- Extract structured data from invoices and documents
- Validate extracted information against predefined schemas
- Create systems that can reference specific regions in source documents
- Handle complex PDF structures with tables and forms

You'll build a system that can extract structured information while maintaining citation integrity.

## Data Files and Assets

- `taxonomy.yml`: Product categories, attributes, and valid values
- `init.sql`: Database schema for product inventory and orders
- `data/invoice.pdf`: Sample invoice for PDF parsing
- `helpers.py`: Utility functions for taxonomy processing and validation

## Technical Requirements

- Required libraries: instructor, pydantic, lancedb, openai, sqlite3, faker, poppler, docling
- OpenAI API access (GPT-4o, GPT-4o-mini)
- Basic understanding of SQL and databases
- Familiarity with PDF document structure

## Why These Notebooks Matter

These notebooks move beyond simple semantic search to address complex real-world queries:

1. Queries with specific attribute requirements ("red sneakers under $100")
2. Questions requiring database access ("How many orders did user X place last month?")
3. Document information extraction with citation needs

## By combining vector search with structured filtering, SQL access, and document parsing, you'll build RAG systems capable of handling sophisticated user needs that pure semantic search can't address alone.

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

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
