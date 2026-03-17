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
4. **Mock plan generation on create**: every new task receives a 5-step plan to make dashboard output useful right away.
5. **Deployment-ready defaults**: Dockerized services, Render and Vercel configs, and GitHub Actions CI for backend tests.

## Features

- Landing page with product overview
- Dashboard with:
  - Build request form
  - Task list with statuses
  - Task detail panel with generated plan
- FastAPI backend endpoints:
  - `GET /api/health`
  - `POST /api/tasks`
  - `GET /api/tasks`
  - `GET /api/tasks/{task_id}`
- PostgreSQL storage via SQLAlchemy
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

### 3) Environment files
- Backend template: `apps/api/.env.example`
- Frontend template: `apps/web/.env.example`

## Manual Non-Docker Run

### Backend
```bash
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

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

1. Add async background worker queue (Celery/RQ) for long-running generation jobs.
2. Integrate LLM planner service for dynamic plan generation.
3. Add authentication + multi-user task ownership.
4. Add pagination, filtering, and status transitions for task workflows.
5. Add Alembic migration scripts and DB migration CI checks.
6. Add generated artifact persistence as files/object storage references.
7. Add structured logging, tracing, and observability dashboards.
8. Expand frontend tests with React Testing Library + Playwright E2E.
9. Add API versioning and stricter domain-level validation.
10. Add agent orchestration modules (planner, coder, tester, reviewer, deployer).
