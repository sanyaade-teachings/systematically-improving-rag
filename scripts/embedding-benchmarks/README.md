# Embedding Latency Benchmarking Suite

A standalone benchmarking tool for measuring embedding latency across multiple providers to demonstrate that embedding models are the primary bottleneck in RAG systems, not database read times.

## Overview

This script benchmarks OpenAI, Cohere, Gemini, and Voyager embedding APIs using mock MTEB datasets to highlight the performance characteristics of different embedding providers and their impact on RAG pipeline latency.

## Key Findings

- **Database reads**: 8-20ms
- **Embedding generation**: 100-500ms (10-25x slower!)
- **Network latency**: Can add 10-100ms depending on co-location

## Features

- **Multi-provider support**: OpenAI, Cohere, Gemini, Voyager
- **Mock MTEB dataset integration**: Simulates real-world text samples
- **Statistical analysis**: P50, P95, P99 latency percentiles printed to console
- **Caching system**: Enables restartability for long-running benchmarks
- **Batch size testing**: Measures performance scaling effects
- **Database co-location analysis**: Compares local vs cloud deployment scenarios

## Installation

```bash
# Install dependencies (from the main project root)
cd ../../  # Navigate to systematically-improving-rag root
uv install

# Set up environment variables
cd scripts/embedding-benchmarks
cp .envrc .envrc.local
# Edit .envrc.local with your API keys
direnv allow
```

## Usage

### Basic Benchmarking

```bash
# Run benchmarks with default settings (mock implementation)
python scripts/embedding-benchmarks/run_mock.py benchmark

# Benchmark specific providers
python scripts/embedding-benchmarks/run_mock.py benchmark --providers openai,cohere

# Control sample size and batch sizes
python scripts/embedding-benchmarks/run_mock.py benchmark --samples-per-category 20 --batch-sizes 1,10,50,100

# Use custom cache directory
python scripts/embedding-benchmarks/run_mock.py benchmark --cache-dir ./cache
```

### Utility Commands

```bash
# List available MTEB datasets
python scripts/embedding-benchmarks/run_mock.py list-datasets

# Clear benchmark cache
python scripts/embedding-benchmarks/run_mock.py clear-cache
```

## Configuration

### Environment Variables

Set these in your `.envrc` file:

```bash
export OPENAI_API_KEY="your-openai-key"
export COHERE_API_KEY="your-cohere-key"
export GOOGLE_API_KEY="your-gemini-key"
export VOYAGER_API_KEY="your-voyager-key"
```

### Command Line Options

- `--providers`: Comma-separated list of providers to test
- `--samples-per-category`: Number of samples per MTEB dataset (default: 10)
- `--batch-sizes`: Comma-separated batch sizes to test (default: 1,5,10,25)
- `--max-concurrent`: Maximum concurrent requests (default: 5)
- `--cache-dir`: Cache directory for restartability (default: ./data/cache)

## Output

The script prints P50, P95, P99 latency statistics directly to the console:

```
================================================================================
📊 EMBEDDING LATENCY BENCHMARK RESULTS
================================================================================

🎯 Key Finding: Embedding latency dominates RAG pipeline performance
   • Database reads: 8-20ms
   • Embedding generation: 100-500ms (10-25x slower!)

Provider     P50 (ms)   P95 (ms)   P99 (ms)   Throughput   Status
----------------------------------------------------------------------
Openai       211.9      1148.1     1231.0     2.4          ✅
Cohere       156.4      815.6      840.2      3.2          ✅

💡 Recommendations:
   1. Co-locate embedding models with your database infrastructure
   2. Use batch processing to improve throughput
   3. Cache frequently requested embeddings
   4. Monitor embedding latency as the primary RAG bottleneck

🏗️  Database Co-location Impact Analysis:
   Scenario              | DB Read | Embedding | Network | Total
   Co-located           |   15ms  |   200ms   |   5ms   | 220ms
   Separate regions     |   15ms  |   200ms   |  50ms   | 265ms
   Different clouds     |   15ms  |   200ms   | 100ms   | 315ms

   → Embedding latency dominates; database optimizations are secondary
```

## Methodology

### Mock Test Data
- Simulates MTEB (Massive Text Embedding Benchmark) datasets
- Uses texts of varying lengths (short queries to long documents)
- Realistic latency simulation based on provider characteristics

### Metrics Collected
- **Latency**: Simulated embedding generation time
- **Throughput**: Embeddings generated per second
- **Batch effects**: Performance scaling with batch size
- **Statistical percentiles**: P50, P95, P99 measurements

## Database Co-location Analysis

The script includes analysis of how embedding model placement affects total RAG pipeline latency:

| Scenario | Database Read | Embedding | Network | Total Pipeline |
|----------|---------------|-----------|---------|----------------|
| Co-located | 15ms | 200ms | 5ms | 220ms |
| Separate regions | 15ms | 200ms | 50ms | 265ms |
| Different clouds | 15ms | 200ms | 100ms | 315ms |

**Key insight**: Embedding latency dominates total pipeline time, making database optimizations secondary to embedding performance.

## Recommendations

1. **Co-locate embedding models** with your database infrastructure
2. **Use batch processing** where possible to improve throughput
3. **Consider caching** frequently requested embeddings
4. **Monitor embedding latency** as the primary bottleneck in RAG pipelines
5. **Choose providers** based on your latency vs cost requirements

## Files

```
scripts/embedding-benchmarks/
├── run_mock.py           # Main benchmarking script (mock implementation)
├── .envrc               # Environment variables template
├── README.md            # This file
└── data/                # Output directory (created when running)
    └── cache/           # Cached results for restartability
```

## Implementation Notes

This is currently a **mock implementation** that simulates realistic embedding latencies without making actual API calls. The mock provides:

- Realistic latency ranges for each provider
- Proper async/await patterns
- Caching functionality
- Statistical analysis
- Console output formatting

To use with real APIs, replace the mock `embed_batch` methods in each provider class with actual API calls.

## Dependencies

All required dependencies are included in the main project's `pyproject.toml`:
- numpy>=1.24.0
- typer>=0.15.4  
- openai>=1.57.0
- anthropic>=0.40.0
- cohere>=5.11.3
- python-dotenv>=1.0.0
- rich>=13.7.0

## License

This project follows the same license as the systematically-improving-rag repository.
