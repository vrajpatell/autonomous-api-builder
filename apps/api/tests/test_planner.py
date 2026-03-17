from app.services.planner import PlannerService, parse_planner_response


class FlakyProvider:
    def __init__(self):
        self.calls = 0

    def generate_plan(self, prompt: str) -> str:
        self.calls += 1
        if self.calls < 2:
            return "not-json"
        return '{"steps":[{"step_number":10,"title":"Plan","description":"Ship it"}]}'


class FailingProvider:
    def generate_plan(self, prompt: str) -> str:
        raise RuntimeError("provider unavailable")


def test_parse_planner_response_normalizes_step_numbers():
    parsed = parse_planner_response(
        '{"steps":[{"step_number":7,"title":"Analyze","description":"Inspect requirements"}]}'
    )
    assert len(parsed.steps) == 1
    assert parsed.steps[0].step_number == 1


def test_planner_retries_then_succeeds():
    provider = FlakyProvider()
    service = PlannerService(provider=provider, max_retries=2)

    result = service.generate_plan("build me an api")

    assert provider.calls == 2
    assert result.source == "llm"
    assert result.plan.steps[0].title == "Plan"


def test_planner_falls_back_after_failures():
    service = PlannerService(provider=FailingProvider(), max_retries=1)

    result = service.generate_plan("build me an api")

    assert result.source == "fallback"
    assert len(result.plan.steps) == 5
