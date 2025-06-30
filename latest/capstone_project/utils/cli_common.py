"""
Shared CLI components and options for vector database loaders
"""

import sys
import typer
from typing import Callable
from logging_utils import LoaderConsole


# Common CLI options as reusable functions
def cloud_option():
    """Cloud vs local storage option"""
    return typer.Option(
        False, 
        "--cloud",
        help="Use cloud storage instead of local persistent storage"
    )


def table_name_option(default: str = "wildchat_10k"):
    """Table/collection name option"""
    return typer.Option(
        default,
        "--table-name", "--collection-name",
        help="Name of the table/collection"
    )


def limit_option(default: int = 10000):
    """Record limit option"""
    return typer.Option(
        default,
        "--limit",
        help="Maximum number of records to load"
    )


def batch_size_option(default: int = 100):
    """Batch size option"""
    return typer.Option(
        default,
        "--batch-size",
        help="Batch size for writing to database"
    )


def language_option(default: str = "English"):
    """Language filter option"""
    return typer.Option(
        default,
        "--language",
        help="Filter conversations by language"
    )


def min_length_option(default: int = 30):
    """Minimum message length option"""
    return typer.Option(
        default,
        "--min-length",
        help="Minimum message length to include"
    )


def reset_option():
    """Reset table/collection option"""
    return typer.Option(
        False,
        "--reset",
        help="Reset table/collection before loading (delete existing data)"
    )


def handle_cli_errors(func: Callable) -> Callable:
    """
    Decorator to handle common CLI errors
    
    Args:
        func: The main function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        console = LoaderConsole()
        
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console.print_warning("\nOperation cancelled by user")
            sys.exit(1)
        except Exception as e:
            console.print_error(f"\nError: {e}")
            sys.exit(1)
    
    return wrapper


class CommonCLIArgs:
    """Container for common CLI arguments"""
    
    def __init__(
        self,
        cloud: bool = False,
        table_name: str = "wildchat_10k",
        limit: int = 10000,
        batch_size: int = 100,
        language: str = "English",
        min_length: int = 30,
        reset: bool = False
    ):
        self.cloud = cloud
        self.table_name = table_name
        self.limit = limit
        self.batch_size = batch_size
        self.language = language
        self.min_length = min_length
        self.reset = reset
    
    def to_dict(self) -> dict:
        """Convert to dictionary for easy unpacking"""
        return {
            "use_cloud": self.cloud,
            "table_name": self.table_name,
            "limit": self.limit,
            "batch_size": self.batch_size,
            "filter_language": self.language,
            "min_message_length": self.min_length,
            "reset": self.reset
        }