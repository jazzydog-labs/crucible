import pytest
from unittest.mock import Mock, patch
from src.crucible.summarizer import (
    Summarizer, SummaryResult, OutputFormat, 
    ExtractiveStrategy, AbstractiveStrategy, HierarchicalStrategy, ThemeBasedStrategy,
    IdeaDeduplicator, OutputFormatter
)


class TestExtractiveStrategy:
    def test_summarize_empty_list(self):
        strategy = ExtractiveStrategy()
        result = strategy.summarize([])
        
        assert result.content == "No ideas to summarize."
        assert result.format == OutputFormat.BULLET_POINTS
        assert result.themes == []
        assert result.key_points == []
    
    def test_summarize_single_idea(self):
        strategy = ExtractiveStrategy()
        ideas = ["This is a test idea about software development"]
        result = strategy.summarize(ideas)
        
        assert "This is a test idea about software development" in result.content
        assert result.format == OutputFormat.BULLET_POINTS
        assert len(result.key_points) == 1
    
    def test_summarize_multiple_ideas(self):
        strategy = ExtractiveStrategy()
        ideas = [
            "Microservices architecture enables scalability",
            "Cloud computing provides flexible infrastructure",
            "DevOps practices improve deployment efficiency",
            "Containerization simplifies application deployment",
            "Kubernetes orchestrates container management",
            "Monitoring tools ensure system reliability"
        ]
        result = strategy.summarize(ideas)
        
        # Should select top 30% (2 ideas)
        assert len(result.key_points) <= 5
        assert result.format == OutputFormat.BULLET_POINTS
        assert len(result.themes) > 0
        assert "•" in result.content
    
    def test_summarize_with_max_length(self):
        strategy = ExtractiveStrategy()
        ideas = [
            "Short idea",
            "A much longer idea that contains many words and concepts",
            "Medium length idea here"
        ]
        result = strategy.summarize(ideas, max_length=50)
        
        assert len(result.content) <= 50
        assert result.metadata["selected_ideas"] >= 1
    
    def test_get_name(self):
        strategy = ExtractiveStrategy()
        assert strategy.get_name() == "Extractive"


class TestAbstractiveStrategy:
    def test_summarize_without_ai(self):
        strategy = AbstractiveStrategy(ai_model=None)
        ideas = ["First idea", "Second idea", "Third idea"]
        result = strategy.summarize(ideas)
        
        assert result.format == OutputFormat.PARAGRAPH
        assert result.metadata["method"] == "fallback"
        assert len(result.content) > 0
    
    def test_summarize_with_ai(self):
        mock_ai = Mock()
        mock_ai.query.return_value = "This is an AI-generated summary of the ideas."
        
        strategy = AbstractiveStrategy(ai_model=mock_ai)
        ideas = ["Test idea one", "Test idea two"]
        result = strategy.summarize(ideas)
        
        assert result.content == "This is an AI-generated summary of the ideas."
        assert result.metadata["method"] == "ai"
        mock_ai.query.assert_called_once()
    
    def test_summarize_ai_failure_fallback(self):
        mock_ai = Mock()
        mock_ai.query.side_effect = Exception("API error")
        
        strategy = AbstractiveStrategy(ai_model=mock_ai)
        ideas = ["Idea one", "Idea two"]
        result = strategy.summarize(ideas)
        
        # AI was attempted but failed, so metadata still shows "ai"
        assert result.metadata["method"] == "ai"
        assert len(result.content) > 0
    
    def test_fallback_single_idea(self):
        strategy = AbstractiveStrategy(ai_model=None)
        ideas = ["Single idea"]
        result = strategy.summarize(ideas)
        
        assert result.content == "Single idea"
    
    def test_get_name(self):
        strategy = AbstractiveStrategy()
        assert strategy.get_name() == "Abstractive"


class TestHierarchicalStrategy:
    def test_summarize_creates_hierarchy(self):
        strategy = HierarchicalStrategy()
        ideas = [
            "Implement authentication system",
            "Design database schema",
            "Create authentication flow",
            "Build database connections",
            "Add authentication middleware"
        ]
        result = strategy.summarize(ideas)
        
        assert "##" in result.content  # Headers
        assert "   -" in result.content  # Sub-points
        assert result.format == OutputFormat.HIERARCHICAL
        assert len(result.themes) > 0
    
    def test_cluster_by_theme(self):
        strategy = HierarchicalStrategy()
        ideas = [
            "Testing is important",
            "Testing ensures quality",
            "Security must be considered",
            "Security vulnerabilities are risks"
        ]
        result = strategy.summarize(ideas)
        
        # Should have clusters for testing and security
        assert "Testing" in result.content or "testing" in result.content
        assert "Security" in result.content or "security" in result.content
    
    def test_max_length_truncation(self):
        strategy = HierarchicalStrategy()
        ideas = ["Long idea " * 10 for _ in range(10)]
        result = strategy.summarize(ideas, max_length=100)
        
        assert len(result.content) <= 100
        assert result.content.endswith("...")
    
    def test_get_name(self):
        strategy = HierarchicalStrategy()
        assert strategy.get_name() == "Hierarchical"


class TestThemeBasedStrategy:
    def test_identify_themes(self):
        strategy = ThemeBasedStrategy()
        ideas = [
            "Machine learning improves predictions",
            "Machine learning requires data",
            "Cloud computing enables scalability",
            "Cloud platforms offer flexibility"
        ]
        result = strategy.summarize(ideas)
        
        assert result.format == OutputFormat.NUMBERED_LIST
        assert "Theme:" in result.content
        assert len(result.themes) > 0
        assert "1." in result.content
    
    def test_theme_extraction(self):
        strategy = ThemeBasedStrategy()
        ideas = [
            "Authentication is critical for security",
            "Authorization controls access",
            "Performance optimization matters"
        ]
        result = strategy.summarize(ideas)
        
        # Should identify security/auth as themes
        assert len(result.themes) > 0
        assert result.metadata["themes_found"] > 0
    
    def test_get_name(self):
        strategy = ThemeBasedStrategy()
        assert strategy.get_name() == "Theme-Based"


class TestIdeaDeduplicator:
    def test_deduplicate_identical(self):
        dedup = IdeaDeduplicator()
        ideas = [
            "This is an idea",
            "This is an idea",
            "This is a different idea"
        ]
        result = dedup.deduplicate(ideas)
        
        assert len(result) == 2
        assert "This is an idea" in result
        assert "This is a different idea" in result
    
    def test_deduplicate_similar(self):
        dedup = IdeaDeduplicator()
        ideas = [
            "Build authentication system",
            "Build authentication system.",
            "Create login functionality"
        ]
        result = dedup.deduplicate(ideas, similarity_threshold=0.9)
        
        assert len(result) == 2
    
    def test_deduplicate_empty(self):
        dedup = IdeaDeduplicator()
        assert dedup.deduplicate([]) == []
        assert dedup.deduplicate(["one"]) == ["one"]
    
    def test_similarity_calculation(self):
        dedup = IdeaDeduplicator()
        sim1 = dedup._calculate_similarity("hello world", "hello world")
        assert sim1 == 1.0
        
        sim2 = dedup._calculate_similarity("hello world", "goodbye world")
        assert 0 < sim2 < 1


class TestOutputFormatter:
    def setup_method(self):
        self.formatter = OutputFormatter()
        self.sample_result = SummaryResult(
            content="Line 1\nLine 2\nLine 3",
            format=OutputFormat.PARAGRAPH,
            metadata={},
            themes=["theme1", "theme2"],
            key_points=["point1", "point2"]
        )
    
    def test_format_bullets(self):
        formatted = self.formatter._format_bullets(self.sample_result)
        assert "•" in formatted
        assert "Line 1" in formatted
    
    def test_format_paragraph(self):
        # Test with a result that's already in paragraph format
        self.sample_result.format = OutputFormat.PARAGRAPH
        formatted = self.formatter._format_paragraph(self.sample_result)
        assert formatted == self.sample_result.content
        
        # Test conversion from bullet format
        bullet_result = SummaryResult(
            content="• Bullet point\n• Another point",
            format=OutputFormat.BULLET_POINTS,
            metadata={},
            themes=[],
            key_points=[]
        )
        formatted_bullets = self.formatter._format_paragraph(bullet_result)
        assert "•" not in formatted_bullets
        assert "Bullet point" in formatted_bullets
        assert "Another point" in formatted_bullets
    
    def test_format_numbered(self):
        formatted = self.formatter._format_numbered(self.sample_result)
        assert "1." in formatted
        assert "2." in formatted
        assert "3." in formatted
    
    def test_format_hierarchical(self):
        formatted = self.formatter._format_hierarchical(self.sample_result)
        assert "##" in formatted
        assert "Theme1" in formatted or "theme1" in formatted
    
    def test_format_mindmap(self):
        formatted = self.formatter._format_mindmap(self.sample_result)
        assert "[Central Topic]" in formatted
        assert "├─" in formatted
        assert "Theme1" in formatted or "theme1" in formatted


class TestSummarizer:
    def test_initialization(self):
        summarizer = Summarizer()
        
        assert "extractive" in summarizer.strategies
        assert "abstractive" in summarizer.strategies
        assert "hierarchical" in summarizer.strategies
        assert "theme_based" in summarizer.strategies
        assert hasattr(summarizer, "deduplicator")
        assert hasattr(summarizer, "formatter")
    
    def test_summarize_default_strategy(self):
        summarizer = Summarizer()
        payload = {"ideas": ["Idea 1", "Idea 2", "Idea 3"]}
        
        result = summarizer.summarize(payload)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_summarize_with_strategy(self):
        summarizer = Summarizer()
        payload = {
            "ideas": ["Test idea one", "Test idea two"],
            "strategy": "hierarchical"
        }
        
        result = summarizer.summarize(payload)
        assert "##" in result  # Hierarchical format
    
    def test_summarize_with_deduplication(self):
        summarizer = Summarizer()
        payload = {
            "ideas": ["Same idea", "Same idea", "Different idea"],
            "deduplicate": True
        }
        
        result = summarizer.summarize(payload)
        # Should have deduplicated
        assert result.count("Same idea") < 2
    
    def test_summarize_without_deduplication(self):
        summarizer = Summarizer()
        payload = {
            "ideas": ["Same", "Same"],
            "deduplicate": False,
            "strategy": "extractive"
        }
        
        result = summarizer.summarize(payload)
        # Both should be present
        assert "Same" in result
    
    def test_summarize_with_output_format(self):
        summarizer = Summarizer()
        payload = {
            "ideas": ["Idea one", "Idea two"],
            "output_format": "numbered_list"
        }
        
        result = summarizer.summarize(payload)
        assert "1." in result or "2." in result
    
    def test_summarize_with_metadata(self):
        summarizer = Summarizer()
        payload = {"ideas": ["Test idea"]}
        
        result = summarizer.summarize_with_metadata(payload)
        assert isinstance(result, SummaryResult)
        assert result.content
        assert isinstance(result.metadata, dict)
        assert isinstance(result.themes, list)
        assert isinstance(result.key_points, list)
    
    def test_handle_dict_ideas(self):
        summarizer = Summarizer()
        payload = {
            "ideas": [
                {"content": "First idea", "score": 0.8},
                {"content": "Second idea", "score": 0.6}
            ]
        }
        
        result = summarizer.summarize(payload)
        assert "First idea" in result or "Second idea" in result
    
    def test_get_available_strategies(self):
        summarizer = Summarizer()
        strategies = summarizer.get_available_strategies()
        
        assert "extractive" in strategies
        assert "abstractive" in strategies
        assert "hierarchical" in strategies
        assert "theme_based" in strategies
    
    def test_get_available_formats(self):
        summarizer = Summarizer()
        formats = summarizer.get_available_formats()
        
        assert "bullet_points" in formats
        assert "paragraph" in formats
        assert "numbered_list" in formats
        assert "hierarchical" in formats
        assert "mind_map" in formats