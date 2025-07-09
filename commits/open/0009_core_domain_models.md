# Define Core Domain Models

## Status: OPEN

## Description
Define and implement the core domain models (Prompt and Idea entities) with basic persistence capabilities.

## Requirements
- Create Prompt entity with proper attributes and behaviors
- Create Idea entity with relationships to prompts
- Implement persistence layer (YAML/JSON files initially)
- Add validation and business rules
- Implement rendering logic for prompts with context variables
- Create repository pattern for data access

## Domain Model Design
```python
# Prompt entity
- id: str
- title: str
- content: str
- category: str
- tags: List[str]
- variables: Dict[str, Any]
- created_at: datetime
- updated_at: datetime

# Idea entity
- id: str
- prompt_id: str
- content: str
- score: float
- tags: List[str]
- metadata: Dict[str, Any]
- created_at: datetime
- refined_versions: List[Idea]
```

## Implementation Tasks
1. Create entity classes with proper encapsulation
2. Implement value objects for complex attributes
3. Add repository interfaces and implementations
4. Create factories for entity creation
5. Implement template rendering for prompts
6. Add import/export capabilities

## Files to Create
- `src/crucible/domain/prompt.py`
- `src/crucible/domain/idea.py`
- `src/crucible/repository/prompt_repository.py`
- `src/crucible/repository/idea_repository.py`
- `src/crucible/domain/value_objects.py`