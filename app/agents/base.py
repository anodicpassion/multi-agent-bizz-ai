"""Base agent factory — creates tool-calling ReAct agents."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from app.models.state import AgentState


def create_agent(
    llm: BaseChatModel,
    tools: list[BaseTool],
    system_prompt: str,
) -> callable:
    """Create a LangGraph-compatible ReAct agent node.

    Args:
        llm: The language model instance.
        tools: List of tools the agent can invoke.
        system_prompt: Instructions that define the agent's role and behaviour.

    Returns:
        A callable ``agent_node`` function that fits the LangGraph node signature.
    """
    agent = create_react_agent(llm, tools, prompt=system_prompt)

    def agent_node(state: AgentState) -> dict:
        """Execute the agent and return updated state."""
        result = agent.invoke(state)
        return {
            "messages": result["messages"],
        }

    return agent_node
