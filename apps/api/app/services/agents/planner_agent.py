from app.services.agents.base import Agent, AgentContext, AgentResult
from app.services.planner_factory import get_planner_service


class PlannerAgent(Agent):
    name = "planner"

    def run(self, context: AgentContext, previous_outputs: dict[str, dict]) -> AgentResult:
        planner_result = get_planner_service().generate_plan(context.user_prompt)
        return AgentResult(
            summary=f"Generated {len(planner_result.plan.steps)} structured steps",
            payload={
                "source": planner_result.source,
                "steps": [step.model_dump() for step in planner_result.plan.steps],
            },
        )
