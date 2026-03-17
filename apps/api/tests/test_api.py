from app.workers.tasks import process_generation_task


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    payload = {
        "title": "FastAPI CRUD Generator",
        "user_prompt": "Build a FastAPI CRUD API for employee records with JWT auth, PostgreSQL, Docker, tests, and deployment.",
    }
    create_response = client.post("/api/tasks", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()

    assert created["status"] == "queued"
    assert created["queue_job_id"].startswith("noop-")
    assert len(created["plans"]) == 0
    assert created["error_message"] is None
    assert len(created["progress_updates"]) == 2

    list_response = client.get("/api/tasks")
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == created["id"]

    detail_response = client.get(f"/api/tasks/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == payload["title"]


def test_worker_processes_task_asynchronously(client):
    payload = {
        "title": "Background generation",
        "user_prompt": "Generate backend modules and verify tests for a mock API scaffolder.",
    }
    created = client.post("/api/tasks", json=payload).json()

    process_generation_task(created["id"])

    detail_response = client.get(f"/api/tasks/{created['id']}")
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["status"] == "completed"
    assert len(body["plans"]) == 5
    assert len(body["artifacts"]) == 1
    status_history = [event["status"] for event in body["progress_updates"]]
    assert status_history == ["pending", "queued", "planning", "generating", "reviewing", "completed"]
