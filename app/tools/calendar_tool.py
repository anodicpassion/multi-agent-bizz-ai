"""Calendar / scheduling tool (mock implementation)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from langchain_core.tools import tool


# In-memory schedule store
_schedule: list[dict] = []


@tool
def schedule_meeting(
    title: str,
    date_time: str,
    attendees: str,
    duration_minutes: int = 60,
) -> str:
    """Schedule a meeting or event.

    Args:
        title: Meeting title.
        date_time: ISO-format datetime string (e.g. '2026-03-15T10:00:00').
        attendees: Comma-separated list of attendee names or emails.
        duration_minutes: Duration in minutes (default 60).

    Returns:
        JSON confirmation with meeting details and a generated event ID.
    """
    event_id = str(uuid.uuid4())[:8]
    event = {
        "event_id": event_id,
        "title": title,
        "date_time": date_time,
        "attendees": [a.strip() for a in attendees.split(",")],
        "duration_minutes": duration_minutes,
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _schedule.append(event)
    return json.dumps(event, indent=2)


@tool
def list_meetings() -> str:
    """List all scheduled meetings.

    Returns:
        JSON array of all scheduled meetings.
    """
    return json.dumps(_schedule, indent=2)
