"""Prompt entity for the domain model.

Prompts are the core entities that contain templates for generating ideas.
They can have variables that are filled in when rendering.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import re
import string

from .value_objects import Tag, Category, TemplateVariable, ValidationResult


@dataclass
class Prompt:
    """Represents a prompt template for idea generation.
    
    A prompt is a template that can be rendered with specific context
    variables to generate ideas. It belongs to a category and can be
    tagged for easier organization.
    """
    
    id: str
    title: str
    content: str
    category: Category
    tags: List[Tag] = field(default_factory=list)
    variables: Dict[str, TemplateVariable] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize and validate the prompt."""
        self.validate()
        self._extract_variables()
    
    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        category: Category,
        tags: Optional[List[str]] = None,
        variables: Optional[Dict[str, TemplateVariable]] = None
    ) -> Prompt:
        """Factory method to create a new prompt."""
        prompt_id = str(uuid.uuid4())
        tag_objects = [Tag(t) for t in (tags or [])]
        
        return cls(
            id=prompt_id,
            title=title,
            content=content,
            category=category,
            tags=tag_objects,
            variables=variables or {}
        )
    
    def validate(self) -> ValidationResult:
        """Validate the prompt."""
        result = ValidationResult(is_valid=True)
        
        if not self.title:
            result.add_error("Title cannot be empty")
        
        if not self.content:
            result.add_error("Content cannot be empty")
        
        if len(self.title) > 200:
            result.add_error("Title cannot be longer than 200 characters")
        
        if len(self.content) > 10000:
            result.add_error("Content cannot be longer than 10000 characters")
        
        # Check for duplicate tags
        tag_values = [tag.value for tag in self.tags]
        if len(tag_values) != len(set(tag_values)):
            result.add_warning("Duplicate tags found")
        
        return result
    
    def _extract_variables(self) -> None:
        """Extract variables from the content template."""
        # Find all {variable_name} patterns in content
        formatter = string.Formatter()
        
        for _, field_name, _, _ in formatter.parse(self.content):
            if field_name and field_name not in self.variables:
                # Create a default variable if not explicitly defined
                self.variables[field_name] = TemplateVariable(
                    name=field_name,
                    description=f"Variable '{field_name}' used in template",
                    required=True
                )
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render the prompt with given context variables.
        
        Args:
            context: Dictionary of variable values
            
        Returns:
            Rendered prompt content
            
        Raises:
            KeyError: If required variables are missing
            ValueError: If template rendering fails
        """
        # Check required variables
        missing_vars = []
        for var_name, var in self.variables.items():
            if var.required and var_name not in context:
                if var.default_value is not None:
                    context[var_name] = var.default_value
                else:
                    missing_vars.append(var_name)
        
        if missing_vars:
            raise KeyError(f"Missing required variables: {', '.join(missing_vars)}")
        
        try:
            return self.content.format(**context)
        except Exception as e:
            raise ValueError(f"Failed to render template: {e}")
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the prompt."""
        tag_obj = Tag(tag)
        if tag_obj not in self.tags:
            self.tags.append(tag_obj)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the prompt."""
        tag_obj = Tag(tag)
        if tag_obj in self.tags:
            self.tags.remove(tag_obj)
            self.updated_at = datetime.now()
    
    def update_content(self, content: str) -> None:
        """Update the prompt content."""
        self.content = content
        self.updated_at = datetime.now()
        self._extract_variables()
        self.validate()
    
    def get_required_variables(self) -> List[str]:
        """Get list of required variable names."""
        return [
            name for name, var in self.variables.items()
            if var.required and var.default_value is None
        ]
    
    def get_all_variables(self) -> List[str]:
        """Get list of all variable names."""
        return list(self.variables.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert prompt to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": {
                "name": self.category.name,
                "description": self.category.description
            },
            "tags": [tag.value for tag in self.tags],
            "variables": {
                name: {
                    "name": var.name,
                    "description": var.description,
                    "default_value": var.default_value,
                    "required": var.required
                }
                for name, var in self.variables.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Prompt:
        """Create prompt from dictionary."""
        category = Category(
            name=data["category"]["name"],
            description=data["category"].get("description", "")
        )
        
        tags = [Tag(t) for t in data.get("tags", [])]
        
        variables = {}
        for name, var_data in data.get("variables", {}).items():
            variables[name] = TemplateVariable(
                name=var_data["name"],
                description=var_data.get("description", ""),
                default_value=var_data.get("default_value"),
                required=var_data.get("required", True)
            )
        
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            category=category,
            tags=tags,
            variables=variables,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def __str__(self) -> str:
        """String representation of the prompt."""
        return f"Prompt('{self.title}', category='{self.category}')"
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on ID."""
        if not isinstance(other, Prompt):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)