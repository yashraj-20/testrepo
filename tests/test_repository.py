"""Direct tests for TaskRepository."""

import pytest
from sqlalchemy.orm import sessionmaker

from app.database import Base, create_db_engine
from app.models import Task
from app.repositories import TaskRepository


@pytest.fixture
def repo():
    engine = create_db_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = factory()
    try:
        yield TaskRepository(session)
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_get_missing_returns_none(repo):
    assert repo.get(1) is None


def test_add_then_list_in_id_order(repo):
    first = repo.add(Task(title="First", description=None, completed=False))
    second = repo.add(Task(title="Second", description="notes", completed=True))
    tasks = repo.list_all()
    assert [task.id for task in tasks] == [first.id, second.id]
    assert tasks[0].completed is False
    assert tasks[1].description == "notes"
    assert tasks[1].completed is True


def test_save_persists_field_changes(repo):
    task = repo.add(Task(title="Old", description="keep", completed=False))
    task.title = "New"
    saved = repo.save(task)
    assert saved.title == "New"
    fetched = repo.get(task.id)
    assert fetched is not None
    assert fetched.title == "New"
    assert fetched.description == "keep"


def test_delete_removes_the_row(repo):
    task = repo.add(Task(title="Temp", description=None, completed=False))
    repo.delete(task)
    assert repo.get(task.id) is None
    assert repo.list_all() == []
