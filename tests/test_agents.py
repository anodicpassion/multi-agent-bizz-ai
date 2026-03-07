"""Tests for the supervisor agent and routing logic."""

from app.agents.supervisor import AGENT_NAMES, RouterDecision


class TestSupervisor:
    """Tests for the supervisor routing logic."""

    def test_agent_names_defined(self):
        assert "research" in AGENT_NAMES
        assert "reasoning" in AGENT_NAMES
        assert "task_executor" in AGENT_NAMES
        assert "communication" in AGENT_NAMES

    def test_router_decision_valid_agents(self):
        for agent in AGENT_NAMES:
            decision = RouterDecision(
                next_agent=agent,
                reasoning=f"Test routing to {agent}",
            )
            assert decision.next_agent == agent

    def test_router_decision_finish(self):
        decision = RouterDecision(
            next_agent="FINISH",
            reasoning="Task is complete",
        )
        assert decision.next_agent == "FINISH"

    def test_router_decision_has_reasoning(self):
        decision = RouterDecision(
            next_agent="research",
            reasoning="The user needs information",
        )
        assert len(decision.reasoning) > 0
