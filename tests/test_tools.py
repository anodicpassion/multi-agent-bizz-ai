"""Tests for tool implementations."""

import json

from app.tools.web_search import web_search
from app.tools.email_tool import send_email
from app.tools.database_tool import query_database
from app.tools.calendar_tool import schedule_meeting, list_meetings
from app.tools.api_tool import call_api


class TestWebSearch:
    """Tests for the web_search tool."""

    def test_mock_search_returns_results(self):
        result = web_search.invoke({"query": "AI trends 2026"})
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "title" in data[0]
        assert "content" in data[0]

    def test_mock_search_includes_query(self):
        query = "business automation tools"
        result = web_search.invoke({"query": query})
        data = json.loads(result)
        assert query in data[0]["content"]


class TestEmailTool:
    """Tests for the send_email tool."""

    def test_mock_email_returns_confirmation(self):
        result = send_email.invoke({
            "to": "test@example.com",
            "subject": "Test Subject",
            "body": "Hello, this is a test email.",
        })
        data = json.loads(result)
        assert data["status"] == "sent_mock"
        assert data["to"] == "test@example.com"
        assert data["subject"] == "Test Subject"

    def test_mock_email_includes_body_preview(self):
        body = "A" * 200
        result = send_email.invoke({
            "to": "user@example.com",
            "subject": "Long Body",
            "body": body,
        })
        data = json.loads(result)
        assert len(data["body_preview"]) <= 100


class TestDatabaseTool:
    """Tests for the query_database tool."""

    def test_select_customers(self):
        result = query_database.invoke({"query": "SELECT * FROM customers"})
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["name"] == "Alice Johnson"

    def test_select_orders(self):
        result = query_database.invoke({"query": "SELECT * FROM orders WHERE status = 'completed'"})
        data = json.loads(result)
        assert len(data) == 2

    def test_rejects_non_select(self):
        result = query_database.invoke({"query": "DROP TABLE customers"})
        data = json.loads(result)
        assert "error" in data

    def test_handles_invalid_sql(self):
        result = query_database.invoke({"query": "SELECT * FROM nonexistent_table"})
        data = json.loads(result)
        assert "error" in data


class TestCalendarTool:
    """Tests for calendar tools."""

    def test_schedule_and_list_meeting(self):
        result = schedule_meeting.invoke({
            "title": "Sprint Planning",
            "date_time": "2026-03-15T10:00:00",
            "attendees": "Alice, Bob, Carol",
            "duration_minutes": 45,
        })
        data = json.loads(result)
        assert data["title"] == "Sprint Planning"
        assert data["status"] == "scheduled"
        assert len(data["attendees"]) == 3

        # Verify it shows up in the list
        meetings = json.loads(list_meetings.invoke({}))
        assert any(m["title"] == "Sprint Planning" for m in meetings)


class TestApiTool:
    """Tests for the generic API call tool."""

    def test_get_request(self):
        result = call_api.invoke({
            "method": "GET",
            "url": "https://httpbin.org/get",
        })
        data = json.loads(result)
        assert data["status_code"] == 200

    def test_invalid_json_headers(self):
        result = call_api.invoke({
            "method": "GET",
            "url": "https://example.com",
            "headers": "not-json",
        })
        data = json.loads(result)
        assert "error" in data
