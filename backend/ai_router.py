"""
ai_router.py - Smart LLM Routing with Cost Optimization
Routes queries to best model based on complexity & cost
"""

from enum import Enum
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv('.env.production')

class TaskComplexity(Enum):
    """Query complexity levels"""
    FREE = "free"           # Simple queries
    CHEAP = "cheap"         # Regular queries
    SMART = "smart"         # Complex queries
    CRITICAL = "critical"   # Production critical

class ModelTier:
    """Model configuration per tier"""
    def __init__(self, name: str, provider: str, cost_per_1k: float, max_tokens: int):
        self.name = name
        self.provider = provider
        self.cost_per_1k = cost_per_1k
        self.max_tokens = max_tokens

# Tier definitions
TIER_CONFIG = {
    TaskComplexity.FREE: ModelTier(
        name="gemini-3-flash-preview",
        provider="google",
        cost_per_1k=0.001,
        max_tokens=1000
    ),
    TaskComplexity.CHEAP: ModelTier(
        name="gpt-4o-mini",
        provider="openai",
        cost_per_1k=0.05,
        max_tokens=4000
    ),
    TaskComplexity.SMART: ModelTier(
        name="claude-3-sonnet",
        provider="anthropic",
        cost_per_1k=0.15,
        max_tokens=8000
    ),
    TaskComplexity.CRITICAL: ModelTier(
        name="claude-3-opus",
        provider="anthropic",
        cost_per_1k=0.75,
        max_tokens=12000
    ),
}

class AIRouter:
    """Intelligent LLM routing with cost optimization"""
    
    def __init__(self):
        self.tier_config = TIER_CONFIG
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    def classify_query(self, query: str) -> TaskComplexity:
        """Classify query complexity"""
        # Simple keyword-based classification
        
        # Critical queries
        critical_keywords = ["production", "critical", "security", "analysis", "decision"]
        if any(kw in query.lower() for kw in critical_keywords):
            return TaskComplexity.CRITICAL
        
        # Smart queries
        smart_keywords = ["explain", "analyze", "complex", "strategy", "plan"]
        if any(kw in query.lower() for kw in smart_keywords):
            return TaskComplexity.SMART
        
        # Cheap queries
        cheap_keywords = ["summary", "list", "quick", "simple"]
        if any(kw in query.lower() for kw in cheap_keywords):
            return TaskComplexity.CHEAP
        
        # Default: free for simple queries
        return TaskComplexity.FREE
    
    def get_model_for_tier(self, tier: TaskComplexity) -> ModelTier:
        """Get model configuration for tier"""
        return self.tier_config[tier]
    
    def calculate_cost(self, tier: TaskComplexity, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """Calculate query cost"""
        model = self.get_model_for_tier(tier)
        
        input_cost = (input_tokens / 1000) * model.cost_per_1k
        output_cost = (output_tokens / 1000) * model.cost_per_1k
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "model": model.name,
            "tier": tier.value
        }
    
    def route_query(self, query: str, force_tier: Optional[str] = None) -> Dict[str, Any]:
        """Route query to appropriate model"""
        
        # Determine tier
        if force_tier and force_tier in [t.value for t in TaskComplexity]:
            tier = TaskComplexity(force_tier)
        else:
            tier = self.classify_query(query)
        
        model = self.get_model_for_tier(tier)
        
        return {
            "query": query,
            "tier": tier.value,
            "model": model.name,
            "provider": model.provider,
            "max_tokens": model.max_tokens,
            "cost_per_1k_tokens": model.cost_per_1k
        }
    
    async def route_and_respond(self, query: str, force_tier: Optional[str] = None) -> Dict[str, Any]:
        """Route query and get response (async version)"""
        route_info = self.route_query(query, force_tier)
        
        # For now, return route info
        # Tomorrow we'll integrate actual LLM calls
        return {
            **route_info,
            "status": "routed",
            "ready_for_llm_call": True
        }

# Global router instance
_router: Optional[AIRouter] = None

def get_router() -> AIRouter:
    """Get global router instance"""
    global _router
    if _router is None:
        _router = AIRouter()
    return _router

def init_router() -> AIRouter:
    """Initialize router"""
    global _router
    _router = AIRouter()
    return _router