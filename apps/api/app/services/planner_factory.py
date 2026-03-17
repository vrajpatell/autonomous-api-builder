from app.core.config import settings
from app.services.planner import OpenAICompatiblePlannerProvider, PlannerService


def get_planner_service() -> PlannerService:
    if not settings.planner_api_key:
        return PlannerService(provider=None, max_retries=settings.planner_max_retries)

    provider = OpenAICompatiblePlannerProvider(
        api_key=settings.planner_api_key,
        model=settings.planner_model,
        base_url=settings.planner_base_url,
    )
    return PlannerService(provider=provider, max_retries=settings.planner_max_retries)
