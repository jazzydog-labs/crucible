"""Repository interfaces for domain entities.

These interfaces define the contract for data access, allowing
different implementations (file, database, etc.) to be used interchangeably.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from crucible.domain import Prompt, Idea


class PromptRepository(ABC):
    """Interface for prompt persistence."""
    
    @abstractmethod
    def save(self, prompt: Prompt) -> None:
        """Save a prompt to the repository.
        
        Args:
            prompt: The prompt to save
        """
        pass
    
    @abstractmethod
    def get_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by its ID.
        
        Args:
            prompt_id: The ID of the prompt
            
        Returns:
            The prompt if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Prompt]:
        """Get all prompts.
        
        Returns:
            List of all prompts
        """
        pass
    
    @abstractmethod
    def get_by_category(self, category_name: str) -> List[Prompt]:
        """Get prompts by category.
        
        Args:
            category_name: The name of the category
            
        Returns:
            List of prompts in the category
        """
        pass
    
    @abstractmethod
    def get_by_tag(self, tag: str) -> List[Prompt]:
        """Get prompts by tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List of prompts with the tag
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Prompt]:
        """Search prompts by title or content.
        
        Args:
            query: The search query
            
        Returns:
            List of matching prompts
        """
        pass
    
    @abstractmethod
    def delete(self, prompt_id: str) -> bool:
        """Delete a prompt.
        
        Args:
            prompt_id: The ID of the prompt to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, prompt_id: str) -> bool:
        """Check if a prompt exists.
        
        Args:
            prompt_id: The ID of the prompt
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get the total number of prompts.
        
        Returns:
            Number of prompts
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Remove all prompts from the repository."""
        pass


class IdeaRepository(ABC):
    """Interface for idea persistence."""
    
    @abstractmethod
    def save(self, idea: Idea) -> None:
        """Save an idea to the repository.
        
        Args:
            idea: The idea to save
        """
        pass
    
    @abstractmethod
    def get_by_id(self, idea_id: str) -> Optional[Idea]:
        """Get an idea by its ID.
        
        Args:
            idea_id: The ID of the idea
            
        Returns:
            The idea if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Idea]:
        """Get all ideas.
        
        Returns:
            List of all ideas
        """
        pass
    
    @abstractmethod
    def get_by_prompt_id(self, prompt_id: str) -> List[Idea]:
        """Get ideas generated from a specific prompt.
        
        Args:
            prompt_id: The ID of the prompt
            
        Returns:
            List of ideas from the prompt
        """
        pass
    
    @abstractmethod
    def get_by_tag(self, tag: str) -> List[Idea]:
        """Get ideas by tag.
        
        Args:
            tag: The tag to search for
            
        Returns:
            List of ideas with the tag
        """
        pass
    
    @abstractmethod
    def get_by_score_range(self, min_score: float, max_score: float) -> List[Idea]:
        """Get ideas within a score range.
        
        Args:
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)
            
        Returns:
            List of ideas within the score range
        """
        pass
    
    @abstractmethod
    def get_top_ideas(self, limit: int = 10) -> List[Idea]:
        """Get top-scored ideas.
        
        Args:
            limit: Maximum number of ideas to return
            
        Returns:
            List of top-scored ideas
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Idea]:
        """Search ideas by content.
        
        Args:
            query: The search query
            
        Returns:
            List of matching ideas
        """
        pass
    
    @abstractmethod
    def delete(self, idea_id: str) -> bool:
        """Delete an idea.
        
        Args:
            idea_id: The ID of the idea to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, idea_id: str) -> bool:
        """Check if an idea exists.
        
        Args:
            idea_id: The ID of the idea
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get the total number of ideas.
        
        Returns:
            Number of ideas
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Remove all ideas from the repository."""
        pass