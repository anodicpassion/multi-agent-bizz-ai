"""Tests for the FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_returns_200(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


class TestAgentsEndpoint:
    """Tests for the agent status endpoint."""

    def test_agents_status_returns_all_agents(self):
        response = client.get("/api/v1/agents/status")
        assert response.status_code == 200
        data = response.json()
        assert data["total_agents"] == 5
        agent_names = [a["name"] for a in data["agents"]]
        assert "supervisor" in agent_names
        assert "research" in agent_names
        assert "reasoning" in agent_names
        assert "task_executor" in agent_names
        assert "communication" in agent_names


class TestDocumentsEndpoint:
    """Tests for the document management endpoints."""

    def test_list_documents_empty(self):
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_upload_unsupported_format(self):
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.xyz", b"content", "application/octet-stream")},
        )
        assert response.status_code == 400


class TestRootRedirect:
    """Tests for the root endpoint."""

    def test_root_redirects_to_docs(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/docs" in response.headers.get("location", "")
