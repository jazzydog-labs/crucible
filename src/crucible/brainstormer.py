from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random
from enum import Enum


class IdeaStatus(Enum):
    RAW = "raw"
    REFINED = "refined"
    EVALUATED = "evaluated"
    COMBINED = "combined"


@dataclass
class Idea:
    content: str
    technique: str
    timestamp: datetime = field(default_factory=datetime.now)
    score: float = 0.0
    tags: List[str] = field(default_factory=list)
    status: IdeaStatus = IdeaStatus.RAW
    parent_ideas: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrainstormingStrategy(ABC):
    """Base class for brainstorming strategies."""
    
    @abstractmethod
    def generate_ideas(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[Idea]:
        """Generate ideas based on the prompt and optional context."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the brainstorming technique."""
        pass


class SCAMPERStrategy(BrainstormingStrategy):
    """SCAMPER: Substitute, Combine, Adapt, Modify, Put to another use, Eliminate, Reverse."""
    
    def get_name(self) -> str:
        return "SCAMPER"
    
    def generate_ideas(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[Idea]:
        ideas = []
        scamper_prompts = {
            "Substitute": f"What can be substituted in '{prompt}'?",
            "Combine": f"What can be combined with '{prompt}'?",
            "Adapt": f"How can '{prompt}' be adapted for different uses?",
            "Modify": f"How can '{prompt}' be magnified or minimized?",
            "Put to another use": f"What else can '{prompt}' be used for?",
            "Eliminate": f"What can be removed from '{prompt}'?",
            "Reverse": f"How can '{prompt}' be reversed or rearranged?"
        }
        
        for technique, question in scamper_prompts.items():
            idea = Idea(
                content=f"{question} Consider {technique.lower()}ing key elements.",
                technique=f"SCAMPER-{technique}",
                tags=[technique.lower(), "scamper", "creative"]
            )
            ideas.append(idea)
        
        return ideas


class MindMappingStrategy(BrainstormingStrategy):
    """Mind mapping approach for hierarchical idea generation."""
    
    def get_name(self) -> str:
        return "Mind Mapping"
    
    def generate_ideas(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[Idea]:
        ideas = []
        
        # Central concept
        central = Idea(
            content=f"Central theme: {prompt}",
            technique="Mind Map - Central",
            tags=["central", "mindmap", "core"]
        )
        ideas.append(central)
        
        # Primary branches
        branches = [
            ("Purpose", "What is the main purpose or goal?"),
            ("Components", "What are the key components or elements?"),
            ("Connections", "How does it connect to other concepts?"),
            ("Applications", "What are practical applications?"),
            ("Challenges", "What challenges or obstacles exist?")
        ]
        
        for branch_name, question in branches:
            idea = Idea(
                content=f"{branch_name}: {question} (related to {prompt})",
                technique=f"Mind Map - {branch_name}",
                tags=["branch", "mindmap", branch_name.lower()],
                parent_ideas=[central.content]
            )
            ideas.append(idea)
        
        return ideas


class SixThinkingHatsStrategy(BrainstormingStrategy):
    """Edward de Bono's Six Thinking Hats method."""
    
    def get_name(self) -> str:
        return "Six Thinking Hats"
    
    def generate_ideas(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[Idea]:
        ideas = []
        hats = {
            "White": ("Facts and Information", "What facts and data do we have about"),
            "Red": ("Emotions and Intuition", "What are the emotional aspects of"),
            "Black": ("Critical Judgment", "What are the risks and downsides of"),
            "Yellow": ("Positive Thinking", "What are the benefits and opportunities of"),
            "Green": ("Creative Thinking", "What creative solutions exist for"),
            "Blue": ("Process Control", "How should we organize thinking about")
        }
        
        for color, (hat_type, question_start) in hats.items():
            idea = Idea(
                content=f"{color} Hat ({hat_type}): {question_start} {prompt}?",
                technique=f"Six Hats - {color}",
                tags=[color.lower(), "six-hats", hat_type.lower().replace(" ", "-")]
            )
            ideas.append(idea)
        
        return ideas


class ReverseBrainstormingStrategy(BrainstormingStrategy):
    """Generate ideas by thinking about the opposite of the goal."""
    
    def get_name(self) -> str:
        return "Reverse Brainstorming"
    
    def generate_ideas(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> List[Idea]:
        ideas = []
        
        # Generate reverse questions
        reverse_prompts = [
            f"How could we make {prompt} fail completely?",
            f"What would be the worst way to approach {prompt}?",
            f"How can we ensure {prompt} never succeeds?",
            f"What obstacles could prevent {prompt}?",
            f"What would the opposite of {prompt} look like?"
        ]
        
        for i, reverse_prompt in enumerate(reverse_prompts):
            # First, the reverse idea
            reverse_idea = Idea(
                content=reverse_prompt,
                technique="Reverse - Problem",
                tags=["reverse", "problem", "negative"]
            )
            ideas.append(reverse_idea)
            
            # Then, flip it to a solution
            solution_idea = Idea(
                content=f"Solution: Avoid or address the issues raised by '{reverse_prompt}'",
                technique="Reverse - Solution",
                tags=["reverse", "solution", "positive"],
                parent_ideas=[reverse_idea.content]
            )
            ideas.append(solution_idea)
        
        return ideas


class IdeaEvaluator:
    """Evaluates and ranks ideas based on various criteria."""
    
    def evaluate_ideas(self, ideas: List[Idea], criteria: Optional[Dict[str, float]] = None) -> List[Idea]:
        """Evaluate ideas and assign scores."""
        if criteria is None:
            criteria = {
                "feasibility": 0.3,
                "impact": 0.3,
                "novelty": 0.2,
                "resources": 0.2
            }
        
        for idea in ideas:
            # Simple scoring based on content characteristics
            score = 0.0
            
            # Feasibility: shorter ideas might be more feasible
            feasibility = min(1.0, 100 / (len(idea.content) + 1))
            score += feasibility * criteria.get("feasibility", 0)
            
            # Impact: ideas with more tags might have broader impact
            impact = min(1.0, len(idea.tags) / 5)
            score += impact * criteria.get("impact", 0)
            
            # Novelty: ideas from creative techniques get bonus
            novelty = 1.0 if any(tag in ["creative", "reverse", "green"] for tag in idea.tags) else 0.5
            score += novelty * criteria.get("novelty", 0)
            
            # Resources: simpler techniques require fewer resources
            resources = 0.8 if "simple" in idea.technique.lower() else 0.5
            score += resources * criteria.get("resources", 0)
            
            idea.score = round(score, 2)
            idea.status = IdeaStatus.EVALUATED
        
        return sorted(ideas, key=lambda x: x.score, reverse=True)


class IdeaCombiner:
    """Combines and mutates ideas to create new ones."""
    
    def combine_ideas(self, ideas: List[Idea]) -> List[Idea]:
        """Combine pairs of ideas to create new ones."""
        combined_ideas = []
        
        # Only combine if we have at least 2 ideas
        if len(ideas) < 2:
            return combined_ideas
        
        # Combine ideas from different techniques
        for i in range(min(3, len(ideas) // 2)):  # Limit combinations
            idea1, idea2 = random.sample(ideas, 2)
            
            combined = Idea(
                content=f"Combine: {idea1.content[:50]}... WITH {idea2.content[:50]}...",
                technique=f"Combined ({idea1.technique} + {idea2.technique})",
                tags=list(set(idea1.tags + idea2.tags + ["combined"])),
                status=IdeaStatus.COMBINED,
                parent_ideas=[idea1.content, idea2.content]
            )
            combined_ideas.append(combined)
        
        return combined_ideas
    
    def mutate_idea(self, idea: Idea) -> Idea:
        """Create a variation of an existing idea."""
        mutations = [
            "Simplified version",
            "Extended version",
            "Opposite approach",
            "Hybrid approach",
            "Minimal viable version"
        ]
        
        mutation_type = random.choice(mutations)
        mutated = Idea(
            content=f"{mutation_type}: {idea.content}",
            technique=f"Mutated-{idea.technique}",
            tags=idea.tags + ["mutated", mutation_type.lower().replace(" ", "-")],
            status=IdeaStatus.REFINED,
            parent_ideas=[idea.content]
        )
        
        return mutated


class Brainstormer:
    """Main brainstorming class that orchestrates different strategies."""
    
    def __init__(self):
        self.strategies = {
            "scamper": SCAMPERStrategy(),
            "mindmap": MindMappingStrategy(),
            "sixhats": SixThinkingHatsStrategy(),
            "reverse": ReverseBrainstormingStrategy()
        }
        self.evaluator = IdeaEvaluator()
        self.combiner = IdeaCombiner()
        self.all_ideas: List[Idea] = []
    
    def brainstorm(self, payload: Dict[str, Any]) -> List[str]:
        """Main brainstorming method that uses multiple techniques."""
        prompt = payload.get("prompt", "")
        techniques = payload.get("techniques", list(self.strategies.keys()))
        max_ideas = payload.get("max_ideas", 10)
        enable_combination = payload.get("enable_combination", True)
        enable_evaluation = payload.get("enable_evaluation", True)
        
        # Generate ideas using selected techniques
        raw_ideas = []
        for technique in techniques:
            if technique in self.strategies:
                strategy = self.strategies[technique]
                ideas = strategy.generate_ideas(prompt, payload.get("context"))
                raw_ideas.extend(ideas)
        
        # Store all generated ideas
        self.all_ideas.extend(raw_ideas)
        
        # Combine ideas if enabled
        if enable_combination and len(raw_ideas) > 1:
            combined = self.combiner.combine_ideas(raw_ideas)
            raw_ideas.extend(combined)
        
        # Evaluate ideas if enabled
        if enable_evaluation:
            evaluated_ideas = self.evaluator.evaluate_ideas(
                raw_ideas, 
                payload.get("evaluation_criteria")
            )
        else:
            evaluated_ideas = raw_ideas
        
        # Return top ideas as strings
        top_ideas = evaluated_ideas[:max_ideas]
        return [idea.content for idea in top_ideas]
    
    def refine_ideas(self, ideas: Optional[List[str]] = None, iterations: int = 1) -> List[str]:
        """Iteratively refine ideas through mutation and recombination."""
        if ideas is None:
            # Use stored ideas
            working_ideas = self.all_ideas[-10:]  # Last 10 ideas
        else:
            # Convert strings back to Idea objects
            working_ideas = [Idea(content=idea, technique="User Input") for idea in ideas]
        
        refined_ideas = []
        for _ in range(iterations):
            for idea in working_ideas:
                if random.random() > 0.5:  # 50% chance to mutate
                    mutated = self.combiner.mutate_idea(idea)
                    refined_ideas.append(mutated)
        
        # Evaluate and return refined ideas
        if refined_ideas:
            evaluated = self.evaluator.evaluate_ideas(refined_ideas)
            return [idea.content for idea in evaluated[:5]]
        
        return []
    
    def get_idea_history(self) -> List[Dict[str, Any]]:
        """Return the history of all generated ideas."""
        return [
            {
                "content": idea.content,
                "technique": idea.technique,
                "score": idea.score,
                "tags": idea.tags,
                "timestamp": idea.timestamp.isoformat(),
                "status": idea.status.value
            }
            for idea in self.all_ideas
        ]