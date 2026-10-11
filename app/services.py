"""Task use cases."""

from app.models import Task, utcnow
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class TaskService:
    def __init__(self, tasks: TaskRepository) -> None:
        self.tasks = tasks

    def create_task(self, data: TaskCreate) -> Task:
        task = Task(title=data.title, description=data.description, completed=data.completed)
        return self.tasks.add(task)

    def list_tasks(self) -> list[Task]:
        return self.tasks.list_all()

    def get_task(self, task_id: int) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        changes = data.model_dump()
        for field, value in changes.items():
            setattr(task, field, value)
        task.updated_at = utcnow()
        return self.tasks.save(task)

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.tasks.delete(task)
