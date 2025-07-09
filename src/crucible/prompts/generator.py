"""Prompt generation logic that utilises the LLM if available."""

from __future__ import annotations

import string
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, TYPE_CHECKING

# Local import kept inside try-except so the package remains optional for
# environments where ``openai`` is not installed (e.g. CI without network).

if TYPE_CHECKING:  # pragma: no cover
    from ..ai import AIModel


class PromptType(Enum):
    """Types of prompts that can be generated."""
    BRAINSTORMING = "brainstorming"
    ANALYSIS = "analysis"
    REFINEMENT = "refinement"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    EXPLORATION = "exploration"
    PROBLEM_SOLVING = "problem_solving"


class PromptTemplate:
    """Template for generating prompts with variable substitution."""
    
    def __init__(self, template: str, variables: Optional[List[str]] = None):
        self.template = template
        self.variables = variables or self._extract_variables(template)
    
    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from template string."""
        formatter = string.Formatter()
        return [field_name for _, field_name, _, _ in formatter.parse(template) if field_name]
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render template with provided context."""
        return self.template.format(**context)
    
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Check if context contains all required variables."""
        return all(var in context for var in self.variables)

class PromptGenerator:
    """Enhanced prompt generator with support for different prompt types and templates.

    This class provides sophisticated prompt generation capabilities including:
    - Multiple prompt types (brainstorming, analysis, refinement, etc.)
    - Template-based generation with variable substitution
    - AI-powered prompt optimization when available
    - Context-aware prompt adaptation
    - Prompt chaining for multi-stage workflows
    """
    
    # Built-in prompt templates for different types
    TEMPLATES = {
        PromptType.BRAINSTORMING: PromptTemplate(
            "Generate {num_ideas} innovative and creative ideas for {topic}. "
            "Consider different perspectives, approaches, and unconventional solutions. "
            "Focus on {focus_area} and think about how this could impact {target_audience}."
        ),
        PromptType.ANALYSIS: PromptTemplate(
            "Analyze {topic} from multiple angles. Consider the following aspects: "
            "strengths, weaknesses, opportunities, threats, and implications. "
            "Provide a structured analysis that examines {focus_area} in depth."
        ),
        PromptType.REFINEMENT: PromptTemplate(
            "Refine and improve the following concept: {concept}. "
            "Focus on enhancing {improvement_areas} while maintaining {core_constraints}. "
            "Provide specific, actionable improvements."
        ),
        PromptType.SYNTHESIS: PromptTemplate(
            "Synthesize insights from {sources} related to {topic}. "
            "Identify common themes, conflicting viewpoints, and emerging patterns. "
            "Create a unified perspective that integrates {key_elements}."
        ),
        PromptType.EVALUATION: PromptTemplate(
            "Evaluate {options} for {topic} using {criteria}. "
            "Provide a structured comparison that weighs {evaluation_factors}. "
            "Make a recommendation based on your analysis."
        ),
        PromptType.EXPLORATION: PromptTemplate(
            "Explore {topic} by investigating {exploration_areas}. "
            "Ask probing questions, challenge assumptions, and consider "
            "alternative viewpoints. Focus on discovering {discovery_goals}."
        ),
        PromptType.PROBLEM_SOLVING: PromptTemplate(
            "Solve the following problem: {problem}. "
            "Use a systematic approach considering {constraints} and {resources}. "
            "Provide step-by-step solutions that address {success_criteria}."
        )
    }

    def __init__(self, ai_model: "AIModel | None" = None):
        # Import lazily to avoid hard dependency on openai for non-AI workflows.
        if ai_model is not None:
            self._ai = ai_model
        else:
            try:
                from ..ai import AIModel  # Local import to sidestep optional dep.

                self._ai = AIModel()
            except Exception:  # pragma: no cover – missing dependency etc.
                # We store *None* so generate() can detect unavailable AI.
                self._ai = None
        
        # Custom templates can be added at runtime
        self._custom_templates: Dict[str, PromptTemplate] = {}

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def generate(self, context: Mapping[str, Any] | None = None) -> str:
        """Generate a prompt based on context.
        
        Args:
            context: Dictionary containing prompt generation parameters:
                - prompt_type: PromptType enum value
                - topic: Main topic for the prompt
                - Additional context variables based on prompt type
                
        Returns:
            Generated prompt string
        """
        context = dict(context or {})
        prompt_type = context.get("prompt_type", PromptType.BRAINSTORMING)
        
        # Handle string prompt types for backward compatibility
        if isinstance(prompt_type, str):
            try:
                prompt_type = PromptType(prompt_type)
            except ValueError:
                prompt_type = PromptType.BRAINSTORMING
        
        return self._generate_typed_prompt(prompt_type, context)
    
    def generate_chain(self, prompts: List[Dict[str, Any]]) -> List[str]:
        """Generate a chain of related prompts for multi-stage workflows.
        
        Args:
            prompts: List of context dictionaries for each prompt in the chain
            
        Returns:
            List of generated prompt strings
        """
        results = []
        for prompt_context in prompts:
            generated = self.generate(prompt_context)
            results.append(generated)
            # Add previous result to context for next prompt
            if len(results) > 1:
                prompt_context["previous_result"] = results[-2]
        return results
    
    def add_template(self, name: str, template: PromptTemplate) -> None:
        """Add a custom prompt template.
        
        Args:
            name: Unique name for the template
            template: PromptTemplate instance
        """
        self._custom_templates[name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            PromptTemplate instance or None if not found
        """
        return self._custom_templates.get(name)
    
    def validate_context(self, prompt_type: PromptType, context: Dict[str, Any]) -> List[str]:
        """Validate context for a given prompt type.
        
        Args:
            prompt_type: Type of prompt to validate for
            context: Context dictionary to validate
            
        Returns:
            List of missing required variables
        """
        template = self.TEMPLATES.get(prompt_type)
        if not template:
            return []
        
        missing = [var for var in template.variables if var not in context]
        return missing
    
    # ---------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------
    
    def _generate_typed_prompt(self, prompt_type: PromptType, context: Dict[str, Any]) -> str:
        """Generate a prompt for a specific type.
        
        Args:
            prompt_type: Type of prompt to generate
            context: Context for prompt generation
            
        Returns:
            Generated prompt string
        """
        # First try to use AI for enhanced generation
        if self._ai is not None:
            ai_prompt = self._generate_ai_prompt(prompt_type, context)
            if ai_prompt:
                return ai_prompt
        
        # Fall back to template-based generation
        return self._generate_template_prompt(prompt_type, context)
    
    def _generate_ai_prompt(self, prompt_type: PromptType, context: Dict[str, Any]) -> Optional[str]:
        """Generate prompt using AI model.
        
        Args:
            prompt_type: Type of prompt to generate
            context: Context for prompt generation
            
        Returns:
            AI-generated prompt or None if failed
        """
        try:
            # Create AI system instruction based on prompt type
            system_instructions = {
                PromptType.BRAINSTORMING: "You are an expert brainstorming facilitator. Create prompts that encourage creative, divergent thinking.",
                PromptType.ANALYSIS: "You are a skilled analyst. Create prompts that encourage systematic, thorough analysis.",
                PromptType.REFINEMENT: "You are an improvement expert. Create prompts that focus on enhancement and optimization.",
                PromptType.SYNTHESIS: "You are a synthesis expert. Create prompts that help integrate and combine ideas.",
                PromptType.EVALUATION: "You are an evaluation expert. Create prompts that help assess and compare options.",
                PromptType.EXPLORATION: "You are an exploration guide. Create prompts that encourage discovery and investigation.",
                PromptType.PROBLEM_SOLVING: "You are a problem-solving expert. Create prompts that lead to systematic solutions."
            }
            
            system_instruction = system_instructions.get(prompt_type, system_instructions[PromptType.BRAINSTORMING])
            
            # Build context description
            context_items = [f"{k}: {v}" for k, v in context.items() if k != "prompt_type"]
            context_str = ", ".join(context_items)
            
            full_prompt = f"{system_instruction}\n\nContext: {context_str}\n\nCreate a focused, engaging prompt that addresses this context. Return only the prompt text."
            
            return self._ai.query(full_prompt)
        except Exception as exc:  # pragma: no cover – network/API issues.
            print(f"AIModel error – falling back to template. Detail: {exc}")
            return None
    
    def _generate_template_prompt(self, prompt_type: PromptType, context: Dict[str, Any]) -> str:
        """Generate prompt using built-in templates.
        
        Args:
            prompt_type: Type of prompt to generate
            context: Context for prompt generation
            
        Returns:
            Template-generated prompt
        """
        template = self.TEMPLATES.get(prompt_type)
        if not template:
            # Fallback to simple brainstorming prompt
            topic = context.get("topic", "an unspecified topic")
            return f"Generate ideas and insights about '{topic}'."
        
        # Fill in missing variables with reasonable defaults
        filled_context = self._fill_context_defaults(prompt_type, context)
        
        try:
            return template.render(filled_context)
        except KeyError as exc:
            # If template rendering fails, provide a basic prompt
            topic = context.get("topic", "an unspecified topic")
            return f"Work with '{topic}' using a {prompt_type.value} approach."
    
    def _fill_context_defaults(self, prompt_type: PromptType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fill missing context variables with reasonable defaults.
        
        Args:
            prompt_type: Type of prompt being generated
            context: Original context
            
        Returns:
            Context with defaults filled in
        """
        filled = context.copy()
        
        # Common defaults
        defaults = {
            "topic": "an unspecified topic",
            "focus_area": "key aspects",
            "target_audience": "stakeholders",
            "num_ideas": "5-10",
            "constraints": "available resources",
            "success_criteria": "desired outcomes"
        }
        
        # Type-specific defaults
        type_defaults = {
            PromptType.BRAINSTORMING: {
                "num_ideas": "10",
                "focus_area": "innovative solutions",
                "target_audience": "end users"
            },
            PromptType.ANALYSIS: {
                "focus_area": "critical factors"
            },
            PromptType.REFINEMENT: {
                "concept": "the current approach",
                "improvement_areas": "efficiency and effectiveness",
                "core_constraints": "existing requirements"
            },
            PromptType.SYNTHESIS: {
                "sources": "available information",
                "key_elements": "main concepts"
            },
            PromptType.EVALUATION: {
                "options": "available alternatives",
                "criteria": "relevant factors",
                "evaluation_factors": "costs, benefits, and risks"
            },
            PromptType.EXPLORATION: {
                "exploration_areas": "unexplored aspects",
                "discovery_goals": "new insights"
            },
            PromptType.PROBLEM_SOLVING: {
                "problem": "the challenge at hand",
                "resources": "available tools and capabilities"
            }
        }
        
        # Apply general defaults
        for key, value in defaults.items():
            if key not in filled:
                filled[key] = value
        
        # Apply type-specific defaults
        if prompt_type in type_defaults:
            for key, value in type_defaults[prompt_type].items():
                if key not in filled:
                    filled[key] = value
        
        return filled
