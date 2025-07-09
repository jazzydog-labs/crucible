#!/usr/bin/env python
"""Test script to demonstrate AI limit enforcement."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from crucible.ai import AIModel
from crucible.ai_observability import get_observer, CostLimitExceeded, demo_ai_budget_info

def test_token_limit():
    """Test the token limit enforcement."""
    print("🧪 Testing AI Token Limit Enforcement")
    print("="*50)
    
    # Show initial budget
    demo_ai_budget_info()
    
    model = AIModel()
    
    # Make several requests to approach the limit
    prompts = [
        "Write a short explanation of microservices architecture.",
        "Explain the benefits of cloud computing in detail.",
        "Describe the principles of DevOps practices.",
        "What are the advantages of containerization with Docker?",
        "How does Kubernetes help with container orchestration?",
        "Explain the importance of monitoring and observability.",
        "What are the best practices for API design?",
        "Describe event-driven architecture patterns."
    ]
    
    print(f"\n📝 Making requests until limit is reached...")
    
    for i, prompt in enumerate(prompts, 1):
        try:
            print(f"\n{i}. Requesting: {prompt[:50]}...")
            result = model.query(prompt, max_tokens=150)
            print(f"   ✅ Success: {len(result)} chars")
            
            # Check remaining budget
            observer = get_observer()
            session = observer.get_session_summary()
            remaining = session['tokens_remaining']
            print(f"   💰 Tokens remaining: {remaining}")
            
            if remaining < 100:
                print(f"   ⚠️  Budget getting low!")
                
        except CostLimitExceeded as e:
            print(f"   ❌ BLOCKED: {e}")
            break
        except Exception as e:
            print(f"   💥 Error: {e}")
            break
    
    # Show final summary
    print(f"\n📊 Final Summary:")
    from crucible.ai_observability import print_ai_summary
    print_ai_summary()

if __name__ == "__main__":
    test_token_limit()