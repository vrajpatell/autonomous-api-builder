from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AgentContext:
    task_id: int
    title: str
    user_prompt: str


@dataclass
class AgentResult:
    summary: str
    payload: dict[str, Any]


class Agent(Protocol):
    name: str

    def run(self, context: AgentContext, previous_outputs: dict[str, dict[str, Any]]) -> AgentResult:
        """Execute agent and return structured payload."""
