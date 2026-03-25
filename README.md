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
  - Task list with status badges, filters, sorting, search, and pagination
  - Task detail panel with generated plan, status history, and downloadable artifacts
- FastAPI backend endpoints:
  - `GET /metrics` (Prometheus metrics)
  - `GET /api/metrics` (Prometheus metrics alias)
  - `GET /api/health`
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
  - `POST /api/tasks` (authenticated)
  - `GET /api/tasks` (authenticated, pagination/filter/sort/query metadata)
  - `GET /api/tasks/{task_id}` (authenticated, owner-only)
  - `PATCH /api/tasks/{task_id}/status` (authenticated, owner-only, transition-safe)
  - `GET /api/tasks/{task_id}/artifacts` (authenticated, owner-only artifact listing)
  - `GET /api/tasks/{task_id}/artifacts/{artifact_id}` (authenticated metadata lookup)
  - `GET /api/tasks/{task_id}/artifacts/{artifact_id}/download` (authenticated artifact retrieval)
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

Artifact storage variables:
- `STORAGE_BACKEND` (default `local`; interface is ready for S3/GCS/Azure backends)
- `STORAGE_LOCAL_BASE_PATH` (default `./data/artifacts`, artifacts are written as `tasks/<task_id>/<artifact_type>/<uuid>-<file_name>`)

## Manual Non-Docker Run

### Backend
```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# apply DB schema migrations
alembic upgrade head

uvicorn app.main:app --reload

# in another terminal, start the worker
celery -A app.workers.celery_app.celery_app worker --loglevel=info

# optional scheduler scaffold
celery -A app.workers.celery_app.celery_app beat --loglevel=info
```

### Database Migrations (Alembic)

All backend schema changes are managed with Alembic migrations. `Base.metadata.create_all(...)` is not used in app startup.

```bash
cd apps/api

# create a new migration from model changes
make migration-create message="add task labels"

# apply latest migrations
make migrate

# rollback one migration
make migration-downgrade

# fail if SQLAlchemy models and migrations drift
make migration-check
```

Equivalent direct Alembic commands:

```bash
alembic revision --autogenerate -m "your message"
alembic upgrade head
alembic downgrade -1
alembic check
```

### Async Task Lifecycle

Task status flow:

`pending -> queued -> planning -> generating -> reviewing -> completed`

Additional terminal statuses: `failed`, `cancelled`.

Transition policy rejects invalid rewinds (for example `completed -> planning`) and only allows explicit workflow edges.

Planner lifecycle:

`pending -> running -> completed` (or `failed` when worker crashes). Planner source is tracked as `llm` or `fallback`.

Failure path:

`* -> failed` with `error_message` persisted on the task.

Progress updates are written to `task_progress_updates`, making worker execution observable by polling task detail endpoints.
Generated outputs are persisted through a storage abstraction; local development writes files to disk and stores only artifact metadata + storage references in the database.

### Frontend
```bash
cd apps/web
npm install
npm run dev
```


## Observability

### What is instrumented
- **Structured JSON logs** across API startup, request middleware, task service lifecycle transitions, planner execution, artifact persistence, and Celery workers.
- **Correlation and request IDs** propagated through HTTP (`x-request-id`, `x-correlation-id`), queue enqueue/dequeue, worker execution, planner calls, and artifact generation logs.
- **Metrics for Prometheus/Grafana**:
  - `autobuilder_api_requests_total`
  - `autobuilder_api_request_latency_seconds`
  - `autobuilder_worker_jobs_total`
  - `autobuilder_worker_job_duration_seconds`
  - `autobuilder_tasks_lifecycle_total`
  - `autobuilder_active_tasks`
- **OpenTelemetry tracing hooks** with OTLP export support (vendor-neutral).
- **Frontend error hooks** for runtime errors, unhandled promise rejections, and API failures (JSON payload in browser console with correlation ID).

### Environment variables
Backend observability variables in `apps/api/.env.example`:
- `OTEL_ENABLED`
- `OTEL_SERVICE_NAME`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

### Local observability stack
`docker compose up --build` now includes:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Jaeger**: http://localhost:16686
- **OTel Collector** receiving OTLP on ports `4317` and `4318`

### Dashboard quick start
1. Start all services: `docker compose up --build`.
2. Open Grafana and verify the pre-provisioned Prometheus data source.
3. Build panels from `autobuilder_*` metrics for:
   - API throughput + latency
   - Worker success/failure ratio
   - Task lifecycle counts by status
4. Open Jaeger and inspect traces by service name (`autonomous-api-builder-api`).

### Security note
Error logging intentionally avoids dumping secret-bearing config values. Exceptions are logged with structured type/message fields, and queue/planner failures are persisted with sanitized task-level messages.

## Testing

### Backend
```bash
cd apps/api
PYTHONPATH=. pytest -q
```

### Frontend unit/integration (React Testing Library + Vitest)
```bash
cd apps/web
npm run test:unit
```

### Frontend E2E (Playwright)
```bash
cd apps/web
# first run only (or after Playwright upgrades)
npx playwright install --with-deps chromium
npm run test:e2e
```

### Frontend testing architecture
- `apps/web/tests/components/*`: focused component tests for `TaskForm` and `TaskList`.
- `apps/web/tests/pages/*`: page-level integration tests for dashboard loading/error behavior and auth flows.
- `apps/web/tests/utils/*`: shared test fixtures and API mock helpers.
- `apps/web/e2e/*`: end-to-end tests for register/login, task creation, task detail viewing, and list filtering/pagination interactions.

## Deployment Steps

### Backend on Render
1. Push repository to GitHub.
2. In Render, create Blueprint deploy using `render.yaml`.
3. Ensure `DATABASE_URL` is wired from the managed Postgres instance.
4. Run `alembic upgrade head` during deploy/release before serving traffic.
5. Render builds from `apps/api` Dockerfile and exposes port 8000.

### Frontend on Vercel
1. Import repo into Vercel.
2. Set project root to `apps/web`.
3. Set `NEXT_PUBLIC_API_BASE_URL` to your Render API URL + `/api`.
4. Deploy with default Next.js settings (`vercel.json` included).

## CI/CD

Backend CI workflow: `.github/workflows/backend-ci.yml`
- Installs dependencies
- Starts a temporary PostgreSQL service
- Runs `alembic upgrade head`
- Runs `alembic check` to catch migration/model drift
- Runs pytest on push/PR for backend-related changes

Frontend CI workflow: `.github/workflows/frontend-ci.yml`
- Installs Node dependencies in `apps/web`
- Runs React Testing Library + Vitest unit/integration tests
- Installs Playwright Chromium browser
- Runs Playwright E2E workflows on push/PR for frontend-related changes

## Screenshots

> Add screenshots after running locally.

- Dashboard view placeholder
- Task creation flow placeholder
- Task detail/plan placeholder

## Next 10 Improvements

1. Add an alternate RQ queue adapter behind the queue backend interface.
2. Add richer planner observability (token usage/latency) and per-step confidence metadata.
3. Extend auth to role-based permissions (admin, project owner, auditor).
4. Add audit logging + webhook notifications for workflow state changes.
5. Add artifact integrity checks and retention policies for generated files.
6. Add structured logging, tracing, and observability dashboards.
7. Expand frontend tests with React Testing Library + Playwright E2E.
8. Add API versioning and stricter domain-level validation.
9. Add agent orchestration modules (planner, coder, tester, reviewer, deployer).
10. Add canary deploy + rollback automation for backend releases.
