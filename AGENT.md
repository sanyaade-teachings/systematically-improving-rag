# AGENT.md - Systematically Improving RAG Applications

## Build/Test Commands

- Install dependencies: `uv install` or `pip install -e .`
- Run tests: `pytest` (pytest>=8.4.1 with pytest-asyncio>=1.0.0)
- Build docs: `mkdocs serve` (local) or `mkdocs build` (static)
- Package management: Always use `uv` instead of `pip` (e.g., `uv add <package>`)

## Architecture & Structure

- **Main course content**: `latest/` (current version), `cohort_1/`, `cohort_2/` (previous versions)
- **Weekly modules**: `week0/` (setup), `week1/` (evaluation), `week2/` (embedding tuning), `week4/` (query understanding), `week5/` (multimodal), `week6/` (architecture)
- **Capstone project**: `latest/capstone_project/` - comprehensive WildChat dataset implementation
- **Documentation**: `docs/` (MkDocs book), `md/` (notebook conversions)
- **Technologies**: ChromaDB/LanceDB/Turbopuffer (vector DBs), OpenAI/Anthropic/Cohere (LLMs), Sentence-transformers, BERTopic

## Code Style & Conventions

- **Reading level**: Write at 9th-grade level for educational content
- **CLI tools**: Use `typer` + `rich` for command-line interfaces, never emojis in code
- **Async preferred**: Use async/await over synchronous code when possible
- **Data handling**: Use `pydantic` for validation, `pandas` for processing
- **Console output**: Use `rich.console` with text indicators ("Success:", "Error:", "Warning:")
- **Educational**: Add markdown explanations between code sections in notebooks
- **Dependencies**: Core ML stack includes sentence-transformers, transformers, pandas, numpy, scikit-learn

## Key Patterns

- RAG Flywheel: Measure → Analyze → Improve → Iterate
- Evaluation-first approach using Braintrust/pydantic-evals
- Vector database integration with filtering and metadata
- Synthetic data generation for cold-start problems
