"""FastAPI dependency injection providers."""

from __future__ import annotations

from functools import lru_cache

from app.graph.workflow import get_compiled_workflow
from app.rag.vectorstore import get_vectorstore as _get_vs


def get_workflow():
    """Dependency: returns the compiled multi-agent workflow."""
    return get_compiled_workflow()


def get_vectorstore():
    """Dependency: returns the ChromaDB vector store instance."""
    return _get_vs()
