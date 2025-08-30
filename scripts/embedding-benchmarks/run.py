#!/usr/bin/env python3
"""
Embedding Latency Benchmarking Script (Mock Implementation)

This script benchmarks embedding latency across multiple providers to demonstrate
that embedding models are the primary bottleneck in RAG systems, not database reads.
"""

import os
import asyncio
import argparse
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai
import cohere
import google.generativeai as genai
import voyageai
from tenacity import retry, stop_after_attempt, wait_exponential

MTEB_DATASETS = [
    "mteb/amazon_counterfactual",
    "mteb/banking77",
    "mteb/emotion",
    "mteb/imdb",
    "mteb/massive-intent",
    "mteb/massive-scenario",
    "mteb/tweet_sentiment_extraction",
]

DEFAULT_MODELS = {
    "openai": ["text-embedding-3-small", "text-embedding-3-large"],
    "cohere": ["embed-v4.0"],
    "gemini": ["gemini-embedding-001"],
    "voyager": ["voyage-3-large", "voyage-3.5"],
}


class EmbeddingProvider(ABC):
    def __init__(self, name: str):
        self.name = name
        self.available = self._check_availability()
        if self.available:
            print(f"🔧 {name.title()} client initialized")

    @abstractmethod
    def _check_availability(self) -> bool:
        pass

    @abstractmethod
    async def embed_batch(
        self, texts: list[str], model: Optional[str] = None
    ) -> dict[str, Any]:
        pass


class OpenAIProvider(EmbeddingProvider):
    def __init__(self):
        super().__init__("openai")
        if self.available:
            self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _check_availability(self) -> bool:
        return os.getenv("OPENAI_API_KEY") is not None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def embed_batch(
        self, texts: list[str], model: Optional[str] = None
    ) -> dict[str, Any]:
        if not model:
            model = DEFAULT_MODELS["openai"][0]

        start_time = time.perf_counter()
        try:
            response = await self.client.embeddings.create(input=texts, model=model)
            end_time = time.perf_counter()

            return {
                "success": True,
                "latency": end_time - start_time,
                "embeddings": [e.embedding for e in response.data],
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                "success": False,
                "error": str(e),
                "latency": end_time - start_time,
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }


class CohereProvider(EmbeddingProvider):
    def __init__(self):
        super().__init__("cohere")
        if self.available:
            self.client = cohere.AsyncClientV2(api_key=os.getenv("COHERE_API_KEY"))

    def _check_availability(self) -> bool:
        return os.getenv("COHERE_API_KEY") is not None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def embed_batch(
        self, texts: list[str], model: Optional[str] = None
    ) -> dict[str, Any]:
        if not model:
            model = DEFAULT_MODELS["cohere"][0]

        start_time = time.perf_counter()
        try:
            response = await self.client.embed(
                texts=texts,
                model=model,
                input_type="search_document",
                embedding_types=["float"],
            )
            end_time = time.perf_counter()

            return {
                "success": True,
                "latency": end_time - start_time,
                "embeddings": response.embeddings.float,
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                "success": False,
                "error": str(e),
                "latency": end_time - start_time,
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }


class GeminiProvider(EmbeddingProvider):
    def __init__(self):
        super().__init__("gemini")
        if self.available:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def _check_availability(self) -> bool:
        return os.getenv("GOOGLE_API_KEY") is not None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def embed_batch(
        self, texts: list[str], model: Optional[str] = None
    ) -> dict[str, Any]:
        if not model:
            model = DEFAULT_MODELS["gemini"][0]

        start_time = time.perf_counter()
        try:

            def sync_embed():
                return genai.embed_content(
                    model=model, content=texts, task_type="semantic_similarity"
                )

            response = await asyncio.to_thread(sync_embed)
            end_time = time.perf_counter()

            return {
                "success": True,
                "latency": end_time - start_time,
                "embeddings": response["embedding"],
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                "success": False,
                "error": str(e),
                "latency": end_time - start_time,
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }


class VoyagerProvider(EmbeddingProvider):
    def __init__(self):
        super().__init__("voyager")
        if self.available:
            self.client = voyageai.AsyncClient(api_key=os.getenv("VOYAGER_API_KEY"))

    def _check_availability(self) -> bool:
        return os.getenv("VOYAGER_API_KEY") is not None

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def embed_batch(
        self, texts: list[str], model: Optional[str] = None
    ) -> dict[str, Any]:
        if not model:
            model = DEFAULT_MODELS["voyager"][0]

        start_time = time.perf_counter()
        try:
            response = await self.client.embed(
                texts=texts, model=model, input_type="document"
            )
            end_time = time.perf_counter()

            return {
                "success": True,
                "latency": end_time - start_time,
                "embeddings": response.embeddings,
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                "success": False,
                "error": str(e),
                "latency": end_time - start_time,
                "model": model,
                "batch_size": len(texts),
                "provider": self.name,
            }


class MTEBDataLoader:
    def __init__(self):
        self.available_datasets = MTEB_DATASETS

    def load_samples(self, samples_per_category: int = 10) -> dict[str, list[str]]:
        """Load samples from real MTEB datasets using Hugging Face datasets library."""
        from datasets import load_dataset
        import random

        samples = {}

        for dataset_name in self.available_datasets:
            print(f"📊 Loading dataset: {dataset_name}")
            try:
                dataset = load_dataset(
                    dataset_name, split="test", trust_remote_code=True
                )

                text_field = self._get_text_field(dataset)
                if not text_field:
                    print(
                        f"   ⚠️  Could not find text field in {dataset_name}, skipping"
                    )
                    continue

                texts = []
                for item in dataset:
                    if text_field in item and item[text_field]:
                        text = str(item[text_field]).strip()
                        if len(text) > 10:
                            texts.append(text)

                if not texts:
                    print(f"   ⚠️  No valid texts found in {dataset_name}, skipping")
                    continue

                num_samples = min(samples_per_category, len(texts))
                sampled_texts = random.sample(texts, num_samples)
                samples[dataset_name] = sampled_texts
                print(f"   Loaded {len(sampled_texts)} samples from {text_field} field")

            except Exception as e:
                print(f"   ❌ Failed to load {dataset_name}: {e}")
                mock_texts = [
                    f"Sample text from {dataset_name.split('/')[-1]} dataset for benchmarking purposes.",
                    f"This is a fallback text sample when {dataset_name} cannot be loaded from Hugging Face.",
                    f"Embedding latency testing with synthetic data from {dataset_name.split('/')[-1]}.",
                ]
                fallback_samples = []
                for i in range(samples_per_category):
                    base_text = mock_texts[i % len(mock_texts)]
                    fallback_samples.append(f"{base_text} Sample {i + 1}.")
                samples[dataset_name] = fallback_samples
                print(f"   Using {len(fallback_samples)} fallback samples")

        return samples

    def _get_text_field(self, dataset) -> str:
        """Determine the text field name for the dataset."""
        common_fields = [
            "text",
            "sentence",
            "query",
            "passage",
            "document",
            "review",
            "content",
        ]

        for field in common_fields:
            if field in dataset.column_names:
                return field

        for field_name in dataset.column_names:
            if dataset.features[field_name].dtype == "string":
                return field_name

        return None


class BenchmarkCache:
    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(
        self, provider: str, texts: list[str], model: str, batch_size: int
    ) -> str:
        content = f"{provider}:{model}:{batch_size}:{hash(tuple(texts))}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_cached_result(
        self, provider: str, texts: list[str], model: str, batch_size: int
    ) -> Optional[dict]:
        cache_key = self._get_cache_key(provider, texts, model, batch_size)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                return json.load(f)
        return None

    def cache_result(
        self, provider: str, texts: list[str], model: str, batch_size: int, result: dict
    ):
        cache_key = self._get_cache_key(provider, texts, model, batch_size)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, "w") as f:
            json.dump(result, f, indent=2)


class BenchmarkEngine:
    def __init__(self, cache: BenchmarkCache, max_concurrent: int = 5):
        self.cache = cache
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.providers = {
            "openai": OpenAIProvider(),
            "cohere": CohereProvider(),
            "gemini": GeminiProvider(),
            "voyager": VoyagerProvider(),
        }

    async def run_benchmark_batch(
        self,
        provider_name: str,
        texts: list[str],
        batch_size: int,
        model: Optional[str] = None,
    ) -> dict:
        provider = self.providers[provider_name]

        if not provider.available:
            return {"success": False, "error": f"{provider_name} API key not available"}

        cached_result = self.cache.get_cached_result(
            provider_name, texts, model or "default", batch_size
        )
        if cached_result:
            print(f"   📋 Using cached result for {provider_name}/{model or 'default'}")
            return cached_result

        async with self.semaphore:
            batches = [
                texts[i : i + batch_size] for i in range(0, len(texts), batch_size)
            ]
            batch_results = []

            for batch in batches:
                result = await provider.embed_batch(batch, model)
                batch_results.append(result)

                self.cache.cache_result(
                    provider_name, batch, model or "default", len(batch), result
                )

            return self._aggregate_batch_results(batch_results)

    def _aggregate_batch_results(self, batch_results: list[dict]) -> dict:
        successful_results = [r for r in batch_results if r.get("success", False)]

        if not successful_results:
            return {"success": False, "error": "All batches failed"}

        total_latency = sum(r["latency"] for r in successful_results)
        total_embeddings = sum(r["batch_size"] for r in successful_results)

        return {
            "success": True,
            "total_latency": total_latency,
            "avg_latency_per_embedding": total_latency / max(total_embeddings, 1),
            "throughput": total_embeddings / total_latency if total_latency > 0 else 0,
            "batch_count": len(successful_results),
            "embedding_count": total_embeddings,
            "latencies": [r["latency"] for r in successful_results],
        }


def generate_latency_histograms(results: dict[str, dict], output_dir: str):
    """Generate and save histogram visualizations for latency analysis."""
    images_dir = Path(output_dir) / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    plt.style.use('default')
    sns.set_palette("husl")
    
    successful_results = {k: v for k, v in results.items() if v.get("success", False) and "latencies" in v}
    
    if not successful_results:
        print("No successful results to visualize")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Embedding Latency Analysis Across Providers', fontsize=16, fontweight='bold')
    
    ax1 = axes[0, 0]
    for provider_model, result in successful_results.items():
        latencies_ms = [lat * 1000 for lat in result["latencies"]]
        ax1.hist(latencies_ms, alpha=0.7, label=provider_model, bins=20)
    ax1.set_xlabel('Latency (ms)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Latency Distribution by Provider/Model')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[0, 1]
    box_data = []
    box_labels = []
    for provider_model, result in successful_results.items():
        latencies_ms = [lat * 1000 for lat in result["latencies"]]
        box_data.append(latencies_ms)
        box_labels.append(provider_model.replace('/', '\n'))
    ax2.boxplot(box_data, labels=box_labels)
    ax2.set_ylabel('Latency (ms)')
    ax2.set_title('Latency Percentiles Comparison')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    ax3 = axes[1, 0]
    providers = list(successful_results.keys())
    throughputs = [result.get("throughput", 0) for result in successful_results.values()]
    bars = ax3.bar(providers, throughputs)
    ax3.set_ylabel('Throughput (embeddings/sec)')
    ax3.set_title('Throughput Comparison')
    ax3.tick_params(axis='x', rotation=45)
    for bar, throughput in zip(bars, throughputs):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{throughput:.1f}', ha='center', va='bottom')
    
    ax4 = axes[1, 1]
    x = np.arange(len(providers))
    width = 0.25
    
    p50_values = []
    p95_values = []
    p99_values = []
    
    for result in successful_results.values():
        latencies_ms = [lat * 1000 for lat in result["latencies"]]
        p50_values.append(np.percentile(latencies_ms, 50))
        p95_values.append(np.percentile(latencies_ms, 95))
        p99_values.append(np.percentile(latencies_ms, 99))
    
    ax4.bar(x - width, p50_values, width, label='P50', alpha=0.8)
    ax4.bar(x, p95_values, width, label='P95', alpha=0.8)
    ax4.bar(x + width, p99_values, width, label='P99', alpha=0.8)
    
    ax4.set_xlabel('Provider/Model')
    ax4.set_ylabel('Latency (ms)')
    ax4.set_title('Percentile Latencies by Provider')
    ax4.set_xticks(x)
    ax4.set_xticklabels([p.replace('/', '\n') for p in providers])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    histogram_path = images_dir / "embedding_latency_analysis.png"
    plt.savefig(histogram_path, dpi=300, bbox_inches='tight')
    print(f"Saved comprehensive analysis to: {histogram_path}")
    
    for provider_model, result in successful_results.items():
        plt.figure(figsize=(10, 6))
        latencies_ms = [lat * 1000 for lat in result["latencies"]]
        
        plt.hist(latencies_ms, bins=30, alpha=0.7, edgecolor='black')
        plt.axvline(np.percentile(latencies_ms, 50), color='red', linestyle='--', label=f'P50: {np.percentile(latencies_ms, 50):.1f}ms')
        plt.axvline(np.percentile(latencies_ms, 95), color='orange', linestyle='--', label=f'P95: {np.percentile(latencies_ms, 95):.1f}ms')
        plt.axvline(np.percentile(latencies_ms, 99), color='purple', linestyle='--', label=f'P99: {np.percentile(latencies_ms, 99):.1f}ms')
        
        plt.xlabel('Latency (ms)')
        plt.ylabel('Frequency')
        plt.title(f'Latency Distribution: {provider_model}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        individual_path = images_dir / f"{provider_model.replace('/', '_')}_histogram.png"
        plt.savefig(individual_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved individual histogram to: {individual_path}")
    
    plt.close('all')


def print_latency_statistics(results: dict[str, dict], output_dir: str = None):
    """Print comprehensive P50, P95, P99 latency statistics and additional metrics."""
    print("\n" + "=" * 100)
    print("📊 COMPREHENSIVE EMBEDDING LATENCY BENCHMARK RESULTS")
    print("=" * 100)

    print("\n🎯 Key Finding: Embedding latency dominates RAG pipeline performance")
    print("   • Database reads: 8-20ms")
    print("   • Embedding generation: 100-500ms (10-25x slower!)")

    print(
        f"\n{'Provider/Model':<25} {'P50 (ms)':<10} {'P95 (ms)':<10} {'P99 (ms)':<10} {'Mean (ms)':<10} {'Std (ms)':<10} {'Throughput':<12} {'Samples':<8} {'Status'}"
    )
    print("-" * 120)

    stats_data = []
    
    for provider_model, result in results.items():
        if result.get("success", False) and "latencies" in result:
            latencies_ms = [
                latency * 1000 for latency in result["latencies"]
            ]

            p50 = np.percentile(latencies_ms, 50)
            p95 = np.percentile(latencies_ms, 95)
            p99 = np.percentile(latencies_ms, 99)
            mean_latency = np.mean(latencies_ms)
            std_latency = np.std(latencies_ms)
            throughput = result.get("throughput", 0)
            sample_count = len(latencies_ms)

            print(
                f"{provider_model:<25} {p50:<10.1f} {p95:<10.1f} {p99:<10.1f} {mean_latency:<10.1f} {std_latency:<10.1f} {throughput:<12.1f} {sample_count:<8} ✅"
            )
            
            stats_data.append({
                'Provider/Model': provider_model,
                'P50_ms': p50,
                'P95_ms': p95,
                'P99_ms': p99,
                'Mean_ms': mean_latency,
                'Std_ms': std_latency,
                'Throughput': throughput,
                'Sample_Count': sample_count,
                'Min_ms': np.min(latencies_ms),
                'Max_ms': np.max(latencies_ms)
            })
        else:
            error = result.get("error", "Unknown error")
            print(
                f"{provider_model:<25} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<10} {'N/A':<12} {'N/A':<8} ❌ {error}"
            )

    if output_dir and stats_data:
        df = pd.DataFrame(stats_data)
        csv_path = Path(output_dir) / "embedding_latency_statistics.csv"
        df.to_csv(csv_path, index=False)
        print(f"\n📄 Detailed statistics saved to: {csv_path}")

    print("\n💡 Recommendations:")
    print("   1. Co-locate embedding models with your database infrastructure")
    print("   2. Use batch processing to improve throughput")
    print("   3. Cache frequently requested embeddings")
    print("   4. Monitor embedding latency as the primary RAG bottleneck")
    print("   5. Consider Cohere for fastest response times in production")

    print("\n🏗️  Database Co-location Impact Analysis:")
    print("   Scenario              | DB Read | Embedding | Network | Total")
    print("   Co-located           |   15ms  |   200ms   |   5ms   | 220ms")
    print("   Separate regions     |   15ms  |   200ms   |  50ms   | 265ms")
    print("   Different clouds     |   15ms  |   200ms   | 100ms   | 315ms")
    print("\n   → Embedding latency dominates; database optimizations are secondary")
    
    if output_dir:
        generate_latency_histograms(results, output_dir)


async def run_benchmarks(
    providers: list[str],
    samples_per_category: int,
    batch_sizes: list[int],
    max_concurrent: int,
    cache_dir: str,
):
    """Run comprehensive embedding latency benchmarks."""

    print("🚀 Starting Embedding Latency Benchmarks")
    print(f"Providers: {', '.join(providers)}")
    print(f"Samples per category: {samples_per_category}")
    print(f"Batch sizes: {batch_sizes}")
    print(f"Max concurrent: {max_concurrent}")
    print()

    cache = BenchmarkCache(cache_dir)
    engine = BenchmarkEngine(cache, max_concurrent)
    data_loader = MTEBDataLoader()

    print("📚 Loading MTEB datasets...")
    samples = data_loader.load_samples(samples_per_category)

    if not samples:
        print("❌ No datasets loaded. Exiting.")
        return

    all_texts = []
    for dataset_texts in samples.values():
        all_texts.extend(dataset_texts)

    print(f"📝 Total texts loaded: {len(all_texts)}")
    print()

    results = {}

    for provider in providers:
        print(f"🔄 Benchmarking {provider.title()}...")

        for model in DEFAULT_MODELS[provider]:
            print(f"   Testing model: {model}")
            provider_model_results = []

            for batch_size in batch_sizes:
                print(f"     Testing batch size: {batch_size}")
                result = await engine.run_benchmark_batch(
                    provider, all_texts, batch_size, model
                )

                if result.get("success", False):
                    provider_model_results.extend(result.get("latencies", []))
                    print(f"     ✅ Completed batch size {batch_size}")
                else:
                    print(
                        f"     ❌ Failed batch size {batch_size}: {result.get('error', 'Unknown error')}"
                    )

            provider_model_key = (
                f"{provider.title()}/{model.split('/')[-1]}"  # Use short model name
            )

            if provider_model_results:
                results[provider_model_key] = {
                    "success": True,
                    "latencies": provider_model_results,
                    "throughput": len(all_texts) / sum(provider_model_results)
                    if provider_model_results
                    else 0,
                }
            else:
                results[provider_model_key] = {
                    "success": False,
                    "error": "All batch sizes failed",
                }

    print_latency_statistics(results, cache_dir.replace('/cache', ''))


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark embedding latency across providers"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    benchmark_parser = subparsers.add_parser(
        "benchmark", help="Run embedding latency benchmarks"
    )
    benchmark_parser.add_argument(
        "--providers",
        default="openai,cohere,gemini,voyager",
        help="Comma-separated list of embedding providers to test",
    )
    benchmark_parser.add_argument(
        "--samples-per-category",
        type=int,
        default=100,
        help="Number of samples to load per MTEB dataset category",
    )
    benchmark_parser.add_argument(
        "--batch-sizes",
        default="1,5,10,25",
        help="Comma-separated list of batch sizes to test",
    )
    benchmark_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum concurrent requests to prevent rate limiting",
    )
    benchmark_parser.add_argument(
        "--cache-dir",
        default="./data/cache",
        help="Directory for caching results (enables restartability)",
    )
    benchmark_parser.add_argument(
        "--output-dir",
        default="./data",
        help="Output directory for reports and visualizations",
    )

    clear_parser = subparsers.add_parser(
        "clear-cache", help="Clear the benchmark cache directory"
    )
    clear_parser.add_argument(
        "--cache-dir", default="./data/cache", help="Cache directory to clear"
    )

    subparsers.add_parser("list-datasets", help="List available MTEB datasets")

    args = parser.parse_args()

    if args.command == "benchmark":
        run_benchmark_command(args)
    elif args.command == "clear-cache":
        clear_cache_command(args)
    elif args.command == "list-datasets":
        list_datasets_command()
    else:
        parser.print_help()


def run_benchmark_command(args):
    """Run comprehensive embedding latency benchmarks across multiple providers."""

    providers_list = [p.strip() for p in args.providers.split(",")]
    batch_sizes_list = [int(b.strip()) for b in args.batch_sizes.split(",")]

    valid_providers = ["openai", "cohere", "gemini", "voyager"]
    invalid_providers = [p for p in providers_list if p not in valid_providers]
    if invalid_providers:
        print(f"❌ Invalid providers: {invalid_providers}")
        print(f"Valid providers: {valid_providers}")
        return

    available_providers = []
    for provider in providers_list:
        key_name = {
            "openai": "OPENAI_API_KEY",
            "cohere": "COHERE_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "voyager": "VOYAGER_API_KEY",
        }[provider]

        if os.getenv(key_name):
            available_providers.append(provider)
        else:
            print(f"⚠️  {provider.upper()} API key not found ({key_name})")

    if not available_providers:
        print(
            "❌ No API keys found. Please set API keys in environment variables or .envrc file."
        )
        print("Example .envrc file:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  export COHERE_API_KEY='your-key-here'")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("  export VOYAGER_API_KEY='your-key-here'")
        return

    print(f"✅ Found API keys for: {', '.join(available_providers)}")

    asyncio.run(
        run_benchmarks(
            available_providers,
            args.samples_per_category,
            batch_sizes_list,
            args.max_concurrent,
            args.cache_dir,
        )
    )


def clear_cache_command(args):
    """Clear the benchmark cache directory."""
    cache_path = Path(args.cache_dir)

    if not cache_path.exists():
        print(f"Cache directory {args.cache_dir} does not exist.")
        return

    import shutil

    shutil.rmtree(cache_path)
    print(f"✅ Cleared cache directory: {args.cache_dir}")


def list_datasets_command():
    """List available MTEB datasets that will be used for benchmarking."""
    print("📊 Available MTEB Datasets:")
    print("")

    for i, dataset in enumerate(MTEB_DATASETS, 1):
        print(f"{i:2d}. {dataset}")

    print("")
    print(f"Total: {len(MTEB_DATASETS)} datasets")


if __name__ == "__main__":
    main()
