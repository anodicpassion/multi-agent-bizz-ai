"""Pydantic request / response schemas for the FastAPI layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Chat ──────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str = Field(..., min_length=1, description="User message")
    session_id: str | None = Field(
        default=None, description="Optional session ID for conversation continuity"
    )


class AgentStep(BaseModel):
    """A single step taken by an agent during processing."""

    agent: str = Field(..., description="Name of the agent that acted")
    action: str = Field(..., description="What the agent did")
    result: str = Field(default="", description="Output from the agent")


class ChatResponse(BaseModel):
    """Response from the multi-agent system."""

    answer: str = Field(..., description="Final synthesized answer")
    session_id: str = Field(..., description="Session ID for follow-up messages")
    agents_used: list[str] = Field(
        default_factory=list, description="Agents that contributed"
    )
    steps: list[AgentStep] = Field(
        default_factory=list, description="Step-by-step agent execution trace"
    )


# ── Documents ─────────────────────────────────────────────────────────


class DocumentUploadResponse(BaseModel):
    """Response after uploading a document to the knowledge base."""

    filename: str
    chunks_created: int
    message: str = "Document ingested successfully"


class DocumentInfo(BaseModel):
    """Metadata about an ingested document."""

    filename: str
    chunk_count: int
    ingested_at: str


# ── Agents ────────────────────────────────────────────────────────────


class AgentInfo(BaseModel):
    """Description of an available agent."""

    name: str
    description: str
    tools: list[str] = Field(default_factory=list)


class AgentStatusResponse(BaseModel):
    """System-wide agent status."""

    agents: list[AgentInfo]
    total_agents: int


# ── Health ────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "1.0.0"
    agents_ready: bool = True
