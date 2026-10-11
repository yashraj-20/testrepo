"""Task use cases."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Task, utcnow
from app.schemas import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_task(self, data: TaskCreate) -> Task:
        task = Task(title=data.title, description=data.description, completed=data.completed)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(self) -> list[Task]:
        statement = select(Task).order_by(Task.id)
        return list(self.db.scalars(statement).all())

    def get_task(self, task_id: int) -> Task:
        task = self.db.get(Task, task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        task.updated_at = utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.db.delete(task)
        self.db.commit()
