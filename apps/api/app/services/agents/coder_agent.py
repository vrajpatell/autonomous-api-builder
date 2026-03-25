from app.services.agents.base import Agent, AgentContext, AgentResult


class CoderAgent(Agent):
    name = "coder"

    def run(self, context: AgentContext, previous_outputs: dict[str, dict]) -> AgentResult:
        planner_steps = previous_outputs.get("planner", {}).get("steps", [])
        file_map = {
            "app/main.py": "# Placeholder generated entrypoint\nfrom fastapi import FastAPI\napp = FastAPI()\n",
            "app/routes/health.py": "from fastapi import APIRouter\nrouter = APIRouter()\n",
            "tests/test_health.py": "def test_health_placeholder():\n    assert True\n",
        }
        return AgentResult(
            summary="Prepared scaffold artifact candidates using generation service abstraction",
            payload={
                "input_plan_step_count": len(planner_steps),
                "generated_files": file_map,
            },
        )
