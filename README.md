# Autonomous API Builder

Production-style MVP monorepo that accepts a natural-language API request, stores it, generates a structured execution plan, and shows task status/output in a dashboard.

## Monorepo Structure

```text
.
├── apps
│   ├── api                 # FastAPI + SQLAlchemy backend
│   └── web                 # Next.js 14 frontend
├── docs                    # Architecture notes
├── infra                   # Infra placeholders for future IaC
├── .github/workflows       # CI pipelines
├── docker-compose.yml      # Local full-stack environment
└── render.yaml             # Render deployment blueprint
```

## Architecture Decisions

1. **Monorepo split by runtime boundary**: frontend and backend are isolated in `apps/` for independent deployment and scaling.
2. **Service layer in backend**: task business logic is in `TaskService` so future agent workers can reuse core flows.
3. **Task-centric data model**: `Task`, `TaskPlan`, and `GeneratedArtifact` provide immediate utility now and a durable base for future autonomous modules.
4. **Planner abstraction with provider swap**: generation pipeline resolves a `PlannerService` that can use a provider (OpenAI-compatible today) or deterministic fallback without API changes.
5. **Worker-first task processing**: API requests persist tasks and enqueue Celery jobs so planning + generation stays out of request/response.
6. **Deployment-ready defaults**: Dockerized services, Render and Vercel configs, and GitHub Actions CI for backend tests.

## Features

- Landing page with product overview
- Auth-aware frontend flows:
  - Registration and login pages
  - Protected dashboard
  - Logout and current-user display in nav
- Dashboard with per-user task data:
  - Build request form
  - Task list with statuses
  - Task detail panel with generated plan
- FastAPI backend endpoints:
  - `GET /api/health`
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - `POST /api/tasks` (authenticated)
  - `GET /api/tasks` (authenticated)
  - `GET /api/tasks/{task_id}` (authenticated, owner-only)
- PostgreSQL storage via SQLAlchemy
- Redis-backed Celery queue for background generation workers
- LLM-driven planner with JSON schema validation, retries, and deterministic fallback
- Basic automated tests for backend and frontend scaffold

## Local Development

### 1) Prerequisites
- Docker + Docker Compose

### 2) Start all services

```bash
docker compose up --build
```

Services:
- Web: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Worker: Celery worker (`worker` service)
- Beat scaffold: Celery beat (`beat` service)

### 3) Environment files
- Backend template: `apps/api/.env.example`
- Frontend template: `apps/web/.env.example`

Important backend queue variables:
- `QUEUE_BACKEND` (`celery` by default, `noop` available for tests/fallback)
- `REDIS_URL`
- `CELERY_BROKER_URL` (optional override)
- `CELERY_RESULT_BACKEND` (optional override)

Planner variables:
- `PLANNER_MODEL` (default `gpt-4o-mini`)
- `PLANNER_API_KEY` (leave empty to force deterministic fallback planner)
- `PLANNER_BASE_URL` (OpenAI-compatible endpoint, default `https://api.openai.com/v1`)
- `PLANNER_MAX_RETRIES` (retries for malformed/failed LLM outputs)

Auth variables:
- `JWT_SECRET_KEY` (required in non-dev; use a strong random secret)
- `JWT_ALGORITHM` (default `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default `60`)

## Manual Non-Docker Run

### Backend
```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# in another terminal, start the worker
celery -A app.workers.celery_app.celery_app worker --loglevel=info

# optional scheduler scaffold
celery -A app.workers.celery_app.celery_app beat --loglevel=info
```

### Async Task Lifecycle

Task status flow:

`pending -> queued -> planning -> generating -> reviewing -> completed`

Planner lifecycle:

`pending -> running -> completed` (or `failed` when worker crashes). Planner source is tracked as `llm` or `fallback`.

Failure path:

`* -> failed` with `error_message` persisted on the task.

Progress updates are written to `task_progress_updates`, making worker execution observable by polling task detail endpoints.

### Frontend
```bash
cd apps/web
npm install
npm run dev
```

## Testing

### Backend
```bash
cd apps/api
PYTHONPATH=. pytest -q
```

### Frontend (placeholder scaffold)
```bash
cd apps/web
npm test
```

## Deployment Steps

### Backend on Render
1. Push repository to GitHub.
2. In Render, create Blueprint deploy using `render.yaml`.
3. Ensure `DATABASE_URL` is wired from the managed Postgres instance.
4. Render builds from `apps/api` Dockerfile and exposes port 8000.

### Frontend on Vercel
1. Import repo into Vercel.
2. Set project root to `apps/web`.
3. Set `NEXT_PUBLIC_API_BASE_URL` to your Render API URL + `/api`.
4. Deploy with default Next.js settings (`vercel.json` included).

## CI/CD

Backend CI workflow: `.github/workflows/backend-ci.yml`
- Installs dependencies
- Runs pytest on push/PR for backend-related changes

## Screenshots

> Add screenshots after running locally.

- Dashboard view placeholder
- Task creation flow placeholder
- Task detail/plan placeholder

## Next 10 Improvements

1. Add an alternate RQ queue adapter behind the queue backend interface.
2. Add richer planner observability (token usage/latency) and per-step confidence metadata.
3. Extend auth to role-based permissions (admin, project owner, auditor).
4. Add pagination, filtering, and status transitions for task workflows.
5. Add Alembic migration scripts and DB migration CI checks.
6. Add generated artifact persistence as files/object storage references.
7. Add structured logging, tracing, and observability dashboards.
8. Expand frontend tests with React Testing Library + Playwright E2E.
9. Add API versioning and stricter domain-level validation.
10. Add agent orchestration modules (planner, coder, tester, reviewer, deployer).
