"""
AI client for contract generation using OpenAI and Anthropic APIs.
"""
from typing import AsyncGenerator, Dict, Any, Optional
import asyncio
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import AsyncOpenAI, RateLimitError, APIError

from .config import settings
from .models import BusinessContext
from .prompt import basePrompt


class AIClientError(Exception):
    """Custom exception for AI client errors."""
    pass


class AIClient:
    """AI client for contract generation."""
    
    def __init__(self):
        """Initialize AI clients."""
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.ai_base_url)
        self.model = settings.default_model or "google/gemini-2.5-flash-lite"
    async def generate_contract_stream(
        self,
        business_context: BusinessContext,
    ) -> AsyncGenerator[str, None]:
        """
        Generate contract content as a streaming response.
        
        Args:
            business_context: Business context for contract generation
            abort_signal: To stop streaming when cancelled
            
        Yields:
            Generated contract content chunks
        """
        try:
            # Build the prompt for contract generation
            prompt = basePrompt(business_context.description)
            
            # Generate contract using OpenAI (streaming)
            async for chunk in self._generate_openai_stream(prompt):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in contract generation: {str(e)}")
            raise AIClientError(f"Contract generation failed: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _generate_openai_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate content using OpenAI API with streaming and retry logic.
        
        Args:
            prompt: The prompt to send to OpenAI
            
        Yields:
            Generated content chunks
        """
        try:
            stream = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a transactional attorney with over 15+ years of experience, specializing in drafting precise, enforceable legal documents. You have extensive experience in contract law, regulatory compliance, and risk allocation strategies across multiple industries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3, # Should be configurable
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded, retrying...")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise AIClientError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI generation: {str(e)}")
            raise AIClientError(f"Unexpected error: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of AI services.
        
        Returns:
            Health status dictionary
        """
        health_status = {
            "openai": "unknown",
        }
        
        # Check OpenAI
        try:
            await self.openai_client.models.list()
            health_status["openai"] = "healthy"
        except Exception as e:
            logger.error(f"OpenAI health check failed: {str(e)}")
            health_status["openai"] = "unhealthy"
        
        return health_status
