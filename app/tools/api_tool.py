"""Generic HTTP API caller tool."""

from __future__ import annotations

import json
import logging

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def call_api(
    method: str,
    url: str,
    headers: str = "{}",
    body: str = "{}",
) -> str:
    """Make an HTTP request to an external API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, PATCH).
        url: The full URL to call.
        headers: JSON string of HTTP headers.
        body: JSON string of the request body (for POST/PUT/PATCH).

    Returns:
        JSON string with status_code and response body.
    """
    method = method.upper()
    try:
        parsed_headers = json.loads(headers)
        parsed_body = json.loads(body)
    except json.JSONDecodeError as exc:
        return json.dumps({"error": f"Invalid JSON: {exc}"})

    try:
        with httpx.Client(timeout=30) as client:
            response = client.request(
                method=method,
                url=url,
                headers=parsed_headers,
                json=parsed_body if method in ("POST", "PUT", "PATCH") else None,
            )
        # Try to parse response as JSON, fall back to text
        try:
            resp_data = response.json()
        except Exception:
            resp_data = response.text

        return json.dumps(
            {
                "status_code": response.status_code,
                "data": resp_data,
            },
            indent=2,
            default=str,
        )
    except httpx.HTTPError as exc:
        logger.exception("API call failed")
        return json.dumps({"error": str(exc)})
