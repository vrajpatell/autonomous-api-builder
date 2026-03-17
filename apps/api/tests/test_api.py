from datetime import datetime, timedelta, timezone

from app.workers.tasks import process_generation_task


def register_and_login(client, email: str, password: str, display_name: str = "User"):
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "display_name": display_name},
    )
    assert response.status_code == 201
    data = response.json()
    return {"Authorization": f"Bearer {data['access_token']}"}, data["user"]


def create_task(client, headers, title: str, prompt: str):
    response = client.post("/api/tasks", json={"title": title, "user_prompt": prompt}, headers=headers)
    assert response.status_code == 201
    return response.json()


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

    created = create_task(
        client,
        user1_headers,
        "FastAPI CRUD Generator",
        "Build a FastAPI CRUD API for employee records with JWT auth, PostgreSQL, Docker, tests, and deployment.",
    )

    assert created["status"] == "queued"
    assert created["planner_status"] == "pending"
    assert created["planner_source"] is None
    assert created["queue_job_id"].startswith("noop-")
    assert len(created["plans"]) == 0
    assert created["error_message"] is None
    assert len(created["progress_updates"]) == 2

    list_response = client.get("/api/tasks", headers=user1_headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == created["id"]
    assert body["meta"]["total_count"] == 1
    assert body["meta"]["current_page"] == 1

    other_list_response = client.get("/api/tasks", headers=user2_headers)
    assert other_list_response.status_code == 200
    assert other_list_response.json()["items"] == []

    detail_response = client.get(f"/api/tasks/{created['id']}", headers=user1_headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == "FastAPI CRUD Generator"

    forbidden_detail = client.get(f"/api/tasks/{created['id']}", headers=user2_headers)
    assert forbidden_detail.status_code == 404


def test_task_list_supports_pagination_filtering_sorting_and_search(client):
    headers, _ = register_and_login(client, "filters@example.com", "password123")

    create_task(client, headers, "Alpha API", "Build alpha API with auth, tests, docs, and deployment automation.")
    create_task(client, headers, "Beta Service", "Create beta service with queue integration and observability support.")
    create_task(client, headers, "Gamma Pipeline", "Design gamma data pipeline and build the worker integration layer.")

    list_response = client.get("/api/tasks?page=1&page_size=2", headers=headers)
    assert list_response.status_code == 200
    page_1 = list_response.json()
    assert len(page_1["items"]) == 2
    assert page_1["meta"] == {"total_count": 3, "current_page": 1, "page_size": 2, "total_pages": 2}

    list_response_page_2 = client.get("/api/tasks?page=2&page_size=2", headers=headers)
    assert list_response_page_2.status_code == 200
    assert len(list_response_page_2.json()["items"]) == 1

    search_response = client.get("/api/tasks?search=beta", headers=headers)
    assert search_response.status_code == 200
    assert len(search_response.json()["items"]) == 1
    assert search_response.json()["items"][0]["title"] == "Beta Service"

    status_filtered = client.get("/api/tasks?status=queued", headers=headers)
    assert status_filtered.status_code == 200
    assert len(status_filtered.json()["items"]) == 3

    sort_oldest = client.get("/api/tasks?sort_by=created_at&sort_order=asc", headers=headers)
    assert sort_oldest.status_code == 200
    titles = [item["title"] for item in sort_oldest.json()["items"]]
    assert titles == ["Alpha API", "Beta Service", "Gamma Pipeline"]



def test_task_list_supports_date_range_filter(client):
    headers, _ = register_and_login(client, "dates@example.com", "password123")
    create_task(client, headers, "Date filter task", "Build a task used to validate date range filters in list endpoints.")

    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=1)).isoformat()
    end = (now + timedelta(days=1)).isoformat()
    inside = client.get(f"/api/tasks?date_from={start}&date_to={end}", headers=headers)
    assert inside.status_code == 200
    assert inside.json()["meta"]["total_count"] == 1

    outside_start = (now + timedelta(days=1)).isoformat()
    outside_end = (now + timedelta(days=2)).isoformat()
    outside = client.get(f"/api/tasks?date_from={outside_start}&date_to={outside_end}", headers=headers)
    assert outside.status_code == 200
    assert outside.json()["meta"]["total_count"] == 0



def test_status_transitions_validate_and_persist_history(client):
    headers, _ = register_and_login(client, "status@example.com", "password123")
    task = create_task(
        client,
        headers,
        "Transition task",
        "Build a transition-ready task so status workflow rules can be validated through the API.",
    )

    to_planning = client.patch(
        f"/api/tasks/{task['id']}/status",
        headers=headers,
        json={"status": "planning", "message": "Worker started planning"},
    )
    assert to_planning.status_code == 200
    assert to_planning.json()["status"] == "planning"

    invalid_back = client.patch(
        f"/api/tasks/{task['id']}/status",
        headers=headers,
        json={"status": "queued", "message": "Invalid rewind"},
    )
    assert invalid_back.status_code == 409

    transition_sequence = ["generating", "reviewing", "completed"]
    for status in transition_sequence:
        response = client.patch(
            f"/api/tasks/{task['id']}/status",
            headers=headers,
            json={"status": status},
        )
        assert response.status_code == 200

    terminal_transition = client.patch(
        f"/api/tasks/{task['id']}/status",
        headers=headers,
        json={"status": "planning"},
    )
    assert terminal_transition.status_code == 409

    detail = client.get(f"/api/tasks/{task['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["status"] == "completed"


def test_worker_processes_task_asynchronously(client):
    headers, _ = register_and_login(client, "worker@example.com", "password123")
    task = create_task(
        client,
        headers,
        "Background generation",
        "Generate backend modules and verify tests for a mock API scaffolder.",
    )

    process_generation_task(task["id"])

    detail_response = client.get(f"/api/tasks/{task['id']}", headers=headers)
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["status"] == "completed"
    assert body["planner_status"] == "completed"
    assert body["planner_source"] == "fallback"
    assert len(body["plans"]) == 5
    assert len(body["artifacts"]) == 3
    artifact = body["artifacts"][0]
    assert artifact["storage_backend"] == "local"
    assert artifact["storage_key"].startswith("tasks/")
    assert artifact["file_size"] > 0
    status_history = [event["status"] for event in body["progress_updates"]]
    assert status_history == ["pending", "queued", "planning", "planning", "generating", "reviewing", "completed"]


def test_tasks_require_authentication(client):
    payload = {"title": "No auth", "user_prompt": "This request should fail without an auth token."}
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 401


def test_artifact_listing_metadata_and_download(client):
    headers, _ = register_and_login(client, "artifacts@example.com", "password123")
    task = create_task(
        client,
        headers,
        "Artifact task",
        "Generate assets and confirm metadata and downloads are available for each output.",
    )

    process_generation_task(task["id"])

    list_response = client.get(f"/api/tasks/{task['id']}/artifacts", headers=headers)
    assert list_response.status_code == 200
    artifacts = list_response.json()
    assert len(artifacts) == 3

    artifact_id = artifacts[0]["id"]
    metadata_response = client.get(f"/api/tasks/{task['id']}/artifacts/{artifact_id}", headers=headers)
    assert metadata_response.status_code == 200
    metadata = metadata_response.json()
    assert metadata["storage_backend"] == "local"
    assert metadata["storage_key"].startswith("tasks/")

    download_response = client.get(f"/api/tasks/{task['id']}/artifacts/{artifact_id}/download", headers=headers)
    assert download_response.status_code == 200
    assert len(download_response.content) == metadata["file_size"]
    assert "attachment;" in download_response.headers["content-disposition"]
