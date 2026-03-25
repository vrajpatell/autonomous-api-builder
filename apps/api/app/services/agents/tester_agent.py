from app.services.agents.base import Agent, AgentContext, AgentResult


class TesterAgent(Agent):
    name = "tester"

    def run(self, context: AgentContext, previous_outputs: dict[str, dict]) -> AgentResult:
        generated_files = previous_outputs.get("coder", {}).get("generated_files", {})
        checks = [
            {"name": "generated_files_present", "status": "passed" if generated_files else "failed"},
            {"name": "plan_exists", "status": "passed" if previous_outputs.get("planner") else "failed"},
        ]
        overall = "passed" if all(check["status"] == "passed" for check in checks) else "failed"
        return AgentResult(
            summary=f"Validation {overall}",
            payload={"overall": overall, "checks": checks},
        )
