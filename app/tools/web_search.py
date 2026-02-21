"""Web search tool using Tavily (with mock fallback)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from langchain_core.tools import tool

from app.config import settings


@tool
def web_search(query: str) -> str:
    """Search the web for up-to-date information on a topic.

    Args:
        query: The search query string.

    Returns:
        A JSON string containing search results with titles, URLs, and snippets.
    """
    if settings.tavily_api_key:
        from tavily import TavilyClient  # type: ignore[import-untyped]

        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(query=query, max_results=5)
        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            }
            for r in response.get("results", [])
        ]
        return json.dumps(results, indent=2)

    # ── Mock fallback ──────────────────────────────────────────────
    return json.dumps(
        [
            {
                "title": f"Search result for: {query}",
                "url": "https://example.com/result",
                "content": (
                    f"This is a simulated search result for '{query}'. "
                    f"In production, connect a Tavily API key for real results. "
                    f"Retrieved at {datetime.now(timezone.utc).isoformat()}."
                ),
            }
        ],
        indent=2,
    )
