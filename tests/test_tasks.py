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
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


def test_list_returns_tasks_in_id_order(client):
    first = client.post("/tasks", json={"title": "First"}).json()
    second = client.post("/tasks", json={"title": "Second"}).json()
    response = client.get("/tasks")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 20
    assert body["offset"] == 0
    ids = [item["id"] for item in body["items"]]
    assert ids == [first["id"], second["id"]]


def test_list_paginates(client):
    ids = []
    for index in range(5):
        created = client.post("/tasks", json={"title": f"Task {index}"}).json()
        ids.append(created["id"])

    first_page = client.get("/tasks", params={"limit": 2, "offset": 0})
    assert first_page.status_code == 200
    body = first_page.json()
    assert body["total"] == 5
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert [item["id"] for item in body["items"]] == ids[:2]

    last_page = client.get("/tasks", params={"limit": 2, "offset": 4})
    assert last_page.json()["total"] == 5
    assert [item["id"] for item in last_page.json()["items"]] == [ids[4]]

    past_end = client.get("/tasks", params={"limit": 2, "offset": 10})
    assert past_end.json()["items"] == []
    assert past_end.json()["total"] == 5


def test_list_filters_by_completed(client):
    client.post("/tasks", json={"title": "Open", "completed": False})
    done = client.post("/tasks", json={"title": "Done", "completed": True}).json()
    also_done = client.post("/tasks", json={"title": "Also done", "completed": True}).json()

    completed = client.get("/tasks", params={"completed": True, "limit": 1})
    assert completed.status_code == 200
    body = completed.json()
    assert body["total"] == 2
    assert body["limit"] == 1
    assert [item["id"] for item in body["items"]] == [done["id"]]

    rest = client.get("/tasks", params={"completed": True, "limit": 1, "offset": 1})
    assert [item["id"] for item in rest.json()["items"]] == [also_done["id"]]
    assert rest.json()["total"] == 2

    open_tasks = client.get("/tasks", params={"completed": False})
    assert open_tasks.json()["total"] == 1
    assert open_tasks.json()["items"][0]["title"] == "Open"


def test_list_rejects_invalid_paging(client):
    assert client.get("/tasks", params={"limit": 0}).status_code == 422
    assert client.get("/tasks", params={"limit": 101}).status_code == 422
    assert client.get("/tasks", params={"offset": -1}).status_code == 422


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
