"""Value objects for the domain model.

Value objects are immutable objects that represent domain concepts
but have no identity of their own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any, Optional
import re


@dataclass(frozen=True)
class Tag:
    """Represents a tag for categorizing prompts and ideas."""
    
    value: str
    
    def __post_init__(self):
        """Validate tag format."""
        if not self.value:
            raise ValueError("Tag cannot be empty")
        
        # Normalize tag: lowercase, alphanumeric with dashes
        normalized = re.sub(r'[^a-z0-9-]', '-', self.value.lower())
        normalized = re.sub(r'-+', '-', normalized).strip('-')
        
        if normalized != self.value:
            object.__setattr__(self, 'value', normalized)
        
        if len(self.value) > 50:
            raise ValueError("Tag cannot be longer than 50 characters")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Score:
    """Represents a score for rating ideas."""
    
    value: float
    
    def __post_init__(self):
        """Validate score range."""
        if not 0.0 <= self.value <= 10.0:
            raise ValueError("Score must be between 0.0 and 10.0")
    
    def __str__(self) -> str:
        return f"{self.value:.1f}"
    
    def __lt__(self, other: Score) -> bool:
        return self.value < other.value
    
    def __le__(self, other: Score) -> bool:
        return self.value <= other.value
    
    @classmethod
    def default(cls) -> Score:
        """Create a default neutral score."""
        return cls(5.0)
    
    @classmethod
    def from_percentage(cls, percentage: float) -> Score:
        """Create a score from a percentage (0-100)."""
        return cls(percentage / 10.0)
    
    def to_percentage(self) -> float:
        """Convert score to percentage."""
        return self.value * 10.0


@dataclass(frozen=True)
class Category:
    """Represents a category for organizing prompts."""
    
    name: str
    description: str = ""
    
    def __post_init__(self):
        """Validate category."""
        if not self.name:
            raise ValueError("Category name cannot be empty")
        
        # Normalize name: title case, alphanumeric with spaces
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', self.name)
        normalized = ' '.join(normalized.split()).title()
        
        if normalized != self.name:
            object.__setattr__(self, 'name', normalized)
        
        if len(self.name) > 100:
            raise ValueError("Category name cannot be longer than 100 characters")
    
    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class TemplateVariable:
    """Represents a variable in a prompt template."""
    
    name: str
    description: str = ""
    default_value: Optional[Any] = None
    required: bool = True
    
    def __post_init__(self):
        """Validate variable."""
        if not self.name:
            raise ValueError("Variable name cannot be empty")
        
        # Variable names should be valid Python identifiers
        if not self.name.isidentifier():
            raise ValueError(f"Variable name '{self.name}' is not a valid identifier")
    
    def __str__(self) -> str:
        return f"{{{self.name}}}"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
    
    def merge(self, other: ValidationResult) -> ValidationResult:
        """Merge with another validation result."""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings
        )
    
    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid