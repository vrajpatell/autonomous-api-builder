# Architecture Notes

## Backend
- FastAPI with modular routers under `app/api/routes`.
- SQLAlchemy models for `Task`, `TaskPlan`, `GeneratedArtifact`.
- Service layer (`TaskService`) encapsulates task planning behavior.

## Frontend
- Next.js App Router with dashboard-centric UX.
- `lib/api.ts` centralizes backend HTTP calls.
- Component split for `TaskForm`, `TaskList`, and `TaskDetail`.

## Extensibility
- Task lifecycle and artifact table are prepared for asynchronous agent modules.
- Generated plans are persisted and can be enhanced with AI planner output later.
