"""LangGraph shared agent state definition."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state passed between all agents in the LangGraph workflow.

    Attributes:
        messages: Conversation history, automatically merged via add_messages reducer.
        next_agent: Routing decision from the supervisor — which agent acts next.
        context: RAG-retrieved context to ground agent responses.
        task_results: Accumulated results from individual agents keyed by agent name.
        final_answer: The synthesized final output returned to the user.
    """

    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str
    context: str
    task_results: Annotated[dict, operator.ior]
    final_answer: str
