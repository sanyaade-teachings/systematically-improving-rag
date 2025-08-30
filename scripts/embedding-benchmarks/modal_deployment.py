"""
Modal Labs deployment for multi-region embedding latency benchmarking.

This script demonstrates how to use Modal to run embedding benchmarks across
different regions for comprehensive latency analysis.
"""

import modal
from pathlib import Path
import json
import os

app = modal.App("embedding-benchmarks")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "numpy",
        "pandas", 
        "matplotlib",
        "seaborn",
        "datasets",
        "openai",
        "cohere",
        "google-generativeai",
        "voyageai",
        "typer",
        "rich"
    ])
    .copy_local_dir(".", "/app")
)

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("openai-api-key"),
        modal.Secret.from_name("cohere-api-key"), 
        modal.Secret.from_name("google-api-key"),
        modal.Secret.from_name("voyager-api-key", required=False)
    ],
    timeout=3600,
    cpu=2,
    memory=4096
)
def run_benchmark_in_region(
    region: str,
    providers: str = "openai,cohere,gemini",
    samples_per_category: int = 100,
    batch_sizes: str = "1,5,10,25"
):
    """Run embedding benchmark in a specific region."""
    import subprocess
    import sys
    
    os.chdir("/app")
    
    cmd = [
        sys.executable, "run.py", "benchmark",
        "--providers", providers,
        "--samples-per-category", str(samples_per_category),
        "--batch-sizes", batch_sizes,
        "--output-dir", f"./data/{region}"
    ]
    
    print(f"Running benchmark in region: {region}")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    metadata = {
        "region": region,
        "providers": providers,
        "samples_per_category": samples_per_category,
        "batch_sizes": batch_sizes,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
    
    return metadata

@app.function(
    image=image,
    timeout=7200,
    cpu=1,
    memory=2048
)
def run_multi_region_benchmarks(
    regions: list[str] = ["us-east", "us-west", "europe"],
    providers: str = "openai,cohere,gemini",
    samples_per_category: int = 100
):
    """Run benchmarks across multiple regions and aggregate results."""
    results = {}
    
    for region in regions:
        print(f"Starting benchmark for region: {region}")
        try:
            result = run_benchmark_in_region.remote(
                region=region,
                providers=providers,
                samples_per_category=samples_per_category
            )
            results[region] = result
            print(f"Completed benchmark for region: {region}")
        except Exception as e:
            print(f"Failed benchmark for region {region}: {str(e)}")
            results[region] = {"success": False, "error": str(e)}
    
    return results

@app.function(
    image=image,
    volumes={"/results": modal.Volume.from_name("benchmark-results", create_if_missing=True)},
    timeout=1800
)
def aggregate_regional_results(results_data: dict):
    """Aggregate and visualize results from multiple regions."""
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pathlib import Path
    
    output_dir = Path("/results")
    
    all_stats = []
    
    for region, result in results_data.items():
        if result.get("success", False):
            try:
                csv_path = Path(f"./data/{region}/embedding_latency_statistics.csv")
                if csv_path.exists():
                    df = pd.read_csv(csv_path)
                    df['Region'] = region
                    all_stats.append(df)
            except Exception as e:
                print(f"Failed to load results for {region}: {e}")
    
    if not all_stats:
        print("No successful results to aggregate")
        return
    
    combined_df = pd.concat(all_stats, ignore_index=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Multi-Region Embedding Latency Comparison', fontsize=16, fontweight='bold')
    
    pivot_p50 = combined_df.pivot(index='Provider/Model', columns='Region', values='P50_ms')
    pivot_p50.plot(kind='bar', ax=axes[0,0], title='P50 Latency by Region')
    axes[0,0].set_ylabel('Latency (ms)')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    pivot_p95 = combined_df.pivot(index='Provider/Model', columns='Region', values='P95_ms')
    pivot_p95.plot(kind='bar', ax=axes[0,1], title='P95 Latency by Region')
    axes[0,1].set_ylabel('Latency (ms)')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    pivot_throughput = combined_df.pivot(index='Provider/Model', columns='Region', values='Throughput')
    pivot_throughput.plot(kind='bar', ax=axes[1,0], title='Throughput by Region')
    axes[1,0].set_ylabel('Embeddings/sec')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    heatmap_data = combined_df.pivot_table(index='Provider/Model', columns='Region', values='P50_ms')
    sns.heatmap(heatmap_data, ax=axes[1,1], annot=True, fmt='.1f', cmap='YlOrRd')
    axes[1,1].set_title('P50 Latency Heatmap (ms)')
    
    plt.tight_layout()
    
    comparison_path = output_dir / 'multi_region_comparison.png'
    plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
    print(f"Saved regional comparison to: {comparison_path}")
    
    combined_csv_path = output_dir / 'combined_regional_results.csv'
    combined_df.to_csv(combined_csv_path, index=False)
    print(f"Saved combined results to: {combined_csv_path}")
    
    return str(comparison_path)

@app.local_entrypoint()
def main(
    regions: str = "us-east,us-west,europe",
    providers: str = "openai,cohere,gemini",
    samples_per_category: int = 100
):
    """Main entrypoint for multi-region benchmarking."""
    region_list = [r.strip() for r in regions.split(",")]
    
    print(f"Starting multi-region benchmarks for regions: {region_list}")
    print(f"Providers: {providers}")
    print(f"Samples per category: {samples_per_category}")
    
    results = run_multi_region_benchmarks.remote(
        regions=region_list,
        providers=providers,
        samples_per_category=samples_per_category
    )
    
    print("Aggregating results...")
    comparison_path = aggregate_regional_results.remote(results)
    
    print(f"Multi-region benchmark complete!")
    print(f"Results visualization: {comparison_path}")
    
    return results

if __name__ == "__main__":
    import typer
    typer.run(main)
