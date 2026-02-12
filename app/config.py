"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the multi-agent AI system."""

    # --- LLM ---
    openai_api_key: str = Field(default="", description="OpenAI API key")
    llm_model: str = Field(default="gpt-4o", description="Primary LLM model")
    llm_temperature: float = Field(default=0.1, description="LLM temperature")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="Embedding model"
    )

    # --- External Services ---
    tavily_api_key: str = Field(default="", description="Tavily search API key")
    sendgrid_api_key: str = Field(default="", description="SendGrid API key")
    sendgrid_from_email: str = Field(
        default="noreply@example.com", description="Sender email"
    )

    # --- ChromaDB ---
    chroma_persist_dir: str = Field(
        default="./data/chromadb", description="ChromaDB persistence directory"
    )
    chroma_collection_name: str = Field(
        default="knowledge_base", description="ChromaDB collection name"
    )

    # --- RAG ---
    chunk_size: int = Field(default=1000, description="Document chunk size")
    chunk_overlap: int = Field(default=200, description="Chunk overlap")

    # --- Server ---
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
