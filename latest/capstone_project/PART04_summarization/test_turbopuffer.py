#!/usr/bin/env python3
"""Debug TurboPuffer namespace to see what data is stored"""

import os
import turbopuffer
from dotenv import load_dotenv
from rich.console import Console

console = Console()

# Load environment variables
load_dotenv()

api_key = os.getenv("TURBOPUFFER_API_KEY")
client = turbopuffer.Turbopuffer(api_key=api_key, region="gcp-us-central1")

# Get namespace
ns = client.namespace("wildchat-summaries-v2")

# Query to see some documents
try:
    # Get a few documents
    results = ns.query(
        top_k=5,
        include_attributes=["id", "hash", "summary_version", "text"]
    )
    
    console.print(f"Found {len(results.rows)} documents")
    
    for i, row in enumerate(results.rows):
        console.print(f"\n[cyan]Document {i+1}:[/cyan]")
        console.print(f"ID: {row.id}")
        console.print(f"Hash: {getattr(row, 'hash', 'N/A')}")
        console.print(f"Version: {getattr(row, 'summary_version', 'N/A')}")
        console.print(f"Text preview: {row.text[:100]}...")
        
except Exception as e:
    console.print(f"[red]Error: {e}[/red]")