"""Task CRUD routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TaskCreate, TaskPage, TaskRead, TaskUpdate
from app.services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

DbSession = Annotated[Session, Depends(get_db)]
TaskId = Annotated[int, Path(ge=1)]
CompletedFilter = Annotated[bool | None, Query()]
PageLimit = Annotated[int, Query(ge=1, le=100)]
PageOffset = Annotated[int, Query(ge=0)]


def get_task_service(db: DbSession) -> TaskService:
    return TaskService(db)


TaskSvc = Annotated[TaskService, Depends(get_task_service)]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary="Create a task")
def create_task(data: TaskCreate, service: TaskSvc) -> TaskRead:
    return service.create_task(data)


@router.get("", response_model=TaskPage, summary="List tasks")
def list_tasks(
    service: TaskSvc,
    completed: CompletedFilter = None,
    limit: PageLimit = 20,
    offset: PageOffset = 0,
) -> TaskPage:
    items, total = service.list_tasks(completed=completed, limit=limit, offset=offset)
    return TaskPage(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a task",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Task not found"}},
)
def get_task(task_id: TaskId, service: TaskSvc) -> TaskRead:
    return service.get_task(task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Task not found"}},
)
def update_task(task_id: TaskId, data: TaskUpdate, service: TaskSvc) -> TaskRead:
    return service.update_task(task_id, data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Task not found"}},
)
def delete_task(task_id: TaskId, service: TaskSvc) -> Response:
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
