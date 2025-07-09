"""Summarization module with multiple strategies for condensing and organizing ideas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
import re
from difflib import SequenceMatcher

if TYPE_CHECKING:
    from ..ai import AIModel


class OutputFormat(Enum):
    """Supported output formats for summaries."""
    BULLET_POINTS = "bullet_points"
    PARAGRAPH = "paragraph"
    NUMBERED_LIST = "numbered_list"
    HIERARCHICAL = "hierarchical"
    MIND_MAP = "mind_map"


@dataclass
class SummaryResult:
    """Result of a summarization operation."""
    content: str
    format: OutputFormat
    metadata: Dict[str, Any]
    themes: List[str]
    key_points: List[str]


class SummarizationStrategy(ABC):
    """Base class for summarization strategies."""
    
    @abstractmethod
    def summarize(self, ideas: List[str], max_length: Optional[int] = None) -> SummaryResult:
        """Summarize a list of ideas."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the summarization strategy."""
        pass


class ExtractiveStrategy(SummarizationStrategy):
    """Extract key sentences/ideas based on importance scoring."""
    
    def get_name(self) -> str:
        return "Extractive"
    
    def summarize(self, ideas: List[str], max_length: Optional[int] = None) -> SummaryResult:
        """Extract the most important ideas based on frequency and relevance."""
        if not ideas:
            return SummaryResult(
                content="No ideas to summarize.",
                format=OutputFormat.BULLET_POINTS,
                metadata={},
                themes=[],
                key_points=[]
            )
        
        # Score ideas based on word frequency and length
        word_freq = self._calculate_word_frequency(ideas)
        scored_ideas = []
        
        for idea in ideas:
            score = self._score_idea(idea, word_freq)
            scored_ideas.append((score, idea))
        
        # Sort by score and select top ideas
        scored_ideas.sort(reverse=True)
        
        if max_length:
            # Select ideas up to max_length
            selected = []
            current_length = 0
            for score, idea in scored_ideas:
                if current_length + len(idea) <= max_length:
                    selected.append(idea)
                    current_length += len(idea)
                else:
                    break
        else:
            # Select top 30% of ideas
            num_to_select = max(1, len(ideas) // 3)
            selected = [idea for _, idea in scored_ideas[:num_to_select]]
        
        # Extract themes
        themes = self._extract_themes(selected)
        
        return SummaryResult(
            content=self._format_as_bullets(selected),
            format=OutputFormat.BULLET_POINTS,
            metadata={"total_ideas": len(ideas), "selected_ideas": len(selected)},
            themes=themes,
            key_points=selected[:5]  # Top 5 as key points
        )
    
    def _calculate_word_frequency(self, ideas: List[str]) -> Counter:
        """Calculate word frequency across all ideas."""
        words = []
        for idea in ideas:
            # Simple tokenization
            tokens = re.findall(r'\b\w+\b', idea.lower())
            # Filter out common words
            filtered = [w for w in tokens if len(w) > 3 and w not in self._get_stopwords()]
            words.extend(filtered)
        return Counter(words)
    
    def _score_idea(self, idea: str, word_freq: Counter) -> float:
        """Score an idea based on word importance."""
        tokens = re.findall(r'\b\w+\b', idea.lower())
        filtered = [w for w in tokens if len(w) > 3 and w not in self._get_stopwords()]
        
        if not filtered:
            return 0.0
        
        # Average word frequency score
        total_score = sum(word_freq.get(word, 0) for word in filtered)
        return total_score / len(filtered)
    
    def _extract_themes(self, ideas: List[str]) -> List[str]:
        """Extract common themes from ideas."""
        word_freq = self._calculate_word_frequency(ideas)
        # Top 5 most common meaningful words as themes
        themes = [word for word, _ in word_freq.most_common(5)]
        return themes
    
    def _format_as_bullets(self, ideas: List[str]) -> str:
        """Format ideas as bullet points."""
        return "\n".join(f"• {idea}" for idea in ideas)
    
    def _get_stopwords(self) -> Set[str]:
        """Get common stopwords to filter out."""
        return {
            'the', 'and', 'for', 'with', 'this', 'that', 'from', 
            'have', 'will', 'can', 'are', 'was', 'were', 'been',
            'about', 'into', 'through', 'during', 'before', 'after'
        }


class AbstractiveStrategy(SummarizationStrategy):
    """Generate new summary text using AI."""
    
    def __init__(self, ai_model: Optional["AIModel"] = None):
        self._ai = ai_model
    
    def get_name(self) -> str:
        return "Abstractive"
    
    def summarize(self, ideas: List[str], max_length: Optional[int] = None) -> SummaryResult:
        """Use AI to generate an abstract summary."""
        if not ideas:
            return SummaryResult(
                content="No ideas to summarize.",
                format=OutputFormat.PARAGRAPH,
                metadata={},
                themes=[],
                key_points=[]
            )
        
        # Prepare context for AI
        ideas_text = "\n".join(f"- {idea}" for idea in ideas[:20])  # Limit to prevent token overflow
        
        if self._ai:
            prompt = f"""Summarize these ideas into a concise, coherent summary that captures the main themes and insights:

{ideas_text}

Provide a summary that:
1. Identifies key themes
2. Highlights the most important points
3. Shows connections between ideas
4. Is no more than {max_length or 200} words"""
            
            try:
                summary = self._ai.query(prompt, max_tokens=max_length or 200)
            except Exception:
                # Fallback to extractive
                summary = self._fallback_summary(ideas)
        else:
            summary = self._fallback_summary(ideas)
        
        # Extract themes from original ideas
        themes = self._extract_themes(ideas)
        key_points = ideas[:5] if len(ideas) >= 5 else ideas
        
        return SummaryResult(
            content=summary,
            format=OutputFormat.PARAGRAPH,
            metadata={"total_ideas": len(ideas), "method": "ai" if self._ai else "fallback"},
            themes=themes,
            key_points=key_points
        )
    
    def _fallback_summary(self, ideas: List[str]) -> str:
        """Create a simple summary when AI is not available."""
        if len(ideas) == 1:
            return ideas[0]
        elif len(ideas) <= 3:
            return " Additionally, ".join(ideas)
        else:
            return f"Key insights include: {ideas[0]} Among {len(ideas)} ideas, common themes emerge around {ideas[1]} Further exploration reveals {ideas[2]}"
    
    def _extract_themes(self, ideas: List[str]) -> List[str]:
        """Extract themes using word frequency."""
        extractor = ExtractiveStrategy()
        return extractor._extract_themes(ideas)


class HierarchicalStrategy(SummarizationStrategy):
    """Organize ideas into a hierarchical structure."""
    
    def get_name(self) -> str:
        return "Hierarchical"
    
    def summarize(self, ideas: List[str], max_length: Optional[int] = None) -> SummaryResult:
        """Create a hierarchical summary with main topics and sub-points."""
        if not ideas:
            return SummaryResult(
                content="No ideas to summarize.",
                format=OutputFormat.HIERARCHICAL,
                metadata={},
                themes=[],
                key_points=[]
            )
        
        # Cluster ideas by similarity
        clusters = self._cluster_ideas(ideas)
        
        # Build hierarchical structure
        hierarchy = []
        themes = []
        key_points = []
        
        for theme, cluster_ideas in clusters.items():
            themes.append(theme)
            if cluster_ideas:
                key_points.append(cluster_ideas[0])  # First idea as key point
                
            # Add to hierarchy
            hierarchy.append(f"## {theme.title()}")
            for idea in cluster_ideas[:5]:  # Limit sub-points
                hierarchy.append(f"   - {idea}")
        
        content = "\n".join(hierarchy)
        
        # Trim if needed
        if max_length and len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return SummaryResult(
            content=content,
            format=OutputFormat.HIERARCHICAL,
            metadata={"clusters": len(clusters), "total_ideas": len(ideas)},
            themes=themes[:5],
            key_points=key_points[:5]
        )
    
    def _cluster_ideas(self, ideas: List[str]) -> Dict[str, List[str]]:
        """Cluster ideas by theme/similarity."""
        clusters = defaultdict(list)
        
        # Simple clustering by common keywords
        for idea in ideas:
            theme = self._extract_main_theme(idea)
            clusters[theme].append(idea)
        
        # If too many clusters, merge similar ones
        if len(clusters) > 5:
            clusters = self._merge_similar_clusters(clusters)
        
        return dict(clusters)
    
    def _extract_main_theme(self, idea: str) -> str:
        """Extract the main theme from an idea."""
        # Find the most significant noun/phrase
        words = re.findall(r'\b\w+\b', idea.lower())
        # Filter out common words
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'about'}
        significant = [w for w in words if len(w) > 4 and w not in stopwords]
        
        if significant:
            return significant[0]
        elif words:
            return words[0]
        else:
            return "general"
    
    def _merge_similar_clusters(self, clusters: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Merge similar clusters to reduce total number."""
        # Simple merging - combine smallest clusters
        sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
        
        merged = {}
        for i, (theme, ideas) in enumerate(sorted_clusters):
            if i < 5:  # Keep top 5
                merged[theme] = ideas
            else:
                # Merge into "other"
                if "other" not in merged:
                    merged["other"] = []
                merged["other"].extend(ideas)
        
        return merged


class ThemeBasedStrategy(SummarizationStrategy):
    """Organize summary by identified themes."""
    
    def get_name(self) -> str:
        return "Theme-Based"
    
    def summarize(self, ideas: List[str], max_length: Optional[int] = None) -> SummaryResult:
        """Create a theme-based summary."""
        if not ideas:
            return SummaryResult(
                content="No ideas to summarize.",
                format=OutputFormat.NUMBERED_LIST,
                metadata={},
                themes=[],
                key_points=[]
            )
        
        # Identify themes
        theme_map = self._identify_themes(ideas)
        themes = list(theme_map.keys())
        
        # Build summary
        summary_parts = []
        key_points = []
        
        for i, (theme, theme_ideas) in enumerate(theme_map.items(), 1):
            summary_parts.append(f"{i}. Theme: {theme.title()}")
            
            # Select top ideas for this theme
            top_ideas = theme_ideas[:3]
            key_points.extend(top_ideas[:1])  # First idea from each theme
            
            for idea in top_ideas:
                summary_parts.append(f"   • {idea}")
        
        content = "\n".join(summary_parts)
        
        # Trim if needed
        if max_length and len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return SummaryResult(
            content=content,
            format=OutputFormat.NUMBERED_LIST,
            metadata={"themes_found": len(themes), "total_ideas": len(ideas)},
            themes=themes[:5],
            key_points=key_points[:5]
        )
    
    def _identify_themes(self, ideas: List[str]) -> Dict[str, List[str]]:
        """Identify and group ideas by theme."""
        # Use keyword extraction for theme identification
        keyword_ideas = defaultdict(list)
        
        for idea in ideas:
            keywords = self._extract_keywords(idea)
            for keyword in keywords:
                keyword_ideas[keyword].append(idea)
        
        # Select top themes by idea count
        sorted_themes = sorted(keyword_ideas.items(), key=lambda x: len(x[1]), reverse=True)
        
        # Return top 5 themes
        theme_map = {}
        for theme, theme_ideas in sorted_themes[:5]:
            theme_map[theme] = theme_ideas
        
        return theme_map
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter for significant words
        keywords = [w for w in words if len(w) > 5 and w not in self._get_stopwords()]
        return keywords[:2]  # Top 2 keywords per idea
    
    def _get_stopwords(self) -> Set[str]:
        """Get stopwords set."""
        return {
            'the', 'and', 'for', 'with', 'this', 'that', 'from', 
            'have', 'will', 'can', 'are', 'was', 'were', 'been',
            'about', 'into', 'through', 'during', 'before', 'after',
            'should', 'could', 'would', 'might', 'must', 'shall'
        }


class IdeaDeduplicator:
    """Remove duplicate and highly similar ideas."""
    
    def deduplicate(self, ideas: List[str], similarity_threshold: float = 0.8) -> List[str]:
        """Remove duplicate ideas based on similarity threshold."""
        if len(ideas) <= 1:
            return ideas
        
        unique_ideas = []
        
        for idea in ideas:
            is_duplicate = False
            
            for unique_idea in unique_ideas:
                similarity = self._calculate_similarity(idea, unique_idea)
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_ideas.append(idea)
        
        return unique_ideas
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


class OutputFormatter:
    """Format summaries in different output styles."""
    
    def format(self, summary: SummaryResult, format_type: Optional[OutputFormat] = None) -> str:
        """Format a summary result in the specified format."""
        target_format = format_type or summary.format
        
        if target_format == OutputFormat.BULLET_POINTS:
            return self._format_bullets(summary)
        elif target_format == OutputFormat.PARAGRAPH:
            return self._format_paragraph(summary)
        elif target_format == OutputFormat.NUMBERED_LIST:
            return self._format_numbered(summary)
        elif target_format == OutputFormat.HIERARCHICAL:
            return self._format_hierarchical(summary)
        elif target_format == OutputFormat.MIND_MAP:
            return self._format_mindmap(summary)
        else:
            return summary.content
    
    def _format_bullets(self, summary: SummaryResult) -> str:
        """Format as bullet points."""
        if summary.format == OutputFormat.BULLET_POINTS:
            return summary.content
        
        # Convert from other formats
        lines = summary.content.split('\n')
        formatted = []
        for line in lines:
            if line.strip():
                if not line.startswith('•'):
                    formatted.append(f"• {line.strip()}")
                else:
                    formatted.append(line)
        return '\n'.join(formatted)
    
    def _format_paragraph(self, summary: SummaryResult) -> str:
        """Format as paragraph."""
        if summary.format == OutputFormat.PARAGRAPH:
            return summary.content
        
        # Convert from other formats
        lines = summary.content.split('\n')
        # Remove bullets and numbering
        cleaned = []
        for line in lines:
            text = re.sub(r'^[•\-\d\.]+\s*', '', line).strip()
            if text:
                cleaned.append(text)
        
        return ' '.join(cleaned)
    
    def _format_numbered(self, summary: SummaryResult) -> str:
        """Format as numbered list."""
        if summary.format == OutputFormat.NUMBERED_LIST:
            return summary.content
        
        lines = summary.content.split('\n')
        formatted = []
        counter = 1
        
        for line in lines:
            if line.strip() and not line.startswith(' '):
                formatted.append(f"{counter}. {line.strip()}")
                counter += 1
            elif line.strip():
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    def _format_hierarchical(self, summary: SummaryResult) -> str:
        """Format as hierarchical structure."""
        if summary.format == OutputFormat.HIERARCHICAL:
            return summary.content
        
        # Create hierarchy from themes and key points
        output = []
        for theme in summary.themes:
            output.append(f"## {theme.title()}")
            # Find related points
            for point in summary.key_points:
                if theme.lower() in point.lower():
                    output.append(f"   - {point}")
        
        return '\n'.join(output)
    
    def _format_mindmap(self, summary: SummaryResult) -> str:
        """Format as text-based mind map."""
        output = ["[Central Topic]"]
        
        for i, theme in enumerate(summary.themes):
            output.append(f"├─ {theme.title()}")
            
            # Add related key points
            related_points = [p for p in summary.key_points if theme.lower() in p.lower()]
            for j, point in enumerate(related_points[:2]):
                if j == len(related_points) - 1:
                    output.append(f"│  └─ {point[:50]}...")
                else:
                    output.append(f"│  ├─ {point[:50]}...")
        
        return '\n'.join(output)


class Summarizer:
    """Main summarizer class that orchestrates different strategies."""
    
    def __init__(self, ai_model: Optional["AIModel"] = None):
        self.strategies = {
            "extractive": ExtractiveStrategy(),
            "abstractive": AbstractiveStrategy(ai_model),
            "hierarchical": HierarchicalStrategy(),
            "theme_based": ThemeBasedStrategy()
        }
        self.deduplicator = IdeaDeduplicator()
        self.formatter = OutputFormatter()
        self._ai = ai_model
    
    def summarize(self, payload: Dict[str, Any]) -> str:
        """Summarize ideas using the specified strategy."""
        ideas = payload.get("ideas", [])
        strategy_name = payload.get("strategy", "extractive")
        max_length = payload.get("max_length")
        output_format = payload.get("output_format")
        deduplicate = payload.get("deduplicate", True)
        
        # Handle string ideas or idea objects
        if ideas and isinstance(ideas[0], dict):
            ideas = [idea.get("content", str(idea)) for idea in ideas]
        
        # Deduplicate if requested
        if deduplicate:
            ideas = self.deduplicator.deduplicate(ideas)
        
        # Select strategy
        strategy = self.strategies.get(strategy_name, self.strategies["extractive"])
        
        # Generate summary
        result = strategy.summarize(ideas, max_length)
        
        # Format output if requested
        if output_format:
            try:
                format_enum = OutputFormat(output_format)
                return self.formatter.format(result, format_enum)
            except ValueError:
                pass
        
        return result.content
    
    def summarize_with_metadata(self, payload: Dict[str, Any]) -> SummaryResult:
        """Summarize and return full result with metadata."""
        ideas = payload.get("ideas", [])
        strategy_name = payload.get("strategy", "extractive")
        max_length = payload.get("max_length")
        deduplicate = payload.get("deduplicate", True)
        
        # Handle string ideas or idea objects
        if ideas and isinstance(ideas[0], dict):
            ideas = [idea.get("content", str(idea)) for idea in ideas]
        
        # Deduplicate if requested
        if deduplicate:
            ideas = self.deduplicator.deduplicate(ideas)
        
        # Select strategy
        strategy = self.strategies.get(strategy_name, self.strategies["extractive"])
        
        # Generate summary
        return strategy.summarize(ideas, max_length)
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available summarization strategies."""
        return list(self.strategies.keys())
    
    def get_available_formats(self) -> List[str]:
        """Get list of available output formats."""
        return [fmt.value for fmt in OutputFormat]