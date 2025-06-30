# Capstone Project - Systematically Improving RAG

One of the goals I have right now is to do some of the processes I would undergo when building out back applications. The first thing really is to understand the data source that I'm working with. In this example, the text chunk I'm working with is the first message in WildChat. And in particular, this idea that I can use conversations because everyone at some point will be analyzing conversation data.

## Project Structure

### 01_exploring_wildchat.ipynb

This notebook is a work in progress. It's a simple exploration of the WildChat dataset. It's not a complete analysis, but it's a good starting point.

### 02_exploring_wildchat_with_ai.ipynb

This notebook is a work in progress. It's a simple exploration of the WildChat dataset using AI. It's not a complete analysis, but it's a good starting point.

### 03_synthetic_question_generation/

A Streamlit application for generating synthetic search queries from conversation data using two different approaches:

- **Version 1**: User-focused queries (how users might search for similar conversations)
- **Version 2**: Pattern-focused queries (for research and conversation analysis)

#### Running the Synthetic Question Generator

**Important**: Run all Streamlit applications from the `capstone_project` directory to ensure proper module imports.

```bash
# Navigate to the capstone project directory
cd latest/capstone_project

# Run the synthetic question generator
streamlit run 03_synthetic_question_generation/streamlit_app.py
```

## Environment Setup

Ensure you have your OpenAI API key configured:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

Install dependencies:

```bash
uv sync
```