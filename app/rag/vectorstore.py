"""ChromaDB vector store wrapper with singleton access."""

from __future__ import annotations

import logging
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import settings
from app.llm.provider import get_embeddings

logger = logging.getLogger(__name__)

_vectorstore: Optional[Chroma] = None


def get_vectorstore() -> Chroma:
    """Return the singleton ChromaDB vector store instance.

    Creates the store on first call, using persistent storage at
    ``settings.chroma_persist_dir``.
    """
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=get_embeddings(),
            persist_directory=settings.chroma_persist_dir,
        )
        logger.info(
            "Initialised ChromaDB at %s (collection: %s)",
            settings.chroma_persist_dir,
            settings.chroma_collection_name,
        )
    return _vectorstore


def add_documents(documents: list[Document]) -> int:
    """Embed and add documents to the vector store.

    Returns:
        Number of documents added.
    """
    store = get_vectorstore()
    store.add_documents(documents)
    logger.info("Added %d document chunks to vector store", len(documents))
    return len(documents)


def similarity_search(query: str, k: int = 4) -> list[Document]:
    """Retrieve the top-k most relevant document chunks for a query.

    Args:
        query: The search query string.
        k: Number of results to return.

    Returns:
        List of ``Document`` objects ranked by relevance.
    """
    store = get_vectorstore()
    results = store.similarity_search(query, k=k)
    logger.debug("Vector search for '%s' returned %d results", query, len(results))
    return results
