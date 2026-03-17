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

    assert created["status"] == "planned"
    assert len(created["plans"]) >= 4

    list_response = client.get("/api/tasks")
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == created["id"]

    detail_response = client.get(f"/api/tasks/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["title"] == payload["title"]
