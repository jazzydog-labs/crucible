import pytest
from datetime import datetime
from src.crucible.brainstormer import (
    Brainstormer, Idea, IdeaStatus, IdeaEvaluator, IdeaCombiner,
    SCAMPERStrategy, MindMappingStrategy, SixThinkingHatsStrategy, 
    ReverseBrainstormingStrategy
)


class TestIdea:
    def test_idea_creation(self):
        idea = Idea(
            content="Test idea",
            technique="Test technique"
        )
        assert idea.content == "Test idea"
        assert idea.technique == "Test technique"
        assert idea.score == 0.0
        assert idea.status == IdeaStatus.RAW
        assert isinstance(idea.timestamp, datetime)
        assert idea.tags == []
        assert idea.parent_ideas == []
        assert idea.metadata == {}
    
    def test_idea_with_full_params(self):
        idea = Idea(
            content="Test idea",
            technique="Test technique",
            score=0.8,
            tags=["creative", "test"],
            status=IdeaStatus.EVALUATED,
            parent_ideas=["parent1", "parent2"]
        )
        assert idea.score == 0.8
        assert idea.tags == ["creative", "test"]
        assert idea.status == IdeaStatus.EVALUATED
        assert idea.parent_ideas == ["parent1", "parent2"]


class TestSCAMPERStrategy:
    def test_generate_ideas(self):
        strategy = SCAMPERStrategy()
        ideas = strategy.generate_ideas("improve customer service")
        
        assert len(ideas) == 7  # SCAMPER has 7 techniques
        assert all(isinstance(idea, Idea) for idea in ideas)
        assert all("SCAMPER" in idea.technique for idea in ideas)
        assert all("scamper" in idea.tags for idea in ideas)
        
        # Check for specific SCAMPER techniques
        techniques = [idea.technique for idea in ideas]
        assert "SCAMPER-Substitute" in techniques
        assert "SCAMPER-Combine" in techniques
        assert "SCAMPER-Adapt" in techniques
        assert "SCAMPER-Modify" in techniques
        assert "SCAMPER-Put to another use" in techniques
        assert "SCAMPER-Eliminate" in techniques
        assert "SCAMPER-Reverse" in techniques
    
    def test_get_name(self):
        strategy = SCAMPERStrategy()
        assert strategy.get_name() == "SCAMPER"


class TestMindMappingStrategy:
    def test_generate_ideas(self):
        strategy = MindMappingStrategy()
        ideas = strategy.generate_ideas("develop new product")
        
        assert len(ideas) == 6  # 1 central + 5 branches
        assert ideas[0].technique == "Mind Map - Central"
        assert "central" in ideas[0].tags
        
        # Check branches
        branch_names = ["Purpose", "Components", "Connections", "Applications", "Challenges"]
        for i, branch in enumerate(branch_names, 1):
            assert f"Mind Map - {branch}" == ideas[i].technique
            assert "branch" in ideas[i].tags
            assert ideas[0].content in ideas[i].parent_ideas
    
    def test_get_name(self):
        strategy = MindMappingStrategy()
        assert strategy.get_name() == "Mind Mapping"


class TestSixThinkingHatsStrategy:
    def test_generate_ideas(self):
        strategy = SixThinkingHatsStrategy()
        ideas = strategy.generate_ideas("marketing campaign")
        
        assert len(ideas) == 6  # Six hats
        colors = ["White", "Red", "Black", "Yellow", "Green", "Blue"]
        
        for i, color in enumerate(colors):
            assert f"Six Hats - {color}" == ideas[i].technique
            assert color.lower() in ideas[i].tags
            assert "six-hats" in ideas[i].tags
    
    def test_get_name(self):
        strategy = SixThinkingHatsStrategy()
        assert strategy.get_name() == "Six Thinking Hats"


class TestReverseBrainstormingStrategy:
    def test_generate_ideas(self):
        strategy = ReverseBrainstormingStrategy()
        ideas = strategy.generate_ideas("increase sales")
        
        assert len(ideas) == 10  # 5 reverse + 5 solutions
        
        # Check alternating pattern
        for i in range(0, 10, 2):
            assert ideas[i].technique == "Reverse - Problem"
            assert "negative" in ideas[i].tags
            assert ideas[i+1].technique == "Reverse - Solution"
            assert "positive" in ideas[i+1].tags
            assert ideas[i].content in ideas[i+1].parent_ideas
    
    def test_get_name(self):
        strategy = ReverseBrainstormingStrategy()
        assert strategy.get_name() == "Reverse Brainstorming"


class TestIdeaEvaluator:
    def test_evaluate_ideas_default_criteria(self):
        evaluator = IdeaEvaluator()
        ideas = [
            Idea(content="Short idea", technique="Test", tags=["creative"]),
            Idea(content="A much longer idea with more details", technique="Test", tags=[]),
            Idea(content="Medium idea", technique="Test", tags=["tag1", "tag2", "tag3", "green"])
        ]
        
        evaluated = evaluator.evaluate_ideas(ideas)
        
        assert all(idea.status == IdeaStatus.EVALUATED for idea in evaluated)
        assert all(idea.score > 0 for idea in evaluated)
        assert evaluated[0].score >= evaluated[-1].score  # Sorted descending
    
    def test_evaluate_ideas_custom_criteria(self):
        evaluator = IdeaEvaluator()
        ideas = [Idea(content="Test", technique="Test", tags=["creative"])]
        criteria = {"feasibility": 1.0, "impact": 0.0, "novelty": 0.0, "resources": 0.0}
        
        evaluated = evaluator.evaluate_ideas(ideas, criteria)
        
        assert evaluated[0].score > 0
        assert evaluated[0].score <= 1.0


class TestIdeaCombiner:
    def test_combine_ideas(self):
        combiner = IdeaCombiner()
        ideas = [
            Idea(content="First idea", technique="Tech1", tags=["tag1"]),
            Idea(content="Second idea", technique="Tech2", tags=["tag2"]),
            Idea(content="Third idea", technique="Tech3", tags=["tag3"])
        ]
        
        combined = combiner.combine_ideas(ideas)
        
        assert len(combined) <= 3  # Max 3 combinations
        for idea in combined:
            assert idea.status == IdeaStatus.COMBINED
            assert "combined" in idea.tags
            assert len(idea.parent_ideas) == 2
            assert "Combined" in idea.technique
    
    def test_combine_ideas_insufficient(self):
        combiner = IdeaCombiner()
        ideas = [Idea(content="Only one", technique="Tech1")]
        
        combined = combiner.combine_ideas(ideas)
        assert len(combined) == 0
    
    def test_mutate_idea(self):
        combiner = IdeaCombiner()
        original = Idea(content="Original idea", technique="Tech1", tags=["original"])
        
        mutated = combiner.mutate_idea(original)
        
        assert mutated.status == IdeaStatus.REFINED
        assert "mutated" in mutated.tags
        assert "original" in mutated.tags
        assert original.content in mutated.parent_ideas
        assert "Mutated-" in mutated.technique


class TestBrainstormer:
    def test_initialization(self):
        brainstormer = Brainstormer()
        
        assert "scamper" in brainstormer.strategies
        assert "mindmap" in brainstormer.strategies
        assert "sixhats" in brainstormer.strategies
        assert "reverse" in brainstormer.strategies
        assert isinstance(brainstormer.evaluator, IdeaEvaluator)
        assert isinstance(brainstormer.combiner, IdeaCombiner)
        assert brainstormer.all_ideas == []
    
    def test_brainstorm_basic(self):
        brainstormer = Brainstormer()
        payload = {"prompt": "improve workflow"}
        
        ideas = brainstormer.brainstorm(payload)
        
        assert isinstance(ideas, list)
        assert len(ideas) <= 10  # Default max_ideas
        assert all(isinstance(idea, str) for idea in ideas)
        assert len(brainstormer.all_ideas) > 0
    
    def test_brainstorm_specific_techniques(self):
        brainstormer = Brainstormer()
        payload = {
            "prompt": "new features",
            "techniques": ["scamper", "mindmap"],
            "max_ideas": 5
        }
        
        ideas = brainstormer.brainstorm(payload)
        
        assert len(ideas) <= 5
        # Should have ideas from both techniques
        stored_techniques = [idea.technique for idea in brainstormer.all_ideas]
        assert any("SCAMPER" in tech for tech in stored_techniques)
        assert any("Mind Map" in tech for tech in stored_techniques)
    
    def test_brainstorm_without_combination(self):
        brainstormer = Brainstormer()
        payload = {
            "prompt": "test",
            "techniques": ["scamper"],
            "enable_combination": False
        }
        
        ideas = brainstormer.brainstorm(payload)
        
        # Should not have any combined ideas
        assert not any(idea.status == IdeaStatus.COMBINED for idea in brainstormer.all_ideas)
    
    def test_brainstorm_without_evaluation(self):
        brainstormer = Brainstormer()
        payload = {
            "prompt": "test",
            "techniques": ["scamper"],
            "enable_evaluation": False
        }
        
        ideas = brainstormer.brainstorm(payload)
        
        # Ideas should not be evaluated
        assert all(idea.status != IdeaStatus.EVALUATED for idea in brainstormer.all_ideas)
    
    def test_refine_ideas_with_stored(self):
        brainstormer = Brainstormer()
        # Generate some ideas first
        brainstormer.brainstorm({"prompt": "test"})
        
        refined = brainstormer.refine_ideas(iterations=2)
        
        assert isinstance(refined, list)
        assert len(refined) <= 5
    
    def test_refine_ideas_with_input(self):
        brainstormer = Brainstormer()
        input_ideas = ["idea one", "idea two", "idea three"]
        
        refined = brainstormer.refine_ideas(input_ideas, iterations=1)
        
        assert isinstance(refined, list)
        assert len(refined) <= 5
    
    def test_get_idea_history(self):
        brainstormer = Brainstormer()
        brainstormer.brainstorm({"prompt": "test", "techniques": ["scamper"]})
        
        history = brainstormer.get_idea_history()
        
        assert isinstance(history, list)
        assert len(history) > 0
        for entry in history:
            assert "content" in entry
            assert "technique" in entry
            assert "score" in entry
            assert "tags" in entry
            assert "timestamp" in entry
            assert "status" in entry