# Architecture Notes

## Backend
- FastAPI backend routes are versioned and mounted under `/api/v1` via `app/api/v1/*` modules.
- A compatibility mount keeps `/api/*` alive short-term while reusing the same v1 routers.
- SQLAlchemy models include `Task`, `TaskPlan`, `GeneratedArtifact`, and workflow/progress entities.
- Service/domain layers own business rules:
  - `TaskService` orchestrates persistence + lifecycle transitions.
  - `TaskDomainRules` centralizes stricter task validation rules.
  - `DomainError` subclasses provide typed failure modes for API translation.
- Global exception handlers normalize API failures into a single error envelope.

## Frontend
- Next.js App Router with dashboard-centric UX.
- `lib/api.ts` centralizes backend HTTP calls and now defaults to `/api/v1`.
- Component split for `TaskForm`, `TaskList`, and `TaskDetail`.

## Extensibility
- Versioned router boundaries keep v1 stable while enabling parallel v2 implementation.
- Task lifecycle and artifact table are prepared for asynchronous agent modules.
- Generated plans are persisted and can be enhanced with AI planner output later.


## Agent-Oriented Orchestration
- `OrchestrationService` is the central coordinator executed by the async worker.
- Agent interfaces are modular and swappable through `app/services/agents/*`:
  - planner
  - coder
  - tester
  - reviewer
  - deployer
- Persistence model:
  - `orchestration_runs`: workflow-level status (`running/completed/failed`), current agent, timing
  - `agent_runs`: per-agent sequence, status, output payload, error payload, timing
- Existing queue compatibility is preserved: API still enqueues one worker job per task; worker now delegates to orchestrator.
- UI consumption: `TaskRead` includes orchestration and agent run records for per-agent progress rendering in task details.

### Interaction Flow (text diagram)
```text
API create task -> queue backend -> Celery worker
  -> OrchestrationService.run(task)
      -> PlannerAgent.run
      -> CoderAgent.run
      -> TesterAgent.run
      -> ReviewerAgent.run
      -> DeployerAgent.run
  -> persist artifacts + agent run records
  -> mark task completed/failed
```
