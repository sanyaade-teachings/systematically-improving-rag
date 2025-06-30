"""Configuration management for synthetic query generation."""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for synthetic query generation."""
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = None
    cache_dir: Path = None
    recall_cache_dir: Path = None
    db_path: Path = None
    
    # Processing settings
    batch_size: int = 100
    max_concurrent: int = 10
    update_interval: int = 50
    
    # Model settings
    model_name: str = "openai/gpt-4o-mini"
    
    # ChromaDB settings
    use_cloud_chromadb: bool = True
    
    def __post_init__(self):
        """Initialize paths after dataclass creation."""
        if self.data_dir is None:
            self.data_dir = self.base_dir / "data"
        
        if self.cache_dir is None:
            self.cache_dir = self.data_dir / "cache"
        
        if self.recall_cache_dir is None:
            self.recall_cache_dir = self.data_dir / "cache_recall"
        
        if self.db_path is None:
            self.db_path = self.data_dir / "databases" / "synthetic_queries.db"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            batch_size=int(os.getenv("SQ_BATCH_SIZE", "100")),
            max_concurrent=int(os.getenv("SQ_MAX_CONCURRENT", "10")),
            update_interval=int(os.getenv("SQ_UPDATE_INTERVAL", "50")),
            model_name=os.getenv("SQ_MODEL_NAME", "openai/gpt-4o-mini"),
            use_cloud_chromadb=os.getenv("SQ_USE_CLOUD_CHROMADB", "true").lower() == "true"
        )
    
    def override_from_args(self, args):
        """Override config values from command line arguments.
        
        Args:
            args: Parsed command line arguments
        """
        if hasattr(args, 'batch_size') and args.batch_size:
            self.batch_size = args.batch_size
        
        if hasattr(args, 'max_concurrent') and args.max_concurrent:
            self.max_concurrent = args.max_concurrent
        
        if hasattr(args, 'update_interval') and args.update_interval:
            self.update_interval = args.update_interval
        
        if hasattr(args, 'model') and args.model:
            self.model_name = args.model
        
        if hasattr(args, 'use_local') and args.use_local:
            self.use_cloud_chromadb = False
        
        if hasattr(args, 'data_dir') and args.data_dir:
            self.data_dir = Path(args.data_dir)
            # Update dependent paths
            self.cache_dir = self.data_dir / "cache"
            self.recall_cache_dir = self.data_dir / "cache_recall"
            self.db_path = self.data_dir / "databases" / "synthetic_queries.db"
    
    def ensure_dirs(self):
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.recall_cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)