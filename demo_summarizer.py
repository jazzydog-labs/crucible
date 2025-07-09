#!/usr/bin/env python
"""Demo script showing all summarization features."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from crucible.summarizer import Summarizer, OutputFormat
from crucible.ai import AIModel


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)


def demo_extractive_summarization():
    """Demo extractive summarization."""
    print_section("1. EXTRACTIVE SUMMARIZATION")
    
    ideas = [
        "Microservices architecture enables better scalability and maintainability",
        "Cloud computing provides flexible infrastructure for modern applications",
        "DevOps practices improve deployment speed and reliability",
        "Container orchestration with Kubernetes simplifies management",
        "Monitoring and observability are crucial for system health",
        "API gateways provide centralized request handling",
        "Service mesh enables advanced traffic management",
        "Event-driven architecture improves system decoupling"
    ]
    
    summarizer = Summarizer()
    
    # Basic extractive summary
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "extractive"
    })
    
    print("Input: 8 ideas about modern architecture")
    print("\nExtracted key ideas:")
    print(result)
    
    # With max length constraint
    print("\n--- With max length (150 chars) ---")
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "extractive",
        "max_length": 150
    })
    print(result)


def demo_abstractive_summarization():
    """Demo AI-powered abstractive summarization."""
    print_section("2. ABSTRACTIVE SUMMARIZATION (AI)")
    
    ideas = [
        "Machine learning models need continuous monitoring",
        "Data quality directly impacts model performance",
        "Feature engineering is crucial for model accuracy",
        "Cross-validation helps prevent overfitting"
    ]
    
    # With AI
    ai_model = AIModel()
    summarizer_ai = Summarizer(ai_model=ai_model)
    
    print("With AI model:")
    result = summarizer_ai.summarize({
        "ideas": ideas,
        "strategy": "abstractive"
    })
    print(result)
    
    # Without AI (fallback)
    summarizer_no_ai = Summarizer(ai_model=None)
    print("\nWithout AI (fallback mode):")
    result = summarizer_no_ai.summarize({
        "ideas": ideas,
        "strategy": "abstractive"
    })
    print(result)


def demo_hierarchical_summarization():
    """Demo hierarchical organization."""
    print_section("3. HIERARCHICAL SUMMARIZATION")
    
    ideas = [
        "Authentication should use JWT tokens",
        "Database queries need optimization",
        "Authentication requires secure password hashing",
        "Database indexing improves query performance",
        "Authorization rules must be clearly defined",
        "Database connection pooling reduces overhead",
        "Security headers prevent common attacks",
        "Caching strategy reduces database load"
    ]
    
    summarizer = Summarizer()
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "hierarchical"
    })
    
    print("Ideas grouped by theme:")
    print(result)


def demo_theme_based_summarization():
    """Demo theme-based clustering."""
    print_section("4. THEME-BASED SUMMARIZATION")
    
    ideas = [
        "Performance optimization requires profiling",
        "Security vulnerabilities need regular scanning",
        "Performance monitoring helps identify bottlenecks",
        "Security patches must be applied promptly",
        "Scalability planning prevents future issues",
        "Performance testing validates improvements"
    ]
    
    summarizer = Summarizer()
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "theme_based"
    })
    
    print("Ideas organized by identified themes:")
    print(result)


def demo_deduplication():
    """Demo idea deduplication."""
    print_section("5. IDEA DEDUPLICATION")
    
    ideas = [
        "Use microservices for scalability",
        "Use microservices for scalability",  # Exact duplicate
        "Implement caching for performance",
        "Add caching to improve performance",  # Similar idea
        "Monitor system health continuously",
        "Continuous monitoring is essential"   # Similar idea
    ]
    
    summarizer = Summarizer()
    
    print("With deduplication (default):")
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "extractive",
        "deduplicate": True
    })
    print(result)
    
    print("\nWithout deduplication:")
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "extractive",
        "deduplicate": False
    })
    print(result)


def demo_output_formats():
    """Demo different output formats."""
    print_section("6. OUTPUT FORMATS")
    
    ideas = [
        "Implement automated testing",
        "Use continuous integration",
        "Deploy with blue-green strategy",
        "Monitor production metrics"
    ]
    
    summarizer = Summarizer()
    base_payload = {
        "ideas": ideas,
        "strategy": "extractive"
    }
    
    formats = ["bullet_points", "paragraph", "numbered_list", "hierarchical", "mind_map"]
    
    for fmt in formats:
        print(f"\n--- Format: {fmt} ---")
        result = summarizer.summarize({
            **base_payload,
            "output_format": fmt
        })
        print(result)


def demo_metadata_extraction():
    """Demo metadata and insights extraction."""
    print_section("7. METADATA & INSIGHTS")
    
    ideas = [
        "React components should be reusable",
        "State management needs Redux or Context",
        "Testing ensures component reliability",
        "Performance optimization with React.memo",
        "Accessibility is crucial for all users"
    ]
    
    summarizer = Summarizer()
    result = summarizer.summarize_with_metadata({
        "ideas": ideas,
        "strategy": "theme_based"
    })
    
    print(f"Summary Content:\n{result.content}")
    print(f"\nExtracted Themes: {result.themes}")
    print(f"Key Points: {result.key_points[:3]}")
    print(f"Metadata: {result.metadata}")


def demo_combined_features():
    """Demo combining multiple features."""
    print_section("8. COMBINED FEATURES")
    
    ideas = [
        "GraphQL provides flexible API queries",
        "REST APIs are simpler to implement",
        "GraphQL reduces over-fetching",
        "REST APIs have better caching",
        "GraphQL enables real-time subscriptions",
        "REST follows HTTP standards closely",
        "GraphQL requires schema definition",
        "REST APIs are more widely supported"
    ]
    
    summarizer = Summarizer()
    
    print("Hierarchical summary with mind map format and max length:")
    result = summarizer.summarize({
        "ideas": ideas,
        "strategy": "hierarchical",
        "output_format": "mind_map",
        "max_length": 300,
        "deduplicate": True
    })
    print(result)


def main():
    """Run all demos."""
    print("\n🎯 CRUCIBLE SUMMARIZATION SYSTEM DEMO")
    print("=====================================")
    
    demos = [
        demo_extractive_summarization,
        demo_hierarchical_summarization,
        demo_theme_based_summarization,
        demo_deduplication,
        demo_output_formats,
        demo_metadata_extraction,
        demo_combined_features
    ]
    
    # Run demos that don't require AI
    for demo in demos:
        if demo != demo_abstractive_summarization:
            try:
                demo()
            except Exception as e:
                print(f"\nError in {demo.__name__}: {e}")
    
    # Run AI demo separately (optional)
    try:
        print("\n" + "="*60)
        print("Note: Skipping AI demo to avoid API costs.")
        print("Uncomment the line below to run AI summarization demo.")
        # demo_abstractive_summarization()
    except Exception as e:
        print(f"\nError in AI demo: {e}")
    
    print("\n\n✅ Demo complete!")
    print("\nAvailable strategies:", Summarizer().get_available_strategies())
    print("Available formats:", Summarizer().get_available_formats())


if __name__ == "__main__":
    main()