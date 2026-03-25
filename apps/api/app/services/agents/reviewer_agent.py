from app.services.agents.base import Agent, AgentContext, AgentResult


class ReviewerAgent(Agent):
    name = "reviewer"

    def run(self, context: AgentContext, previous_outputs: dict[str, dict]) -> AgentResult:
        tester_status = previous_outputs.get("tester", {}).get("overall", "unknown")
        notes = [
            "Planner produced structured implementation intent.",
            "Coder generated lightweight scaffold placeholders.",
            f"Tester reported overall status: {tester_status}.",
        ]
        return AgentResult(
            summary="Generated review summary for orchestrated run",
            payload={"summary": " ".join(notes), "notes": notes},
        )
