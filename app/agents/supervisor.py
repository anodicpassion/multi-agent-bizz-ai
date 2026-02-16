"""Supervisor agent — routes tasks to specialised worker agents."""

from __future__ import annotations

import json
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.llm.provider import get_llm
from app.models.state import AgentState

logger = logging.getLogger(__name__)

AGENT_NAMES = ["research", "reasoning", "task_executor", "communication"]


class RouterDecision(BaseModel):
    """Structured output for the supervisor's routing decision."""

    next_agent: Literal["research", "reasoning", "task_executor", "communication", "FINISH"] = Field(
        description="The next agent to route to, or FINISH if the task is complete."
    )
    reasoning: str = Field(
        description="Brief explanation of why this agent was selected."
    )


SUPERVISOR_SYSTEM_PROMPT = """You are a supervisor agent orchestrating a team of specialised AI agents for business automation. Your role is to analyze the user's request and decide which agent should handle the next step.

Available agents:
1. **research** — Searches the web and internal knowledge base for information. Use for fact-finding, data gathering, market research, and answering questions that need external/internal knowledge.
2. **reasoning** — Performs deep analysis, evaluates options, identifies patterns, and draws conclusions. Use for strategic thinking, planning, problem-solving, and synthesising information.
3. **task_executor** — Executes concrete business tasks: database queries, scheduling meetings, calling external APIs. Use when an action needs to be performed in an external system.
4. **communication** — Drafts and sends professional communications: emails, notifications, reports. Use when the task involves reaching out to people or composing messages.

Routing rules:
- Analyze what has been accomplished so far by reviewing the conversation history.
- If the task requires information, route to **research** first.
- If the gathered information needs analysis, route to **reasoning**.
- If a concrete action is needed (database, API, scheduling), route to **task_executor**.
- If a communication needs to be sent, route to **communication**.
- If the task is fully complete and a final answer can be given, choose **FINISH**.
- You may route to the same agent multiple times if needed.
- Always provide clear reasoning for your routing decision."""


def create_supervisor_node():
    """Create the supervisor node function for the LangGraph workflow."""

    llm = get_llm().with_structured_output(RouterDecision)

    def supervisor_node(state: AgentState) -> dict:
        """Evaluate the current state and decide the next agent."""
        messages = [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            *state["messages"],
        ]

        decision: RouterDecision = llm.invoke(messages)
        logger.info(
            "Supervisor → %s (reason: %s)",
            decision.next_agent,
            decision.reasoning,
        )

        return {
            "next_agent": decision.next_agent,
            "task_results": {
                "supervisor_reasoning": decision.reasoning,
            },
        }

    return supervisor_node
