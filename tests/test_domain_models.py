"""Tests for domain models."""

import pytest
from datetime import datetime
import uuid

from crucible.domain import Prompt, Idea, Tag, Score, Category
from crucible.domain.value_objects import TemplateVariable, ValidationResult


class TestValueObjects:
    """Test value objects."""
    
    def test_tag_creation(self):
        """Test tag creation and normalization."""
        tag = Tag("Test-Tag")
        assert tag.value == "test-tag"
        
        tag2 = Tag("Test Tag!@#")
        assert tag2.value == "test-tag"
        
        tag3 = Tag("test--multiple---dashes")
        assert tag3.value == "test-multiple-dashes"
    
    def test_tag_validation(self):
        """Test tag validation."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Tag("")
        
        with pytest.raises(ValueError, match="cannot be longer than 50"):
            Tag("a" * 51)
    
    def test_score_creation(self):
        """Test score creation and validation."""
        score = Score(7.5)
        assert score.value == 7.5
        assert str(score) == "7.5"
        
        default_score = Score.default()
        assert default_score.value == 5.0
    
    def test_score_validation(self):
        """Test score validation."""
        with pytest.raises(ValueError, match="must be between"):
            Score(-1.0)
        
        with pytest.raises(ValueError, match="must be between"):
            Score(10.5)
    
    def test_score_comparison(self):
        """Test score comparison."""
        score1 = Score(3.0)
        score2 = Score(7.0)
        score3 = Score(7.0)
        
        assert score1 < score2
        assert score2 > score1
        assert score2 == score3
        assert score1 <= score2
        assert score2 >= score3
    
    def test_score_conversion(self):
        """Test score percentage conversion."""
        score = Score.from_percentage(75.0)
        assert score.value == 7.5
        assert score.to_percentage() == 75.0
    
    def test_category_creation(self):
        """Test category creation and normalization."""
        cat = Category("test category", "A test category")
        assert cat.name == "Test Category"
        assert cat.description == "A test category"
        
        cat2 = Category("Test!@#Category123")
        assert cat2.name == "Testcategory123"
    
    def test_category_validation(self):
        """Test category validation."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Category("")
        
        with pytest.raises(ValueError, match="cannot be longer than 100"):
            Category("a" * 101)
    
    def test_template_variable(self):
        """Test template variable."""
        var = TemplateVariable("topic", "The main topic", "default", required=True)
        assert var.name == "topic"
        assert var.description == "The main topic"
        assert var.default_value == "default"
        assert var.required is True
        assert str(var) == "{topic}"
    
    def test_template_variable_validation(self):
        """Test template variable validation."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TemplateVariable("")
        
        with pytest.raises(ValueError, match="not a valid identifier"):
            TemplateVariable("invalid-name")
    
    def test_validation_result(self):
        """Test validation result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert bool(result) is True
        
        result.add_error("Test error")
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert bool(result) is False
        
        result.add_warning("Test warning")
        assert len(result.warnings) == 1


class TestPrompt:
    """Test Prompt entity."""
    
    def test_prompt_creation(self):
        """Test prompt creation."""
        category = Category("Brainstorming")
        prompt = Prompt.create(
            title="Test Prompt",
            content="Generate ideas about {topic}",
            category=category,
            tags=["creative", "ideas"]
        )
        
        assert prompt.id is not None
        assert prompt.title == "Test Prompt"
        assert prompt.content == "Generate ideas about {topic}"
        assert prompt.category.name == "Brainstorming"
        assert len(prompt.tags) == 2
        assert prompt.tags[0].value == "creative"
        assert prompt.tags[1].value == "ideas"
    
    def test_prompt_variable_extraction(self):
        """Test automatic variable extraction."""
        category = Category("Test")
        prompt = Prompt.create(
            title="Variable Test",
            content="Hello {name}, let's discuss {topic} in {location}",
            category=category
        )
        
        assert len(prompt.variables) == 3
        assert "name" in prompt.variables
        assert "topic" in prompt.variables
        assert "location" in prompt.variables
        assert all(var.required for var in prompt.variables.values())
    
    def test_prompt_rendering(self):
        """Test prompt rendering."""
        category = Category("Test")
        prompt = Prompt.create(
            title="Render Test",
            content="Hello {name}, welcome to {place}!",
            category=category
        )
        
        rendered = prompt.render({"name": "Alice", "place": "Wonderland"})
        assert rendered == "Hello Alice, welcome to Wonderland!"
    
    def test_prompt_rendering_with_defaults(self):
        """Test prompt rendering with default values."""
        category = Category("Test")
        prompt = Prompt.create(
            title="Default Test",
            content="Hello {name}!",
            category=category
        )
        
        # Replace with a variable that has a default value
        prompt.variables["name"] = TemplateVariable(
            name="name",
            description="Name to greet",
            default_value="World",
            required=True
        )
        
        # Should use default when not provided
        rendered = prompt.render({})
        assert rendered == "Hello World!"
    
    def test_prompt_rendering_missing_required(self):
        """Test prompt rendering with missing required variables."""
        category = Category("Test")
        prompt = Prompt.create(
            title="Missing Test",
            content="Hello {name} from {city}!",
            category=category
        )
        
        with pytest.raises(KeyError, match="Missing required variables"):
            prompt.render({"name": "Alice"})
    
    def test_prompt_validation(self):
        """Test prompt validation."""
        category = Category("Test")
        
        # Valid prompt
        prompt = Prompt.create(
            title="Valid Prompt",
            content="Test content",
            category=category
        )
        result = prompt.validate()
        assert result.is_valid is True
        
        # Empty title
        prompt.title = ""
        result = prompt.validate()
        assert result.is_valid is False
        assert "Title cannot be empty" in result.errors
        
        # Empty content
        prompt.title = "Test"
        prompt.content = ""
        result = prompt.validate()
        assert result.is_valid is False
        assert "Content cannot be empty" in result.errors
    
    def test_prompt_tag_management(self):
        """Test prompt tag management."""
        category = Category("Test")
        prompt = Prompt.create(
            title="Tag Test",
            content="Test content",
            category=category,
            tags=["tag1"]
        )
        
        assert len(prompt.tags) == 1
        
        prompt.add_tag("tag2")
        assert len(prompt.tags) == 2
        
        # Duplicate tag should not be added
        prompt.add_tag("tag2")
        assert len(prompt.tags) == 2
        
        prompt.remove_tag("tag1")
        assert len(prompt.tags) == 1
        assert prompt.tags[0].value == "tag2"
    
    def test_prompt_serialization(self):
        """Test prompt serialization."""
        category = Category("Test", "Test category")
        prompt = Prompt.create(
            title="Serialization Test",
            content="Test {variable}",
            category=category,
            tags=["test", "serial"]
        )
        
        # To dict
        prompt_dict = prompt.to_dict()
        assert prompt_dict["id"] == prompt.id
        assert prompt_dict["title"] == prompt.title
        assert prompt_dict["content"] == prompt.content
        assert prompt_dict["category"]["name"] == "Test"
        assert len(prompt_dict["tags"]) == 2
        assert "variable" in prompt_dict["variables"]
        
        # From dict
        restored = Prompt.from_dict(prompt_dict)
        assert restored.id == prompt.id
        assert restored.title == prompt.title
        assert restored.content == prompt.content
        assert restored.category.name == prompt.category.name
        assert len(restored.tags) == len(prompt.tags)


class TestIdea:
    """Test Idea entity."""
    
    def test_idea_creation(self):
        """Test idea creation."""
        idea = Idea.create(
            prompt_id="test-prompt-id",
            content="This is a great idea!",
            score=8.5,
            tags=["innovative", "practical"]
        )
        
        assert idea.id is not None
        assert idea.prompt_id == "test-prompt-id"
        assert idea.content == "This is a great idea!"
        assert idea.score.value == 8.5
        assert len(idea.tags) == 2
        assert idea.parent_idea_id is None
    
    def test_idea_refinement(self):
        """Test idea refinement."""
        original = Idea.create(
            prompt_id="test-prompt",
            content="Original idea",
            score=6.0
        )
        
        refined = original.refine(
            "Improved idea",
            score=8.0,
            tags=["refined"]
        )
        
        assert refined.parent_idea_id == original.id
        assert refined.prompt_id == original.prompt_id
        assert refined.content == "Improved idea"
        assert refined.score.value == 8.0
        assert len(original.refined_versions) == 1
        assert original.refined_versions[0] == refined
    
    def test_idea_score_update(self):
        """Test idea score update."""
        idea = Idea.create(
            prompt_id="test",
            content="Test idea",
            score=5.0
        )
        
        idea.update_score(7.5)
        assert idea.score.value == 7.5
        
        with pytest.raises(ValueError):
            idea.update_score(11.0)
    
    def test_idea_metadata(self):
        """Test idea metadata management."""
        idea = Idea.create(
            prompt_id="test",
            content="Test idea",
            metadata={"source": "brainstorm"}
        )
        
        assert idea.get_metadata("source") == "brainstorm"
        assert idea.get_metadata("missing", "default") == "default"
        
        idea.add_metadata("author", "Alice")
        assert idea.get_metadata("author") == "Alice"
    
    def test_idea_versions(self):
        """Test idea version management."""
        original = Idea.create(
            prompt_id="test",
            content="Version 1",
            score=5.0
        )
        
        v2 = original.refine("Version 2", score=6.0)
        v3 = v2.refine("Version 3", score=8.0)
        v4 = original.refine("Version 4", score=7.0)
        
        all_versions = original.get_all_versions()
        assert len(all_versions) == 4
        
        best = original.get_best_version()
        assert best.content == "Version 3"
        assert best.score.value == 8.0
    
    def test_idea_validation(self):
        """Test idea validation."""
        # Valid idea
        idea = Idea.create(
            prompt_id="test",
            content="Valid content"
        )
        result = idea.validate()
        assert result.is_valid is True
        
        # Empty content
        idea.content = ""
        result = idea.validate()
        assert result.is_valid is False
        assert "Content cannot be empty" in result.errors
        
        # Empty prompt_id
        idea.content = "Test"
        idea.prompt_id = ""
        result = idea.validate()
        assert result.is_valid is False
        assert "Prompt ID cannot be empty" in result.errors
    
    def test_idea_serialization(self):
        """Test idea serialization."""
        idea = Idea.create(
            prompt_id="test-prompt",
            content="Test idea",
            score=7.5,
            tags=["test"],
            metadata={"key": "value"}
        )
        
        # Add a refined version
        refined = idea.refine("Refined idea", score=8.0)
        
        # To dict
        idea_dict = idea.to_dict()
        assert idea_dict["id"] == idea.id
        assert idea_dict["prompt_id"] == idea.prompt_id
        assert idea_dict["content"] == idea.content
        assert idea_dict["score"] == 7.5
        assert len(idea_dict["refined_versions"]) == 1
        
        # From dict
        restored = Idea.from_dict(idea_dict)
        assert restored.id == idea.id
        assert restored.prompt_id == idea.prompt_id
        assert restored.content == idea.content
        assert restored.score.value == idea.score.value
        assert len(restored.refined_versions) == 1
        assert restored.refined_versions[0].content == "Refined idea"