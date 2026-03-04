"""FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

# ── Logging ───────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    logger.info("🚀 Multi-Agent Business AI starting up …")
    logger.info("   LLM model     : %s", settings.llm_model)
    logger.info("   Embedding     : %s", settings.embedding_model)
    logger.info("   ChromaDB dir  : %s", settings.chroma_persist_dir)
    logger.info("   Tavily search : %s", "enabled" if settings.tavily_api_key else "mock")
    logger.info("   SendGrid      : %s", "enabled" if settings.sendgrid_api_key else "mock")
    yield
    logger.info("Multi-Agent Business AI shutting down …")


# ── App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Multi-Agent Business AI",
    description=(
        "A multi-agent AI system for business automation, powered by "
        "LangGraph orchestration, RAG-enabled knowledge retrieval, and "
        "tool-calling agents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


# ── Convenience: root redirect to docs ────────────────────────────────


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
