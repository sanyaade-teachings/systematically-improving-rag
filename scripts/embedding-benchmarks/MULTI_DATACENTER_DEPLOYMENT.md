# Multi-Datacenter Embedding Latency Testing Strategy

## Overview

This document outlines strategies for running embedding latency benchmarks across multiple datacenters to understand regional performance differences and optimize RAG system deployment.

## Deployment Options

### 1. Cloud Provider Multi-Region Deployment

#### AWS Regions
```bash
# US East (Virginia)
aws ec2 run-instances --region us-east-1 --image-id ami-0abcdef1234567890 --instance-type t3.medium

# US West (Oregon)  
aws ec2 run-instances --region us-west-2 --image-id ami-0abcdef1234567890 --instance-type t3.medium

# Europe (Ireland)
aws ec2 run-instances --region eu-west-1 --image-id ami-0abcdef1234567890 --instance-type t3.medium
```

#### GCP Regions
```bash
# US Central
gcloud compute instances create benchmark-us-central --zone=us-central1-a --machine-type=e2-medium

# US East
gcloud compute instances create benchmark-us-east --zone=us-east1-b --machine-type=e2-medium

# Europe West
gcloud compute instances create benchmark-europe --zone=europe-west1-b --machine-type=e2-medium
```

#### Azure Regions
```bash
# East US
az vm create --resource-group benchmarks --name benchmark-east-us --location eastus --size Standard_B2s

# West US
az vm create --resource-group benchmarks --name benchmark-west-us --location westus --size Standard_B2s

# West Europe
az vm create --resource-group benchmarks --name benchmark-west-europe --location westeurope --size Standard_B2s
```

### 2. Container-Based Deployment

#### Docker Setup
```dockerfile
# Dockerfile for benchmark container
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY scripts/embedding-benchmarks/ .
ENV PYTHONPATH=/app

CMD ["python", "run.py", "benchmark", "--samples-per-category", "100", "--batch-sizes", "1,5,10,25"]
```

#### Kubernetes Multi-Region Deployment
```yaml
# k8s-benchmark-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: embedding-benchmark
spec:
  template:
    spec:
      containers:
      - name: benchmark
        image: your-registry/embedding-benchmark:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        - name: COHERE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: cohere
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google
        - name: REGION
          value: "us-east-1"
        volumeMounts:
        - name: results
          mountPath: /app/data
      volumes:
      - name: results
        persistentVolumeClaim:
          claimName: benchmark-results
      restartPolicy: Never
```

### 3. Modal Labs Multi-Region Deployment

Modal Labs provides an excellent platform for running benchmarks across different regions with automatic scaling and resource management.

#### Setup Modal Deployment
```bash
# Install Modal CLI
pip install modal

# Set up Modal secrets
modal secret create openai-api-key OPENAI_API_KEY=your_key_here
modal secret create cohere-api-key COHERE_API_KEY=your_key_here  
modal secret create google-api-key GOOGLE_API_KEY=your_key_here
modal secret create voyager-api-key VOYAGER_API_KEY=your_key_here
```

#### Deploy and Run Multi-Region Benchmarks
```bash
# Deploy the Modal app
modal deploy modal_deployment.py

# Run benchmarks across multiple regions
modal run modal_deployment.py --regions "us-east,us-west,europe" --samples-per-category 100

# Run with specific providers
modal run modal_deployment.py --providers "openai,cohere" --regions "us-east,us-west"
```

#### Modal Advantages
- **Automatic Scaling**: Resources scale based on workload
- **Regional Deployment**: Built-in support for different regions
- **Cost Optimization**: Pay only for compute time used
- **Parallel Execution**: Run multiple regions simultaneously
- **Result Aggregation**: Built-in volume storage for results
- **Error Handling**: Automatic retries and error recovery

### 4. GitHub Actions Multi-Region Strategy

```yaml
# .github/workflows/multi-region-benchmark.yml
name: Multi-Region Embedding Benchmarks

on:
  workflow_dispatch:
    inputs:
      regions:
        description: 'Comma-separated list of regions'
        required: true
        default: 'us-east-1,us-west-2,eu-west-1'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        region: ${{ fromJson(github.event.inputs.regions) }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync
    
    - name: Run benchmark
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        COHERE_API_KEY: ${{ secrets.COHERE_API_KEY }}
        GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
        AWS_REGION: ${{ matrix.region }}
      run: |
        cd scripts/embedding-benchmarks
        uv run python run.py benchmark --samples-per-category 100 --output-dir ./data/${{ matrix.region }}
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: benchmark-results-${{ matrix.region }}
        path: scripts/embedding-benchmarks/data/${{ matrix.region }}/
```

## Regional Performance Analysis

### Expected Latency Patterns

1. **Provider API Endpoints**:
   - OpenAI: Primarily US-based endpoints
   - Cohere: Multi-region deployment
   - Google: Global edge network
   - Voyager: US-focused

2. **Network Latency Impact**:
   - Same region: +5-15ms
   - Cross-region (same continent): +20-50ms  
   - Cross-continent: +100-200ms

3. **Time Zone Considerations**:
   - Peak hours impact on API response times
   - Rate limiting variations by region

### Benchmark Execution Strategy

```bash
# Sequential execution across regions
regions=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1")

for region in "${regions[@]}"; do
    echo "Running benchmark in $region"
    export AWS_REGION=$region
    uv run python run.py benchmark \
        --samples-per-category 100 \
        --batch-sizes 1,5,10,25 \
        --output-dir ./data/$region \
        --providers openai,cohere,gemini
    
    # Add region metadata to results
    echo "{\"region\": \"$region\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > ./data/$region/metadata.json
done
```

### Results Aggregation

```python
# aggregate_regional_results.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def aggregate_regional_results(base_dir: str):
    """Aggregate benchmark results across regions."""
    results = []
    
    for region_dir in Path(base_dir).glob("*/"):
        if region_dir.is_dir():
            csv_path = region_dir / "embedding_latency_statistics.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df['Region'] = region_dir.name
                results.append(df)
    
    if results:
        combined_df = pd.concat(results, ignore_index=True)
        
        # Create regional comparison plots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # P50 latency by region
        pivot_p50 = combined_df.pivot(index='Provider/Model', columns='Region', values='P50_ms')
        pivot_p50.plot(kind='bar', ax=axes[0,0], title='P50 Latency by Region')
        
        # P95 latency by region  
        pivot_p95 = combined_df.pivot(index='Provider/Model', columns='Region', values='P95_ms')
        pivot_p95.plot(kind='bar', ax=axes[0,1], title='P95 Latency by Region')
        
        # Throughput by region
        pivot_throughput = combined_df.pivot(index='Provider/Model', columns='Region', values='Throughput')
        pivot_throughput.plot(kind='bar', ax=axes[1,0], title='Throughput by Region')
        
        # Regional latency heatmap
        heatmap_data = combined_df.pivot_table(index='Provider/Model', columns='Region', values='P50_ms')
        sns.heatmap(heatmap_data, ax=axes[1,1], annot=True, fmt='.1f', cmap='YlOrRd')
        axes[1,1].set_title('P50 Latency Heatmap (ms)')
        
        plt.tight_layout()
        plt.savefig(Path(base_dir) / 'regional_comparison.png', dpi=300, bbox_inches='tight')
        
        return combined_df
    
    return None
```

## Implementation Checklist

- [ ] Set up cloud provider accounts and regions
- [ ] Configure API keys in each region's environment
- [ ] Deploy benchmark containers/instances
- [ ] Execute benchmarks with consistent parameters
- [ ] Collect and aggregate results
- [ ] Generate regional comparison reports
- [ ] Document findings and recommendations

## Cost Optimization

1. **Spot Instances**: Use spot instances for cost-effective benchmarking
2. **Scheduled Execution**: Run during off-peak hours
3. **Resource Cleanup**: Automatically terminate instances after completion
4. **Batch Processing**: Group multiple benchmark runs together

## Security Considerations

1. **API Key Management**: Use cloud provider secret management
2. **Network Security**: Restrict access to benchmark instances
3. **Data Encryption**: Encrypt results in transit and at rest
4. **Access Logging**: Monitor benchmark execution and access
