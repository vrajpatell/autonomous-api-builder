from app.workers.tasks import process_generation_task

from tests.test_api import create_task, register_and_login


def test_orchestration_persists_agent_results(client):
    headers, _ = register_and_login(client, "orchestrator@example.com", "password123")
    task = create_task(
        client,
        headers,
        "Orchestrated task",
        "Generate a lightweight architecture and deployment checklist using multiple agents.",
    )

    process_generation_task(task["id"])

    detail = client.get(f"/api/v1/tasks/{task['id']}", headers=headers)
    assert detail.status_code == 200
    body = detail.json()

    assert body["status"] == "completed"
    assert len(body["orchestration_runs"]) == 1
    run = body["orchestration_runs"][0]
    assert run["status"] == "completed"
    assert run["current_agent"] is None

    agent_runs = run["agent_runs"]
    assert [item["agent_name"] for item in agent_runs] == ["planner", "coder", "tester", "reviewer", "deployer"]
    assert all(item["status"] == "completed" for item in agent_runs)
    assert all(item["output_payload"] for item in agent_runs)

    deployment_artifacts = [a for a in body["artifacts"] if a["artifact_type"] == "deployment"]
    assert len(deployment_artifacts) == 1
