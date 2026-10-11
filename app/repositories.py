"""Persistence for tasks."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    """SQLAlchemy access for the tasks table.

    Methods that change rows commit the session. Callers apply business rules
    before ``save``.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def list_all(self) -> list[Task]:
        statement = select(Task).order_by(Task.id)
        return list(self.db.scalars(statement).all())

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def save(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task
