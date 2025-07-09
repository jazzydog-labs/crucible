"""Idea entity for the domain model.

Ideas are generated from prompts and can be scored, refined, and tagged.
They maintain a relationship to their source prompt and can have multiple
refined versions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional

from .value_objects import Tag, Score, ValidationResult


@dataclass
class Idea:
    """Represents an idea generated from a prompt.
    
    Ideas are the output of rendering prompts with specific context.
    They can be scored, tagged, refined, and have metadata attached.
    """
    
    id: str
    prompt_id: str
    content: str
    score: Score = field(default_factory=Score.default)
    tags: List[Tag] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    refined_versions: List[Idea] = field(default_factory=list)
    parent_idea_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize and validate the idea."""
        self.validate()
    
    @classmethod
    def create(
        cls,
        prompt_id: str,
        content: str,
        score: Optional[float] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_idea_id: Optional[str] = None
    ) -> Idea:
        """Factory method to create a new idea."""
        idea_id = str(uuid.uuid4())
        score_obj = Score(score) if score is not None else Score.default()
        tag_objects = [Tag(t) for t in (tags or [])]
        
        return cls(
            id=idea_id,
            prompt_id=prompt_id,
            content=content,
            score=score_obj,
            tags=tag_objects,
            metadata=metadata or {},
            parent_idea_id=parent_idea_id
        )
    
    def validate(self) -> ValidationResult:
        """Validate the idea."""
        result = ValidationResult(is_valid=True)
        
        if not self.content:
            result.add_error("Content cannot be empty")
        
        if not self.prompt_id:
            result.add_error("Prompt ID cannot be empty")
        
        if len(self.content) > 50000:
            result.add_error("Content cannot be longer than 50000 characters")
        
        # Check for circular references in refinements
        if self._has_circular_refinement():
            result.add_error("Circular reference detected in refined versions")
        
        # Check for duplicate tags
        tag_values = [tag.value for tag in self.tags]
        if len(tag_values) != len(set(tag_values)):
            result.add_warning("Duplicate tags found")
        
        return result
    
    def _has_circular_refinement(self) -> bool:
        """Check if there are circular references in refinements."""
        visited = set()
        
        def check_refinement(idea: Idea) -> bool:
            if idea.id in visited:
                return True
            visited.add(idea.id)
            
            for refined in idea.refined_versions:
                if check_refinement(refined):
                    return True
            
            return False
        
        return check_refinement(self)
    
    def refine(self, refined_content: str, **kwargs) -> Idea:
        """Create a refined version of this idea.
        
        Args:
            refined_content: The refined content
            **kwargs: Additional parameters for the refined idea
            
        Returns:
            The newly created refined idea
        """
        refined_idea = Idea.create(
            prompt_id=self.prompt_id,
            content=refined_content,
            score=kwargs.get('score'),
            tags=kwargs.get('tags', [t.value for t in self.tags]),
            metadata=kwargs.get('metadata', self.metadata.copy()),
            parent_idea_id=self.id
        )
        
        self.refined_versions.append(refined_idea)
        return refined_idea
    
    def update_score(self, new_score: float) -> None:
        """Update the idea's score."""
        self.score = Score(new_score)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the idea."""
        tag_obj = Tag(tag)
        if tag_obj not in self.tags:
            self.tags.append(tag_obj)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the idea."""
        tag_obj = Tag(tag)
        if tag_obj in self.tags:
            self.tags.remove(tag_obj)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add or update metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def get_all_versions(self) -> List[Idea]:
        """Get all versions including refinements recursively."""
        versions = [self]
        for refined in self.refined_versions:
            versions.extend(refined.get_all_versions())
        return versions
    
    def get_best_version(self) -> Idea:
        """Get the version with the highest score."""
        all_versions = self.get_all_versions()
        return max(all_versions, key=lambda i: i.score.value)
    
    def get_lineage(self) -> List[str]:
        """Get the lineage of idea IDs from original to this idea."""
        lineage = []
        current = self
        
        while current.parent_idea_id:
            lineage.insert(0, current.parent_idea_id)
            # Note: In a real implementation, we'd need to fetch parent from repository
            # For now, we just return the IDs
            break
        
        lineage.append(self.id)
        return lineage
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert idea to dictionary for serialization."""
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "content": self.content,
            "score": self.score.value,
            "tags": [tag.value for tag in self.tags],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "refined_versions": [idea.to_dict() for idea in self.refined_versions],
            "parent_idea_id": self.parent_idea_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Idea:
        """Create idea from dictionary."""
        tags = [Tag(t) for t in data.get("tags", [])]
        score = Score(data.get("score", 5.0))
        
        # Create the idea without refined versions first
        idea = cls(
            id=data["id"],
            prompt_id=data["prompt_id"],
            content=data["content"],
            score=score,
            tags=tags,
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            refined_versions=[],
            parent_idea_id=data.get("parent_idea_id")
        )
        
        # Then add refined versions
        for refined_data in data.get("refined_versions", []):
            refined_idea = cls.from_dict(refined_data)
            idea.refined_versions.append(refined_idea)
        
        return idea
    
    def __str__(self) -> str:
        """String representation of the idea."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Idea('{content_preview}', score={self.score})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Idea):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)