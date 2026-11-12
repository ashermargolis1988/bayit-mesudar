from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app import database
from app.main import app


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch) -> Iterator[None]:
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    yield


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


def test_update_task_fields() -> None:
    with TestClient(app) as client:
        created = client.post(
            "/api/tasks",
            json={"title": "משימה ישנה", "assignee": "כולם", "frequency": "once"},
        )
        task_id = created.json()["id"]

        updated = client.patch(
            f"/api/tasks/{task_id}",
            json={
                "title": "משימה מעודכנת",
                "assignee": "אשר",
                "due_date": "2026-11-20",
                "frequency": "weekly",
            },
        )

        assert updated.status_code == 200
        expected_fields = {
            "title": "משימה מעודכנת",
            "assignee": "אשר",
            "due_date": "2026-11-20",
            "frequency": "weekly",
        }
        assert {
            key: updated.json()[key] for key in expected_fields
        } == expected_fields

        listed_task = next(
            task for task in client.get("/api/tasks").json() if task["id"] == task_id
        )
        assert listed_task["title"] == "משימה מעודכנת"
        assert listed_task["assignee"] == "אשר"
        assert listed_task["due_date"] == "2026-11-20"
        assert listed_task["frequency"] == "weekly"


def test_update_missing_task_returns_not_found() -> None:
    with TestClient(app) as client:
        response = client.patch("/api/tasks/999999", json={"title": "לא קיימת"})

        assert response.status_code == 404
        assert response.json()["detail"] == "המשימה לא נמצאה"


def test_update_task_rejects_invalid_frequency() -> None:
    with TestClient(app) as client:
        created = client.post("/api/tasks", json={"title": "בדיקת תדירות"})
        task_id = created.json()["id"]

        response = client.patch(
            f"/api/tasks/{task_id}", json={"frequency": "monthly"}
        )

        assert response.status_code == 422


def test_edit_controls_are_served() -> None:
    with TestClient(app) as client:
        page = client.get("/")
        script = client.get("/static/app.js")

        assert page.status_code == 200
        assert 'id="form-title"' in page.text
        assert 'id="cancel-edit"' in page.text
        assert script.status_code == 200
        assert 'data-action="edit"' in script.text
        assert 'method: "PATCH"' in script.text
        assert "messageElement.textContent = error.message" in script.text

