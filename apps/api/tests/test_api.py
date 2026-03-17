from app.workers.tasks import process_generation_task


def register_and_login(client, email: str, password: str, display_name: str = "User"):
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "display_name": display_name},
    )
    assert response.status_code == 201
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_me(client):
    headers, user = register_and_login(client, "me@example.com", "password123")
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["id"] == user["id"]
    assert me_response.json()["email"] == "me@example.com"


def test_create_and_list_tasks_scoped_by_owner(client):
    user1_headers, _ = register_and_login(client, "owner1@example.com", "password123")
    user2_headers, _ = register_and_login(client, "owner2@example.com", "password123")

    payload = {
        "title": "FastAPI CRUD Generator",
        "user_prompt": "Build a FastAPI CRUD API for employee records with JWT auth, PostgreSQL, Docker, tests, and deployment.",
    }
    create_response = client.post("/api/tasks", json=payload, headers=user1_headers)
    assert create_response.status_code == 201
    created = create_response.json()

    assert created["status"] == "queued"
    assert created["planner_status"] == "pending"
    assert created["planner_source"] is None
    assert created["queue_job_id"].startswith("noop-")
    assert len(created["plans"]) == 0
    assert created["error_message"] is None
    assert len(created["progress_updates"]) == 2

    list_response = client.get("/api/tasks", headers=user1_headers)
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == created["id"]

    other_list_response = client.get("/api/tasks", headers=user2_headers)
    assert other_list_response.status_code == 200
    assert other_list_response.json() == []

    detail_response = client.get(f"/api/tasks/{created['id']}", headers=user1_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == payload["title"]

    forbidden_detail = client.get(f"/api/tasks/{created['id']}", headers=user2_headers)
    assert forbidden_detail.status_code == 404


def test_worker_processes_task_asynchronously(client):
    headers, _ = register_and_login(client, "worker@example.com", "password123")
    payload = {
        "title": "Background generation",
        "user_prompt": "Generate backend modules and verify tests for a mock API scaffolder.",
    }
    created = client.post("/api/tasks", json=payload, headers=headers).json()

    process_generation_task(created["id"])

    detail_response = client.get(f"/api/tasks/{created['id']}", headers=headers)
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["status"] == "completed"
    assert body["planner_status"] == "completed"
    assert body["planner_source"] == "fallback"
    assert len(body["plans"]) == 5
    assert len(body["artifacts"]) == 1
    status_history = [event["status"] for event in body["progress_updates"]]
    assert status_history == ["pending", "queued", "planning", "planning", "generating", "reviewing", "completed"]


def test_tasks_require_authentication(client):
    payload = {"title": "No auth", "user_prompt": "This request should fail without an auth token."}
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 401
