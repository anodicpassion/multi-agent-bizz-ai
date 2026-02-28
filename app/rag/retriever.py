"""RAG retrieval chain — combines vector search with contextual prompt."""

from __future__ import annotations

import logging

from langchain_core.tools import tool

from app.rag.vectorstore import similarity_search

logger = logging.getLogger(__name__)


def retrieve_context(query: str, k: int = 4) -> str:
    """Retrieve relevant context from the knowledge base.

    Performs a similarity search and concatenates the results into a single
    context string suitable for injection into an LLM prompt.

    Args:
        query: The user or agent query.
        k: Number of document chunks to retrieve.

    Returns:
        Concatenated context string, or a fallback message if nothing is found.
    """
    docs = similarity_search(query, k=k)
    if not docs:
        return "No relevant context    found in the knowledge base."

    context_parts: list[str] = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("filename", "unknown")
        context_parts.append(
            f"[Source {i}: {source}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(context_parts)


@tool
def knowledge_base_search(query: str) -> str:
    """Search the internal knowledge base for relevant information.

    Use this tool when you need context from previously ingested documents,
    company policies, product documentation, or other internal resources.

    Args:
        query: Natural language search query.

    Returns:
        Relevant excerpts from the knowledge base, with source attribution.
    """
    return retrieve_context(query)
