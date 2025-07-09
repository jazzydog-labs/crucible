"""JSON file-based repository implementations.

These implementations use JSON files for persistence, suitable for
small to medium-sized datasets and development/testing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import threading

from crucible.domain import Prompt, Idea, Category, Tag
from .interfaces import PromptRepository, IdeaRepository


class JSONPromptRepository(PromptRepository):
    """JSON file-based prompt repository."""
    
    def __init__(self, file_path: str | Path = "prompts.json"):
        """Initialize the repository with a file path."""
        self.file_path = Path(file_path)
        self._lock = threading.RLock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the JSON file exists."""
        if not self.file_path.exists():
            self.file_path.write_text("[]")
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        """Load prompts from the JSON file."""
        with self._lock:
            try:
                content = self.file_path.read_text()
                return json.loads(content) if content else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
    
    def _save_prompts(self, prompts: List[Dict[str, Any]]) -> None:
        """Save prompts to the JSON file."""
        with self._lock:
            self.file_path.write_text(json.dumps(prompts, indent=2))
    
    def save(self, prompt: Prompt) -> None:
        """Save a prompt to the repository."""
        prompts_data = self._load_prompts()
        prompt_dict = prompt.to_dict()
        
        # Update if exists, otherwise append
        updated = False
        for i, p in enumerate(prompts_data):
            if p["id"] == prompt.id:
                prompts_data[i] = prompt_dict
                updated = True
                break
        
        if not updated:
            prompts_data.append(prompt_dict)
        
        self._save_prompts(prompts_data)
    
    def get_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by its ID."""
        prompts_data = self._load_prompts()
        
        for prompt_data in prompts_data:
            if prompt_data["id"] == prompt_id:
                return Prompt.from_dict(prompt_data)
        
        return None
    
    def get_all(self) -> List[Prompt]:
        """Get all prompts."""
        prompts_data = self._load_prompts()
        return [Prompt.from_dict(p) for p in prompts_data]
    
    def get_by_category(self, category_name: str) -> List[Prompt]:
        """Get prompts by category."""
        prompts = self.get_all()
        return [p for p in prompts if p.category.name.lower() == category_name.lower()]
    
    def get_by_tag(self, tag: str) -> List[Prompt]:
        """Get prompts by tag."""
        prompts = self.get_all()
        tag_lower = tag.lower()
        return [
            p for p in prompts 
            if any(t.value.lower() == tag_lower for t in p.tags)
        ]
    
    def search(self, query: str) -> List[Prompt]:
        """Search prompts by title or content."""
        prompts = self.get_all()
        query_lower = query.lower()
        
        results = []
        for prompt in prompts:
            if (query_lower in prompt.title.lower() or 
                query_lower in prompt.content.lower()):
                results.append(prompt)
        
        return results
    
    def delete(self, prompt_id: str) -> bool:
        """Delete a prompt."""
        prompts_data = self._load_prompts()
        original_count = len(prompts_data)
        
        prompts_data = [p for p in prompts_data if p["id"] != prompt_id]
        
        if len(prompts_data) < original_count:
            self._save_prompts(prompts_data)
            return True
        
        return False
    
    def exists(self, prompt_id: str) -> bool:
        """Check if a prompt exists."""
        return self.get_by_id(prompt_id) is not None
    
    def count(self) -> int:
        """Get the total number of prompts."""
        return len(self._load_prompts())
    
    def clear(self) -> None:
        """Remove all prompts from the repository."""
        self._save_prompts([])


class JSONIdeaRepository(IdeaRepository):
    """JSON file-based idea repository."""
    
    def __init__(self, file_path: str | Path = "ideas.json"):
        """Initialize the repository with a file path."""
        self.file_path = Path(file_path)
        self._lock = threading.RLock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the JSON file exists."""
        if not self.file_path.exists():
            self.file_path.write_text("[]")
    
    def _load_ideas(self) -> List[Dict[str, Any]]:
        """Load ideas from the JSON file."""
        with self._lock:
            try:
                content = self.file_path.read_text()
                return json.loads(content) if content else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
    
    def _save_ideas(self, ideas: List[Dict[str, Any]]) -> None:
        """Save ideas to the JSON file."""
        with self._lock:
            self.file_path.write_text(json.dumps(ideas, indent=2))
    
    def save(self, idea: Idea) -> None:
        """Save an idea to the repository."""
        ideas_data = self._load_ideas()
        idea_dict = idea.to_dict()
        
        # Update if exists, otherwise append
        updated = False
        for i, existing in enumerate(ideas_data):
            if existing["id"] == idea.id:
                ideas_data[i] = idea_dict
                updated = True
                break
        
        if not updated:
            ideas_data.append(idea_dict)
        
        self._save_ideas(ideas_data)
    
    def get_by_id(self, idea_id: str) -> Optional[Idea]:
        """Get an idea by its ID."""
        ideas_data = self._load_ideas()
        
        for idea_data in ideas_data:
            if idea_data["id"] == idea_id:
                return Idea.from_dict(idea_data)
        
        return None
    
    def get_all(self) -> List[Idea]:
        """Get all ideas."""
        ideas_data = self._load_ideas()
        return [Idea.from_dict(i) for i in ideas_data]
    
    def get_by_prompt_id(self, prompt_id: str) -> List[Idea]:
        """Get ideas generated from a specific prompt."""
        ideas = self.get_all()
        return [i for i in ideas if i.prompt_id == prompt_id]
    
    def get_by_tag(self, tag: str) -> List[Idea]:
        """Get ideas by tag."""
        ideas = self.get_all()
        tag_lower = tag.lower()
        return [
            i for i in ideas 
            if any(t.value.lower() == tag_lower for t in i.tags)
        ]
    
    def get_by_score_range(self, min_score: float, max_score: float) -> List[Idea]:
        """Get ideas within a score range."""
        ideas = self.get_all()
        return [
            i for i in ideas 
            if min_score <= i.score.value <= max_score
        ]
    
    def get_top_ideas(self, limit: int = 10) -> List[Idea]:
        """Get top-scored ideas."""
        ideas = self.get_all()
        sorted_ideas = sorted(ideas, key=lambda i: i.score.value, reverse=True)
        return sorted_ideas[:limit]
    
    def search(self, query: str) -> List[Idea]:
        """Search ideas by content."""
        ideas = self.get_all()
        query_lower = query.lower()
        
        return [
            i for i in ideas 
            if query_lower in i.content.lower()
        ]
    
    def delete(self, idea_id: str) -> bool:
        """Delete an idea."""
        ideas_data = self._load_ideas()
        original_count = len(ideas_data)
        
        ideas_data = [i for i in ideas_data if i["id"] != idea_id]
        
        if len(ideas_data) < original_count:
            self._save_ideas(ideas_data)
            return True
        
        return False
    
    def exists(self, idea_id: str) -> bool:
        """Check if an idea exists."""
        return self.get_by_id(idea_id) is not None
    
    def count(self) -> int:
        """Get the total number of ideas."""
        return len(self._load_ideas())
    
    def clear(self) -> None:
        """Remove all ideas from the repository."""
        self._save_ideas([])