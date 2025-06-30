# Synthetic Question Generator 🔍

A Streamlit app for generating and evaluating synthetic search queries from conversation data using the WildChat dataset.

## Features

- **Data Loading**: Automatically loads 40 conversation examples from the WildChat-1M dataset
- **Conversation Display**: Shows conversation content with metadata (model, language, country, etc.)
- **Synthetic Question Generation**: Uses GPT-4o-mini to generate diverse search queries for each conversation
- **Intelligent Caching**: Results are cached on disk to avoid redundant API calls and speed up repeated processing
- **Quality Evaluation**: Provides UI for rating question quality and diversity
- **Interactive Interface**: Select specific conversations to process and view results

## Setup

### Prerequisites

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. Ensure you have all dependencies installed:
   ```bash
   cd /path/to/systematically-improving-rag/latest
   uv sync
   ```

### Running the App

#### Option 1: Using the run script (Recommended)
```bash
cd latest/capstone_project/03_synthetic_question_generation
python run_app.py
```

#### Option 2: Direct Streamlit command
```bash
cd latest/capstone_project/03_synthetic_question_generation
streamlit run streamlit_app.py
```
