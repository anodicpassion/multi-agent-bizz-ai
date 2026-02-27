"""Document ingestion pipeline — loading, chunking, and metadata extraction."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)

# Mapping of file extensions to loader classes
_LOADERS: dict[str, type] = {
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
}


def _load_single_file(file_path: str | Path) -> list[Document]:
    """Load a single file using the appropriate loader."""
    path = Path(file_path)
    ext = path.suffix.lower()

    loader_cls = _LOADERS.get(ext)
    if loader_cls is None:
        # Fall back to plain text for unknown extensions
        logger.warning("No specialised loader for %s — using TextLoader", ext)
        loader_cls = TextLoader

    try:
        loader = loader_cls(str(path))
        docs = loader.load()
        # Inject source metadata
        for doc in docs:
            doc.metadata["source"] = str(path)
            doc.metadata["filename"] = path.name
        return docs
    except Exception:
        logger.exception("Failed to load %s", path)
        return []


def load_documents(paths: list[str | Path]) -> list[Document]:
    """Load documents from a list of file paths.

    Supports: .txt, .md — additional loaders can be registered in ``_LOADERS``.
    """
    all_docs: list[Document] = []
    for p in paths:
        all_docs.extend(_load_single_file(p))
    logger.info("Loaded %d raw documents from %d files", len(all_docs), len(paths))
    return all_docs


def chunk_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """Split documents into smaller chunks for embedding.

    Args:
        documents: Raw documents from loaders.
        chunk_size: Override for ``settings.chunk_size``.
        chunk_overlap: Override for ``settings.chunk_overlap``.

    Returns:
        List of chunked ``Document`` objects with preserved metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info("Split into %d chunks", len(chunks))
    return chunks


def ingest_documents(file_paths: list[str | Path]) -> list[Document]:
    """End-to-end pipeline: load → chunk → return documents ready for embedding."""
    raw = load_documents(file_paths)
    if not raw:
        logger.warning("No documents loaded from the provided paths")
        return []
    return chunk_documents(raw)
