"""API tests for task CRUD."""


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Buy milk", "description": "2%", "completed": False},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["title"] == "Buy milk"
    assert body["description"] == "2%"
    assert body["completed"] is False
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_defaults(client):
    response = client.post("/tasks", json={"title": "Stretch"})
    assert response.status_code == 201
    body = response.json()
    assert body["description"] is None
    assert body["completed"] is False


def test_create_rejects_blank_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_create_rejects_long_title(client):
    response = client.post("/tasks", json={"title": "a" * 201})
    assert response.status_code == 422


def test_list_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_returns_tasks_in_id_order(client):
    first = client.post("/tasks", json={"title": "First"}).json()
    second = client.post("/tasks", json={"title": "Second"}).json()
    response = client.get("/tasks")
    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert ids == [first["id"], second["id"]]


def test_get_task(client):
    created = client.post("/tasks", json={"title": "Read"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Read"


def test_get_missing_task(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task 999 not found"


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Draft", "description": "notes"}).json()
    response = client.patch(
        f"/tasks/{created['id']}",
        json={"title": "Final", "description": "done", "completed": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Final"
    assert body["description"] == "done"
    assert body["completed"] is True

    fetched = client.get(f"/tasks/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Final"


def test_update_missing_task(client):
    response = client.patch("/tasks/999", json={"title": "Nope"})
    assert response.status_code == 404


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temp"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_missing_task(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_reject_non_positive_id(client):
    assert client.get("/tasks/0").status_code == 422
