"""Tests for the RAG pipeline — ingestion, vector store, and retriever."""

import tempfile
from pathlib import Path

from app.rag.ingestion import load_documents, chunk_documents, ingest_documents


class TestIngestion:
    """Tests for document loading and chunking."""

    def test_load_text_file(self, tmp_path: Path):
        fp = tmp_path / "test.txt"
        fp.write_text("Hello world. This is a test document for ingestion.")
        docs = load_documents([str(fp)])
        assert len(docs) == 1
        assert "Hello world" in docs[0].page_content

    def test_chunk_documents(self, tmp_path: Path):
        fp = tmp_path / "long.txt"
        # Create a document long enough to be split into multiple chunks
        fp.write_text("word " * 500)
        docs = load_documents([str(fp)])
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=20)
        assert len(chunks) > 1

    def test_ingest_documents_end_to_end(self, tmp_path: Path):
        fp = tmp_path / "doc.txt"
        fp.write_text("This is a complete end-to-end test. " * 50)
        chunks = ingest_documents([str(fp)])
        assert len(chunks) >= 1
        assert all(hasattr(c, "page_content") for c in chunks)

    def test_load_nonexistent_file(self):
        docs = load_documents(["/nonexistent/path/file.txt"])
        assert len(docs) == 0

    def test_metadata_preserved(self, tmp_path: Path):
        fp = tmp_path / "meta_test.txt"
        fp.write_text("Content for metadata test.")
        docs = load_documents([str(fp)])
        assert docs[0].metadata["filename"] == "meta_test.txt"
