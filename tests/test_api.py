from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_create_and_list_task() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/tasks",
            json={"title": "בדיקת משימה", "assignee": "אני", "frequency": "once"},
        )
        assert created.status_code == 201
        task_id = created.json()["id"]
        listed = client.get("/api/tasks")
        assert any(task["id"] == task_id for task in listed.json())

