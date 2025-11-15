"""LLM client implementations for SIRA."""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
from src.core.logging import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Generate text from the LLM."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM service is available."""
        pass


class LocalRuntimeClient(LLMClient):
    """Client for local LLM runtime (Ollama)."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.llm_base_url
        self.model = self.settings.llm_model_general
        self.timeout = 120.0  # 2 minutes for long generations
        
    async def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop_sequences: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Generate text using Ollama API.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate (Ollama: num_predict)
            temperature: Sampling temperature (0.0-1.0)
            stop_sequences: Sequences that stop generation
            
        Returns:
            Dict with 'response', 'metadata', and 'usage' keys
        """
        logger.info("llm_generate_request", model=self.model, prompt_length=len(prompt))
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {}
        }
        
        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        if stop_sequences:
            payload["options"]["stop"] = stop_sequences
            
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
            result = {
                "response": data.get("response", ""),
                "metadata": {
                    "model": data.get("model"),
                    "done": data.get("done", False),
                    "done_reason": data.get("done_reason"),
                    "total_duration": data.get("total_duration", 0),
                    "load_duration": data.get("load_duration", 0),
                    "prompt_eval_duration": data.get("prompt_eval_duration", 0),
                    "eval_duration": data.get("eval_duration", 0)
                },
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                }
            }
            
            logger.info(
                "llm_generate_success",
                response_length=len(result["response"]),
                prompt_tokens=result["usage"]["prompt_tokens"],
                completion_tokens=result["usage"]["completion_tokens"],
                duration_ms=result["metadata"]["total_duration"] / 1_000_000
            )
            
            return result
            
        except httpx.HTTPError as e:
            logger.error("llm_generate_http_error", error=str(e), url=self.base_url)
            raise
        except Exception as e:
            logger.error("llm_generate_error", error=str(e), error_type=type(e).__name__)
            raise
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                
                # Check if our model is available
                models = data.get("models", [])
                model_available = any(
                    m.get("name") == self.model for m in models
                )
                
                if not model_available:
                    logger.warning("llm_model_not_found", model=self.model)
                    return False
                    
                logger.info("llm_health_check_success", model=self.model)
                return True
                
        except Exception as e:
            logger.error("llm_health_check_failed", error=str(e))
            return False


def get_llm_client() -> LLMClient:
    """Factory function to get LLM client instance."""
    return LocalRuntimeClient()
