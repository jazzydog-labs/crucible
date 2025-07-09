"""AI observability and cost control system for repository-wide AI usage tracking."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from functools import wraps


@dataclass
class AIUsage:
    """Record of AI usage for observability."""
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    caller: str
    purpose: str
    success: bool
    error: Optional[str] = None


class CostLimitExceeded(Exception):
    """Raised when AI usage exceeds configured limits."""
    pass


class AIObserver:
    """Global AI usage observer and cost controller."""
    
    # Repository-wide policies
    MAX_TOKENS_PER_DEMO = 1000
    ALLOWED_MODELS = ["gpt-4o-mini"]  # Only nano model allowed
    USAGE_LOG_FILE = ".ai_usage.json"
    
    def __init__(self):
        self._usage_history: List[AIUsage] = []
        self._session_tokens = 0
        self._session_cost = 0.0
        self._load_usage_history()
    
    def _load_usage_history(self) -> None:
        """Load usage history from file."""
        try:
            if Path(self.USAGE_LOG_FILE).exists():
                with open(self.USAGE_LOG_FILE, 'r') as f:
                    data = json.load(f)
                    self._usage_history = [AIUsage(**item) for item in data]
        except Exception:
            # If we can't load history, start fresh
            self._usage_history = []
    
    def _save_usage_history(self) -> None:
        """Save usage history to file."""
        try:
            with open(self.USAGE_LOG_FILE, 'w') as f:
                json.dump([asdict(usage) for usage in self._usage_history], f, indent=2)
        except Exception:
            # Fail silently to not break demos
            pass
    
    def pre_request_check(self, model: str, estimated_tokens: int, caller: str) -> None:
        """Check if request should be allowed based on policies."""
        
        # Check model policy
        if model not in self.ALLOWED_MODELS:
            raise CostLimitExceeded(
                f"Model '{model}' not allowed. Only {self.ALLOWED_MODELS} permitted."
            )
        
        # Check demo token limit
        if self._session_tokens + estimated_tokens > self.MAX_TOKENS_PER_DEMO:
            raise CostLimitExceeded(
                f"Request would exceed demo limit of {self.MAX_TOKENS_PER_DEMO} tokens. "
                f"Current session: {self._session_tokens}, requested: {estimated_tokens}"
            )
    
    def record_usage(self, 
                    model: str, 
                    prompt_tokens: int, 
                    completion_tokens: int, 
                    estimated_cost: float,
                    caller: str,
                    purpose: str,
                    success: bool = True,
                    error: Optional[str] = None) -> None:
        """Record AI usage for observability."""
        
        usage = AIUsage(
            timestamp=datetime.now().isoformat(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=estimated_cost,
            caller=caller,
            purpose=purpose,
            success=success,
            error=error
        )
        
        self._usage_history.append(usage)
        self._session_tokens += usage.total_tokens
        self._session_cost += estimated_cost
        
        # Save to file
        self._save_usage_history()
        
        # Print real-time cost info
        print(f"💰 AI Usage: {usage.total_tokens} tokens, ${estimated_cost:.6f} | Session: {self._session_tokens}/{self.MAX_TOKENS_PER_DEMO} tokens")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session usage summary."""
        return {
            "session_tokens": self._session_tokens,
            "session_cost": self._session_cost,
            "max_tokens": self.MAX_TOKENS_PER_DEMO,
            "tokens_remaining": self.MAX_TOKENS_PER_DEMO - self._session_tokens,
            "requests_made": len([u for u in self._usage_history if u.timestamp.startswith(datetime.now().strftime("%Y-%m-%d"))])
        }
    
    def get_total_usage(self) -> Dict[str, Any]:
        """Get total usage across all time."""
        if not self._usage_history:
            return {"total_tokens": 0, "total_cost": 0.0, "total_requests": 0}
        
        return {
            "total_tokens": sum(u.total_tokens for u in self._usage_history),
            "total_cost": sum(u.estimated_cost for u in self._usage_history),
            "total_requests": len(self._usage_history),
            "successful_requests": len([u for u in self._usage_history if u.success])
        }
    
    def reset_session(self) -> None:
        """Reset session counters (useful for new demos)."""
        self._session_tokens = 0
        self._session_cost = 0.0


# Global observer instance
_global_observer = AIObserver()


def get_observer() -> AIObserver:
    """Get the global AI observer instance."""
    return _global_observer


def ai_observability(purpose: str = "general"):
    """Decorator to add observability to AI function calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            observer = get_observer()
            caller = f"{func.__module__}.{func.__qualname__}"
            
            # Try to extract model and estimate tokens
            model = "unknown"
            estimated_tokens = 100  # Default estimate
            
            # Look for AI model in args
            for arg in args:
                if hasattr(arg, 'model'):
                    model = arg.model
                    break
            
            # Look for prompt to estimate tokens
            for arg in list(args) + list(kwargs.values()):
                if isinstance(arg, str) and len(arg) > 10:
                    # Rough estimate: 1 token per 4 characters
                    estimated_tokens = max(estimated_tokens, len(arg) // 4)
                    break
            
            # Pre-request check
            try:
                observer.pre_request_check(model, estimated_tokens, caller)
            except CostLimitExceeded as e:
                print(f"❌ AI Request Blocked: {e}")
                raise
            
            # Execute function
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # Record successful usage
                # Note: This is a simplified version - real usage would be extracted from the AI response
                observer.record_usage(
                    model=model,
                    prompt_tokens=estimated_tokens,
                    completion_tokens=50,  # Estimate
                    estimated_cost=estimated_tokens * 0.15 / 1_000_000 + 50 * 0.60 / 1_000_000,
                    caller=caller,
                    purpose=purpose,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Record failed usage
                observer.record_usage(
                    model=model,
                    prompt_tokens=estimated_tokens,
                    completion_tokens=0,
                    estimated_cost=0.0,
                    caller=caller,
                    purpose=purpose,
                    success=False,
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator


def enforce_ai_policies(ai_model_class):
    """Class decorator to enforce AI policies on all methods."""
    
    # Wrap the query method specifically
    if hasattr(ai_model_class, 'query'):
        original_query = ai_model_class.query
        
        @ai_observability(purpose="ai_query")
        def wrapped_query(self, prompt: str, max_tokens: int = 200):
            observer = get_observer()
            
            # Enforce repo-wide token limit
            if max_tokens > observer.MAX_TOKENS_PER_DEMO:
                max_tokens = observer.MAX_TOKENS_PER_DEMO
                print(f"⚠️  Token limit reduced to {max_tokens} (repo policy)")
            
            # Enforce model policy
            if self.model not in observer.ALLOWED_MODELS:
                raise CostLimitExceeded(f"Model {self.model} not allowed by repo policy")
            
            return original_query(self, prompt, max_tokens)
        
        ai_model_class.query = wrapped_query
    
    return ai_model_class


def print_ai_summary():
    """Print AI usage summary for the session."""
    observer = get_observer()
    session = observer.get_session_summary()
    total = observer.get_total_usage()
    
    print(f"\n🔍 AI Usage Summary:")
    print(f"   Session: {session['session_tokens']}/{session['max_tokens']} tokens (${session['session_cost']:.6f})")
    print(f"   Total: {total['total_tokens']} tokens, ${total['total_cost']:.6f}, {total['total_requests']} requests")
    
    if session['tokens_remaining'] < 100:
        print(f"   ⚠️  Warning: Only {session['tokens_remaining']} tokens remaining in demo budget")


def demo_ai_budget_info():
    """Show AI budget information for demos."""
    observer = get_observer()
    session = observer.get_session_summary()
    
    print(f"🎯 AI Demo Budget: {session['tokens_remaining']}/{observer.MAX_TOKENS_PER_DEMO} tokens remaining")
    print(f"   Allowed models: {observer.ALLOWED_MODELS}")
    print(f"   Current session cost: ${session['session_cost']:.6f}")