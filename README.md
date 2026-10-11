# Task API

Small task tracker used as the base for this repository. It is a JSON API: create, list, fetch, update, and delete tasks. Data is stored in SQLite through SQLAlchemy.

## Requirements

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The server listens on `http://127.0.0.1:8000`. Interactive docs are at `/docs`.

On startup the app creates the `tasks` table if it does not exist. The default database file is `./tasks.db`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `TASK_APP_NAME` | `Task API` | Application title shown in the docs |
| `TASK_DATABASE_URL` | `sqlite:///./tasks.db` | SQLAlchemy database URL |

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List tasks, oldest id first |
| `GET` | `/tasks/{id}` | Fetch one task |
| `PATCH` | `/tasks/{id}` | Update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

Create body:

```json
{"title": "Buy milk", "description": "2%", "completed": false}
```

`title` is required (1–200 characters). `description` is optional. `completed` defaults to `false`. Unknown tasks return `404` with `{"detail": "Task {id} not found"}`.

## Tests

```bash
pytest
```

Tests use a fresh in-memory SQLite database per test and do not write `tasks.db`.

## Layout

```
app/config.py          environment settings
app/database.py        engine, session, declarative base
app/models.py          Task table
app/schemas.py         Pydantic request and response models
app/services.py        create, list, get, update, delete
app/routers/tasks.py   HTTP routes
app/main.py            FastAPI app
tests/                 pytest suite
```
