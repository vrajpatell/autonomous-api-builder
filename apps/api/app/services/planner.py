import json
import re
from dataclasses import dataclass
from typing import Protocol

import httpx
from pydantic import BaseModel, ValidationError, field_validator


DEFAULT_PLAN_STEPS = [
    (
        "Analyze requirements",
        "Parse the prompt and extract architecture, stack, interfaces, and constraints.",
    ),
    (
        "Design system architecture",
        "Define backend modules, data models, API contracts, and service boundaries.",
    ),
    (
        "Generate implementation scaffolding",
        "Prepare project structure, core services, and integration points for delivery.",
    ),
    (
        "Validate and test",
        "Execute tests and static checks to verify correctness and quality gates.",
    ),
    (
        "Prepare deployment bundle",
        "Assemble deployment configuration, documentation, and release notes.",
    ),
]


class PlannerStep(BaseModel):
    step_number: int
    title: str
    description: str

    @field_validator("title", "description")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("must not be empty")
        return trimmed


class PlannerResponse(BaseModel):
    steps: list[PlannerStep]

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, steps: list[PlannerStep]) -> list[PlannerStep]:
        if not steps:
            raise ValueError("at least one plan step is required")

        normalized_steps = []
        for index, step in enumerate(steps, start=1):
            normalized_steps.append(
                PlannerStep(step_number=index, title=step.title, description=step.description)
            )
        return normalized_steps


class PlannerProvider(Protocol):
    def generate_plan(self, prompt: str) -> str:
        """Return a raw LLM response that includes JSON plan data."""


class OpenAICompatiblePlannerProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout_seconds: float = 20.0,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate_plan(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a planner that outputs JSON with shape "
                            '{"steps": [{"step_number": 1, "title": "...", "description": "..."}]}. '
                            "Do not include additional keys."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


class PlannerParseError(ValueError):
    pass


def parse_planner_response(raw_response: str) -> PlannerResponse:
    text = raw_response.strip()
    if not text:
        raise PlannerParseError("planner response is empty")

    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fence_match:
        text = fence_match.group(1)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise PlannerParseError("unable to locate JSON object in planner response")

    json_segment = text[start : end + 1]
    try:
        payload = json.loads(json_segment)
    except json.JSONDecodeError as exc:
        raise PlannerParseError("planner response is not valid JSON") from exc

    try:
        return PlannerResponse.model_validate(payload)
    except ValidationError as exc:
        raise PlannerParseError("planner response failed schema validation") from exc


@dataclass
class PlannerResult:
    plan: PlannerResponse
    source: str


class PlannerService:
    def __init__(self, provider: PlannerProvider | None, max_retries: int = 2) -> None:
        self.provider = provider
        self.max_retries = max_retries

    def generate_plan(self, prompt: str) -> PlannerResult:
        if self.provider is None:
            return PlannerResult(plan=self.default_plan(), source="fallback")

        for _ in range(self.max_retries + 1):
            try:
                raw_response = self.provider.generate_plan(prompt)
                parsed = parse_planner_response(raw_response)
                return PlannerResult(plan=parsed, source="llm")
            except Exception:
                continue

        return PlannerResult(plan=self.default_plan(), source="fallback")

    @staticmethod
    def default_plan() -> PlannerResponse:
        steps = [
            PlannerStep(step_number=index, title=title, description=description)
            for index, (title, description) in enumerate(DEFAULT_PLAN_STEPS, start=1)
        ]
        return PlannerResponse(steps=steps)
