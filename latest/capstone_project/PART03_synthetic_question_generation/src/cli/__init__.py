"""CLI commands for synthetic query generation."""

from .generate import generate_command
from .verify import verify_command

__all__ = ["generate_command", "verify_command"]