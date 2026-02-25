"""Email / notification tool (mock + SendGrid path)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from langchain_core.tools import tool

from app.config import settings

logger = logging.getLogger(__name__)


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Email body content.

    Returns:
        JSON string confirming the email was sent (or logged in mock mode).
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    if settings.sendgrid_api_key:
        try:
            import sendgrid  # type: ignore[import-untyped]
            from sendgrid.helpers.mail import Content, Email, Mail, To  # type: ignore[import-untyped]

            sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
            message = Mail(
                from_email=Email(settings.sendgrid_from_email),
                to_emails=To(to),
                subject=subject,
                plain_text_content=Content("text/plain", body),
            )
            response = sg.client.mail.send.post(request_body=message.get())
            return json.dumps(
                {
                    "status": "sent",
                    "to": to,
                    "subject": subject,
                    "status_code": response.status_code,
                    "timestamp": timestamp,
                }
            )
        except Exception as exc:
            logger.exception("Failed to send email via SendGrid")
            return json.dumps({"status": "error", "error": str(exc)})

    # ── Mock fallback ──────────────────────────────────────────────
    logger.info("MOCK EMAIL → to=%s subject=%s", to, subject)
    return json.dumps(
        {
            "status": "sent_mock",
            "to": to,
            "subject": subject,
            "body_preview": body[:100],
            "timestamp": timestamp,
            "note": "Mock mode — configure SENDGRID_API_KEY for real delivery.",
        }
    )
