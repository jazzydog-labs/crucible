"""Repository interfaces and implementations for domain entities.

This package provides the repository pattern for data access,
separating domain logic from persistence concerns.
"""

from .interfaces import PromptRepository, IdeaRepository
from .json_repositories import JSONPromptRepository, JSONIdeaRepository

__all__ = [
    "PromptRepository",
    "IdeaRepository", 
    "JSONPromptRepository",
    "JSONIdeaRepository"
]