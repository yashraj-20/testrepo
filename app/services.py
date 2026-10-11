"""Task use cases."""

from sqlalchemy import func, select
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

    def list_tasks(
        self,
        *,
        completed: bool | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Task], int]:
        statement = select(Task)
        count_statement = select(func.count()).select_from(Task)
        if completed is not None:
            statement = statement.where(Task.completed == completed)
            count_statement = count_statement.where(Task.completed == completed)
        total = self.db.scalar(count_statement) or 0
        statement = statement.order_by(Task.id).offset(offset).limit(limit)
        return list(self.db.scalars(statement).all()), total

    def get_task(self, task_id: int) -> Task:
        task = self.db.get(Task, task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        changes = data.model_dump()
        for field, value in changes.items():
            setattr(task, field, value)
        task.updated_at = utcnow()
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.db.delete(task)
        self.db.commit()
