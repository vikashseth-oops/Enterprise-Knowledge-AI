import asyncio
from collections.abc import AsyncIterator
from typing import Any

from groq import APIConnectionError, AsyncGroq, GroqError, RateLimitError

from app.config import settings
from app.core.errors import LLMServiceError
from app.core.logging import logger
from app.schemas.chat import TokenUsage


class GroqClient:
    """
    Robust Groq API client with exponential backoff retries,
    token tracking, streaming, and tool execution.
    """

    def __init__(
        self,
        api_key: str | None = None,
        gen_model: str | None = None,
        fast_model: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.gen_model = gen_model or settings.GROQ_GEN_MODEL
        self.fast_model = fast_model or settings.GROQ_FAST_MODEL
        self.timeout = timeout or settings.GROQ_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.GROQ_MAX_RETRIES

        self._client: AsyncGroq | None = None
        if self.api_key:
            self._client = AsyncGroq(
                api_key=self.api_key,
                timeout=self.timeout,
            )

    @property
    def client(self) -> AsyncGroq:
        if self._client is None:
            if not self.api_key:
                raise LLMServiceError("GROQ_API_KEY is not configured.")
            self._client = AsyncGroq(
                api_key=self.api_key,
                timeout=self.timeout,
            )
        return self._client

    async def _execute_with_retry(self, coroutine_fn, *args, **kwargs) -> Any:
        """Executes a Groq API call with exponential backoff on rate limits and network errors."""
        backoff = 1.0
        for attempt in range(1, self.max_retries + 1):
            try:
                return await coroutine_fn(*args, **kwargs)
            except (RateLimitError, APIConnectionError) as e:
                if attempt == self.max_retries:
                    logger.error("groq_retry_exhausted", attempt=attempt, error=str(e))
                    raise LLMServiceError(f"Groq API call failed after {self.max_retries} retries: {e!s}")
                logger.warning(
                    "groq_rate_limit_backoff",
                    attempt=attempt,
                    backoff=backoff,
                    error=str(e),
                )
                await asyncio.sleep(backoff)
                backoff *= 2.0
            except GroqError as e:
                logger.error("groq_api_error", error=str(e))
                raise LLMServiceError(f"Groq API error: {e!s}")
            except Exception as e:
                logger.error("groq_unexpected_error", error=str(e))
                raise LLMServiceError(f"Unexpected error communicating with Groq: {e!s}")

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: dict[str, str] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
    ) -> tuple[str, TokenUsage, list[dict[str, Any]] | None]:
        """
        Executes a non-streaming chat completion, returning (content, token_usage, tool_calls).
        """
        selected_model = model or self.gen_model

        kwargs: dict[str, Any] = {
            "model": selected_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format
        if tools:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice

        async def _call():
            return await self.client.chat.completions.create(**kwargs)

        response = await self._execute_with_retry(_call)

        choice = response.choices[0]
        content = choice.message.content or ""
        tool_calls = None
        if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in choice.message.tool_calls
            ]

        usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
        )

        return content, usage, tool_calls

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """
        Yields text chunks asynchronously for SSE streaming.
        """
        selected_model = model or self.gen_model

        async def _call():
            return await self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

        stream = await self._execute_with_retry(_call)

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())


_global_groq_client: GroqClient | None = None


def get_groq_client() -> GroqClient:
    global _global_groq_client
    if _global_groq_client is None:
        _global_groq_client = GroqClient()
    return _global_groq_client
