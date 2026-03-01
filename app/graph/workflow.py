"""LangGraph multi-agent workflow definition.

Builds a StateGraph with a supervisor hub-and-spoke pattern:
    Supervisor ─┬─► Research
                ├─► Reasoning
                ├─► Task Executor
                ├─► Communication
                └─► FINISH (END)

All worker agents route back to the supervisor for re-evaluation.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.communication import create_communication_node
from app.agents.reasoning import create_reasoning_node
from app.agents.research import create_research_node
from app.agents.supervisor import create_supervisor_node
from app.agents.task_executor import create_task_executor_node
from app.models.state import AgentState

logger = logging.getLogger(__name__)


def _route_from_supervisor(state: AgentState) -> str:
    """Conditional edge function: reads ``next_agent`` from state."""
    next_agent = state.get("next_agent", "FINISH")
    if next_agent == "FINISH":
        return END
    return next_agent


def build_workflow() -> StateGraph:
    """Construct the multi-agent LangGraph workflow (uncompiled).

    Returns:
        A ``StateGraph`` ready to be compiled.
    """
    workflow = StateGraph(AgentState)

    # ── Add nodes ──────────────────────────────────────────────────
    workflow.add_node("supervisor", create_supervisor_node())
    workflow.add_node("research", create_research_node())
    workflow.add_node("reasoning", create_reasoning_node())
    workflow.add_node("task_executor", create_task_executor_node())
    workflow.add_node("communication", create_communication_node())

    # ── Entry point ────────────────────────────────────────────────
    workflow.set_entry_point("supervisor")

    # ── Supervisor → conditional routing ───────────────────────────
    workflow.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {
            "research": "research",
            "reasoning": "reasoning",
            "task_executor": "task_executor",
            "communication": "communication",
            END: END,
        },
    )

    # ── Worker agents → back to supervisor ─────────────────────────
    for agent_name in ("research", "reasoning", "task_executor", "communication"):
        workflow.add_edge(agent_name, "supervisor")

    return workflow


@lru_cache(maxsize=1)
def get_compiled_workflow():
    """Return a compiled, ready-to-invoke workflow with memory checkpointing."""
    workflow = build_workflow()
    checkpointer = MemorySaver()
    compiled = workflow.compile(checkpointer=checkpointer)
    logger.info("Multi-agent workflow compiled successfully")
    return compiled
