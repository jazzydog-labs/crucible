"""Tests for repository implementations."""

import pytest
import tempfile
from pathlib import Path

from crucible.domain import Prompt, Idea, Category
from crucible.repository import JSONPromptRepository, JSONIdeaRepository


class TestJSONPromptRepository:
    """Test JSON-based prompt repository."""
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def repository(self, temp_file):
        """Create a repository instance."""
        return JSONPromptRepository(temp_file)
    
    @pytest.fixture
    def sample_prompt(self):
        """Create a sample prompt."""
        return Prompt.create(
            title="Test Prompt",
            content="Generate ideas about {topic}",
            category=Category("Testing"),
            tags=["test", "sample"]
        )
    
    def test_save_and_get(self, repository, sample_prompt):
        """Test saving and retrieving a prompt."""
        repository.save(sample_prompt)
        
        retrieved = repository.get_by_id(sample_prompt.id)
        assert retrieved is not None
        assert retrieved.id == sample_prompt.id
        assert retrieved.title == sample_prompt.title
        assert retrieved.content == sample_prompt.content
    
    def test_get_nonexistent(self, repository):
        """Test getting a non-existent prompt."""
        result = repository.get_by_id("nonexistent-id")
        assert result is None
    
    def test_update_existing(self, repository, sample_prompt):
        """Test updating an existing prompt."""
        repository.save(sample_prompt)
        
        # Update the prompt
        sample_prompt.title = "Updated Title"
        repository.save(sample_prompt)
        
        # Should not create duplicate
        assert repository.count() == 1
        
        retrieved = repository.get_by_id(sample_prompt.id)
        assert retrieved.title == "Updated Title"
    
    def test_get_all(self, repository):
        """Test getting all prompts."""
        prompts = [
            Prompt.create(f"Prompt {i}", f"Content {i}", Category("Test"))
            for i in range(3)
        ]
        
        for prompt in prompts:
            repository.save(prompt)
        
        all_prompts = repository.get_all()
        assert len(all_prompts) == 3
        assert all(isinstance(p, Prompt) for p in all_prompts)
    
    def test_get_by_category(self, repository):
        """Test getting prompts by category."""
        cat1 = Category("Category1")
        cat2 = Category("Category2")
        
        prompt1 = Prompt.create("P1", "C1", cat1)
        prompt2 = Prompt.create("P2", "C2", cat1)
        prompt3 = Prompt.create("P3", "C3", cat2)
        
        repository.save(prompt1)
        repository.save(prompt2)
        repository.save(prompt3)
        
        cat1_prompts = repository.get_by_category("Category1")
        assert len(cat1_prompts) == 2
        
        cat2_prompts = repository.get_by_category("Category2")
        assert len(cat2_prompts) == 1
    
    def test_get_by_tag(self, repository):
        """Test getting prompts by tag."""
        prompt1 = Prompt.create("P1", "C1", Category("Test"), tags=["python", "code"])
        prompt2 = Prompt.create("P2", "C2", Category("Test"), tags=["python", "data"])
        prompt3 = Prompt.create("P3", "C3", Category("Test"), tags=["javascript"])
        
        repository.save(prompt1)
        repository.save(prompt2)
        repository.save(prompt3)
        
        python_prompts = repository.get_by_tag("python")
        assert len(python_prompts) == 2
        
        js_prompts = repository.get_by_tag("javascript")
        assert len(js_prompts) == 1
    
    def test_search(self, repository):
        """Test searching prompts."""
        prompt1 = Prompt.create("Python Tutorial", "Learn Python basics", Category("Education"))
        prompt2 = Prompt.create("JavaScript Guide", "Python vs JavaScript", Category("Education"))
        prompt3 = Prompt.create("Data Science", "Using pandas library", Category("Tech"))
        
        repository.save(prompt1)
        repository.save(prompt2)
        repository.save(prompt3)
        
        # Search in title
        results = repository.search("Python")
        assert len(results) == 2
        
        # Search in content
        results = repository.search("pandas")
        assert len(results) == 1
        
        # Case insensitive
        results = repository.search("PYTHON")
        assert len(results) == 2
    
    def test_delete(self, repository, sample_prompt):
        """Test deleting a prompt."""
        repository.save(sample_prompt)
        assert repository.count() == 1
        
        deleted = repository.delete(sample_prompt.id)
        assert deleted is True
        assert repository.count() == 0
        
        # Delete non-existent
        deleted = repository.delete("nonexistent")
        assert deleted is False
    
    def test_exists(self, repository, sample_prompt):
        """Test checking if prompt exists."""
        assert repository.exists(sample_prompt.id) is False
        
        repository.save(sample_prompt)
        assert repository.exists(sample_prompt.id) is True
    
    def test_clear(self, repository):
        """Test clearing all prompts."""
        for i in range(5):
            prompt = Prompt.create(f"P{i}", f"C{i}", Category("Test"))
            repository.save(prompt)
        
        assert repository.count() == 5
        
        repository.clear()
        assert repository.count() == 0


class TestJSONIdeaRepository:
    """Test JSON-based idea repository."""
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def repository(self, temp_file):
        """Create a repository instance."""
        return JSONIdeaRepository(temp_file)
    
    @pytest.fixture
    def sample_idea(self):
        """Create a sample idea."""
        return Idea.create(
            prompt_id="test-prompt-id",
            content="This is a brilliant idea!",
            score=8.0,
            tags=["innovative"]
        )
    
    def test_save_and_get(self, repository, sample_idea):
        """Test saving and retrieving an idea."""
        repository.save(sample_idea)
        
        retrieved = repository.get_by_id(sample_idea.id)
        assert retrieved is not None
        assert retrieved.id == sample_idea.id
        assert retrieved.content == sample_idea.content
        assert retrieved.score.value == sample_idea.score.value
    
    def test_get_by_prompt_id(self, repository):
        """Test getting ideas by prompt ID."""
        prompt1_ideas = [
            Idea.create("prompt1", f"Idea {i}", score=float(i))
            for i in range(3)
        ]
        prompt2_ideas = [
            Idea.create("prompt2", f"Idea {i}", score=float(i))
            for i in range(2)
        ]
        
        for idea in prompt1_ideas + prompt2_ideas:
            repository.save(idea)
        
        results = repository.get_by_prompt_id("prompt1")
        assert len(results) == 3
        
        results = repository.get_by_prompt_id("prompt2")
        assert len(results) == 2
    
    def test_get_by_score_range(self, repository):
        """Test getting ideas by score range."""
        ideas = [
            Idea.create("prompt", f"Idea {i}", score=float(i * 2))
            for i in range(5)  # scores: 0, 2, 4, 6, 8
        ]
        
        for idea in ideas:
            repository.save(idea)
        
        # Get ideas with scores 4-7
        results = repository.get_by_score_range(4.0, 7.0)
        assert len(results) == 2
        assert all(4.0 <= i.score.value <= 7.0 for i in results)
    
    def test_get_top_ideas(self, repository):
        """Test getting top-scored ideas."""
        ideas = [
            Idea.create("prompt", f"Idea {i}", score=float(i))
            for i in range(10)
        ]
        
        for idea in ideas:
            repository.save(idea)
        
        top_3 = repository.get_top_ideas(limit=3)
        assert len(top_3) == 3
        assert top_3[0].score.value == 9.0
        assert top_3[1].score.value == 8.0
        assert top_3[2].score.value == 7.0
    
    def test_search(self, repository):
        """Test searching ideas."""
        idea1 = Idea.create("p1", "Machine learning is fascinating")
        idea2 = Idea.create("p2", "Deep learning with neural networks")
        idea3 = Idea.create("p3", "Traditional algorithms are still useful")
        
        repository.save(idea1)
        repository.save(idea2)
        repository.save(idea3)
        
        results = repository.search("learning")
        assert len(results) == 2
        
        results = repository.search("LEARNING")  # Case insensitive
        assert len(results) == 2
    
    def test_idea_with_refinements(self, repository):
        """Test saving and loading ideas with refinements."""
        original = Idea.create("prompt", "Original idea", score=6.0)
        refined1 = original.refine("First refinement", score=7.0)
        refined2 = refined1.refine("Second refinement", score=8.0)
        
        repository.save(original)
        
        # Load and check
        loaded = repository.get_by_id(original.id)
        assert loaded is not None
        assert len(loaded.refined_versions) == 1
        assert len(loaded.refined_versions[0].refined_versions) == 1
        assert loaded.get_best_version().score.value == 8.0