"""
llm_client.py - Multi-LLM Client with unified interface
Supports: Claude (Anthropic), GPT (OpenAI), Gemini (Google)
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv('.env.production')

class LLMClient:
    """Unified client for multiple LLM providers"""
    
    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY", "mock-key")
        self.google_key = os.getenv("GOOGLE_API_KEY", "mock-key")
    
    async def call_claude(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Call Claude API (Anthropic)"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.anthropic_key)
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            
            return {
                "success": True,
                "model": "claude-3-sonnet",
                "response": response_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }
        except Exception as e:
            return {
                "success": False,
                "model": "claude-3-sonnet",
                "error": str(e),
                "response": f"[Error with Claude]: {str(e)}"
            }
    
    async def call_gpt(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Call GPT API (OpenAI) - Mock for now"""
        # For Day 3, we'll use mock response
        # Real integration comes later
        return {
            "success": True,
            "model": "gpt-4o-mini",
            "response": f"[GPT] Response to: {prompt[:50]}...",
            "input_tokens": len(prompt.split()),
            "output_tokens": 50,
            "total_tokens": len(prompt.split()) + 50
        }
    
    async def call_gemini(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Call Gemini API (Google) - Mock for now"""
        return {
            "success": True,
            "model": "gemini-3-flash-preview",
            "response": f"[Gemini] Response to: {prompt[:50]}...",
            "input_tokens": len(prompt.split()),
            "output_tokens": 30,
            "total_tokens": len(prompt.split()) + 30
        }
    
    async def call(self, provider: str, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Route to appropriate provider"""
        
        if provider == "anthropic":
            return await self.call_claude(prompt, max_tokens)
        elif provider == "openai":
            return await self.call_gpt(prompt, max_tokens)
        elif provider == "google":
            return await self.call_gemini(prompt, max_tokens)
        else:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}",
                "response": f"Unknown provider: {provider}"
            }

# Global instance
_client: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    """Get global LLM client"""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client

def init_llm_client() -> LLMClient:
    """Initialize LLM client"""
    global _client
    _client = LLMClient()
    return _client