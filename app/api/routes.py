"""API route definitions for the multi-agent business automation system."""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from langchain_core.messages import AIMessage, HumanMessage

from app.api.dependencies import get_vectorstore, get_workflow
from app.models.schemas import (
    AgentInfo,
    AgentStatusResponse,
    ChatRequest,
    ChatResponse,
    DocumentInfo,
    DocumentUploadResponse,
    HealthResponse,
)
from app.rag.ingestion import ingest_documents
from app.rag.vectorstore import add_documents

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Health ────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check if the system is running and healthy."""
    return HealthResponse()


# ── Chat ──────────────────────────────────────────────────────────────


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, workflow=Depends(get_workflow)):
    """Send a message to the multi-agent system and receive a response.

    The supervisor agent will route the message to appropriate specialist
    agents that collaborate to produce a final answer.
    """
    session_id = request.session_id or str(uuid.uuid4())

    config = {"configurable": {"thread_id": session_id}}
    input_state = {
        "messages": [HumanMessage(content=request.message)],
        "next_agent": "",
        "context": "",
        "task_results": {},
        "final_answer": "",
    }

    try:
        # Invoke the workflow — this runs the full supervisor loop
        result = workflow.invoke(input_state, config=config)

        # Extract the final AI message
        messages = result.get("messages", [])
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        final_answer = ai_messages[-1].content if ai_messages else "No response generated."

        # Collect which agents participated
        agents_used: list[str] = []
        for msg in messages:
            if hasattr(msg, "name") and msg.name and msg.name not in agents_used:
                agents_used.append(msg.name)

        return ChatResponse(
            answer=final_answer,
            session_id=session_id,
            agents_used=agents_used,
        )

    except Exception as exc:
        logger.exception("Chat processing failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ── Documents ─────────────────────────────────────────────────────────

UPLOAD_DIR = Path("data/uploads")


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    tags=["Knowledge Base"],
)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document to the RAG knowledge base.

    Supported formats: .txt, .md
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".txt", ".md"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported: .txt, .md",
        )

    # Save the uploaded file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    # Ingest into vector store
    try:
        chunks = ingest_documents([str(file_path)])
        count = add_documents(chunks)
        return DocumentUploadResponse(
            filename=file.filename,
            chunks_created=count,
        )
    except Exception as exc:
        logger.exception("Document ingestion failed")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/documents",
    response_model=list[DocumentInfo],
    tags=["Knowledge Base"],
)
async def list_documents():
    """List all uploaded documents in the knowledge base."""
    docs: list[DocumentInfo] = []
    if UPLOAD_DIR.exists():
        for f in UPLOAD_DIR.iterdir():
            if f.is_file():
                stat = f.stat()
                docs.append(
                    DocumentInfo(
                        filename=f.name,
                        chunk_count=0,  # Would need metadata store for accurate count
                        ingested_at=str(stat.st_mtime),
                    )
                )
    return docs


# ── Agents ────────────────────────────────────────────────────────────


@router.get(
    "/agents/status",
    response_model=AgentStatusResponse,
    tags=["System"],
)
async def agents_status():
    """List all available agents and their capabilities."""
    agents = [
        AgentInfo(
            name="supervisor",
            description="Routes tasks to specialist agents based on the request",
            tools=["structured_output_routing"],
        ),
        AgentInfo(
            name="research",
            description="Searches the web and internal knowledge base for information",
            tools=["web_search", "knowledge_base_search"],
        ),
        AgentInfo(
            name="reasoning",
            description="Performs deep analysis, pattern recognition, and strategic thinking",
            tools=["knowledge_base_search"],
        ),
        AgentInfo(
            name="task_executor",
            description="Executes business tasks: database queries, scheduling, API calls",
            tools=["query_database", "schedule_meeting", "list_meetings", "call_api"],
        ),
        AgentInfo(
            name="communication",
            description="Drafts and sends professional emails and notifications",
            tools=["send_email"],
        ),
    ]
    return AgentStatusResponse(agents=agents, total_agents=len(agents))
