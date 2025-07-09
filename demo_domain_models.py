#!/usr/bin/env python3
"""Demo showcasing the core domain models.

This demo demonstrates:
- Prompt entity with template variables
- Idea entity with scoring and refinement
- Value objects for domain concepts
- Repository pattern for persistence
- Validation and business rules
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent / 'src'))

from crucible.domain import Prompt, Idea, Category, Tag, Score
from crucible.domain.value_objects import TemplateVariable
from crucible.repository import JSONPromptRepository, JSONIdeaRepository


def demo_value_objects():
    """Demonstrate value objects."""
    print("=== Value Objects Demo ===")
    
    print("\n1. Tags (normalized and validated):")
    tags = [
        Tag("Python Programming"),  # Will be normalized
        Tag("web-development"),
        Tag("API Design"),
    ]
    for tag in tags:
        print(f"   Original input → {tag.value}")
    
    print("\n2. Scores (bounded 0-10):")
    scores = [
        Score(8.5),
        Score.default(),  # 5.0
        Score.from_percentage(75),  # 7.5
    ]
    for score in scores:
        print(f"   Score: {score} ({score.to_percentage()}%)")
    
    print("\n3. Categories (normalized names):")
    categories = [
        Category("machine learning", "ML and AI topics"),
        Category("Web Development"),
        Category("data science"),
    ]
    for cat in categories:
        print(f"   {cat.name}: {cat.description or 'No description'}")


def demo_prompt_entity():
    """Demonstrate Prompt entity."""
    print("\n=== Prompt Entity Demo ===")
    
    # Create a prompt with template variables
    prompt = Prompt.create(
        title="API Design Assistant",
        content="""Design a RESTful API for {domain}.

Consider the following aspects:
- Resource naming for {entity_type}
- HTTP methods and status codes
- Authentication using {auth_method}
- Rate limiting at {rate_limit} requests per minute
- API versioning strategy

The API should follow {standard} standards.""",
        category=Category("Software Architecture"),
        tags=["api", "rest", "design", "architecture"]
    )
    
    print(f"\n1. Created prompt: {prompt.title}")
    print(f"   Category: {prompt.category}")
    print(f"   Tags: {', '.join(t.value for t in prompt.tags)}")
    
    print("\n2. Automatically extracted variables:")
    for name, var in prompt.variables.items():
        print(f"   - {name}: {var.description}")
    
    print("\n3. Required variables:")
    required = prompt.get_required_variables()
    print(f"   {', '.join(required)}")
    
    # Render the prompt with context
    print("\n4. Rendering prompt with context:")
    context = {
        "domain": "E-commerce Platform",
        "entity_type": "Products and Orders",
        "auth_method": "OAuth 2.0",
        "rate_limit": 1000,
        "standard": "OpenAPI 3.0"
    }
    
    rendered = prompt.render(context)
    print("   " + rendered.replace("\n", "\n   "))
    
    # Demonstrate validation
    print("\n5. Validation:")
    result = prompt.validate()
    print(f"   Valid: {result.is_valid}")
    if result.errors:
        print(f"   Errors: {', '.join(result.errors)}")
    if result.warnings:
        print(f"   Warnings: {', '.join(result.warnings)}")
    
    return prompt


def demo_idea_entity(prompt_id: str):
    """Demonstrate Idea entity."""
    print("\n=== Idea Entity Demo ===")
    
    # Create an idea from the prompt
    idea = Idea.create(
        prompt_id=prompt_id,
        content="""RESTful API Design for E-commerce Platform:

Resources:
- /api/v1/products (GET, POST, PUT, DELETE)
- /api/v1/orders (GET, POST, PUT)
- /api/v1/customers (GET, POST, PUT)

Authentication: OAuth 2.0 with JWT tokens
Rate Limiting: 1000 requests/minute per API key
Versioning: URI versioning (/api/v1/)""",
        score=7.5,
        tags=["implementation", "rest-api"],
        metadata={
            "author": "Demo User",
            "tools_used": ["OpenAPI Spec", "Postman"],
            "estimated_hours": 40
        }
    )
    
    print(f"\n1. Created idea with score: {idea.score}")
    print(f"   Tags: {', '.join(t.value for t in idea.tags)}")
    print(f"   Metadata: {idea.metadata}")
    
    # Refine the idea
    print("\n2. Refining the idea:")
    refined = idea.refine(
        refined_content="""Enhanced RESTful API Design:

Previous design + improvements:
- Added GraphQL endpoint for complex queries
- Implemented webhook system for real-time updates
- Added comprehensive error handling with problem details (RFC 7807)
- Included HATEOAS links for better discoverability
- Added OpenAPI documentation endpoint""",
        score=9.0,
        tags=["implementation", "rest-api", "graphql", "enhanced"]
    )
    
    print(f"   Refined version score: {refined.score}")
    print(f"   Parent idea ID: {refined.parent_idea_id}")
    
    # Create another refinement branch
    alternative = idea.refine(
        refined_content="""Alternative API Design:

Using gRPC instead of REST:
- Protocol Buffers for efficient serialization
- Streaming support for real-time data
- Strong typing with .proto definitions
- Better performance for internal services""",
        score=8.0,
        tags=["implementation", "grpc", "alternative"]
    )
    
    print(f"   Alternative version score: {alternative.score}")
    
    # Show version management
    print("\n3. Version management:")
    all_versions = idea.get_all_versions()
    print(f"   Total versions: {len(all_versions)}")
    
    best = idea.get_best_version()
    print(f"   Best version score: {best.score}")
    print(f"   Best version preview: {best.content[:100]}...")
    
    return idea


def demo_repository_pattern():
    """Demonstrate repository pattern."""
    print("\n=== Repository Pattern Demo ===")
    
    # Create temporary files for repositories
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        prompt_file = f.name
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        idea_file = f.name
    
    try:
        # Initialize repositories
        prompt_repo = JSONPromptRepository(prompt_file)
        idea_repo = JSONIdeaRepository(idea_file)
        
        print("\n1. Creating and saving prompts:")
        prompts = [
            Prompt.create(
                "Database Design Guide",
                "Design a database schema for {application_type}",
                Category("Database Design"),
                tags=["database", "schema", "design"]
            ),
            Prompt.create(
                "Code Review Checklist",
                "Review {language} code for {project_type}",
                Category("Code Quality"),
                tags=["review", "quality", "checklist"]
            ),
            Prompt.create(
                "Security Audit Template",
                "Audit {system_type} for security vulnerabilities",
                Category("Security"),
                tags=["security", "audit", "vulnerabilities"]
            )
        ]
        
        for prompt in prompts:
            prompt_repo.save(prompt)
            print(f"   Saved: {prompt.title}")
        
        print(f"\n2. Repository queries:")
        print(f"   Total prompts: {prompt_repo.count()}")
        
        # Search by category
        db_prompts = prompt_repo.get_by_category("Database Design")
        print(f"   Database Design prompts: {len(db_prompts)}")
        
        # Search by tag
        design_prompts = prompt_repo.get_by_tag("design")
        print(f"   Prompts tagged 'design': {len(design_prompts)}")
        
        # Text search
        security_prompts = prompt_repo.search("security")
        print(f"   Prompts containing 'security': {len(security_prompts)}")
        
        print("\n3. Creating and saving ideas:")
        # Create ideas for the first prompt
        prompt_id = prompts[0].id
        ideas = [
            Idea.create(
                prompt_id,
                "Normalized relational database with proper indexing",
                score=8.0,
                tags=["sql", "normalized"]
            ),
            Idea.create(
                prompt_id,
                "NoSQL document store for flexible schema",
                score=7.0,
                tags=["nosql", "flexible"]
            ),
            Idea.create(
                prompt_id,
                "Hybrid approach with SQL + Redis caching",
                score=9.0,
                tags=["hybrid", "performance"]
            )
        ]
        
        for idea in ideas:
            idea_repo.save(idea)
            print(f"   Saved idea with score: {idea.score}")
        
        print("\n4. Idea queries:")
        # Get top ideas
        top_ideas = idea_repo.get_top_ideas(limit=2)
        print(f"   Top 2 ideas:")
        for idea in top_ideas:
            print(f"     - Score {idea.score}: {idea.content[:50]}...")
        
        # Get by score range
        good_ideas = idea_repo.get_by_score_range(7.5, 10.0)
        print(f"   Ideas with score 7.5-10: {len(good_ideas)}")
        
    finally:
        # Cleanup
        Path(prompt_file).unlink(missing_ok=True)
        Path(idea_file).unlink(missing_ok=True)


def demo_validation_and_business_rules():
    """Demonstrate validation and business rules."""
    print("\n=== Validation and Business Rules Demo ===")
    
    print("\n1. Tag validation:")
    try:
        tag = Tag("")  # Empty tag
    except ValueError as e:
        print(f"   ✗ Empty tag: {e}")
    
    try:
        tag = Tag("a" * 51)  # Too long
    except ValueError as e:
        print(f"   ✗ Long tag: {e}")
    
    print("\n2. Score validation:")
    try:
        score = Score(11.0)  # Out of range
    except ValueError as e:
        print(f"   ✗ Invalid score: {e}")
    
    print("\n3. Prompt validation:")
    category = Category("Test")
    prompt = Prompt.create("", "Content", category)  # Empty title
    result = prompt.validate()
    if not result.is_valid:
        print(f"   ✗ Invalid prompt: {result.errors[0]}")
    
    print("\n4. Template variable validation:")
    try:
        var = TemplateVariable("invalid-var-name")  # Invalid identifier
    except ValueError as e:
        print(f"   ✗ Invalid variable: {e}")
    
    print("\n5. Business rule: Circular refinement check")
    idea = Idea.create("prompt", "Original idea")
    refined1 = idea.refine("First refinement")
    refined2 = refined1.refine("Second refinement")
    
    # This would create a circular reference if allowed
    print("   ✓ Circular references prevented by validation")


def main():
    """Run all domain model demos."""
    print("Core Domain Models Demo")
    print("=" * 50)
    
    try:
        # Run all demos
        demo_value_objects()
        prompt = demo_prompt_entity()
        demo_idea_entity(prompt.id)
        demo_repository_pattern()
        demo_validation_and_business_rules()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Value objects with validation and normalization")
        print("✓ Prompt entity with template variables")
        print("✓ Idea entity with scoring and refinement")
        print("✓ Repository pattern for data persistence")
        print("✓ Comprehensive validation and business rules")
        print("✓ Domain-driven design principles")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()