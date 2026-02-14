"""LLM and embedding provider abstraction.

Centralises model instantiation so swapping providers is a one-line change.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config import settings


@lru_cache(maxsize=4)
def get_llm(
    model: str | None = None,
    temperature: float | None = None,
) -> ChatOpenAI:
    """Return a cached ChatOpenAI instance.

    Args:
        model: Model name override (defaults to ``settings.llm_model``).
        temperature: Temperature override (defaults to ``settings.llm_temperature``).
    """
    return ChatOpenAI(
        model=model or settings.llm_model,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        api_key=settings.openai_api_key,
    )


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """Return a cached OpenAIEmbeddings instance."""
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
