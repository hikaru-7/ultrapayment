from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..clients.user_client import (
    UnexpectedUserServiceResponseError,
    UserNotFoundError,
    UserServiceError,
    UserServiceTimeoutError,
    UserServiceUnavailableError,
    UserClient,
)
from ..db.database import get_db
from ..repositories.task_repository import TaskRepository
from ..schemas.task import TaskCreate, TaskResponse, TaskUpdate
from ..services.task_service import TaskNotFoundError, TaskService


router = APIRouter()


def get_task_service(
    db: Session = Depends(get_db),
) -> TaskService:
    repository = TaskRepository(db)
    user_client = UserClient()

    return TaskService(
        repository=repository,
        user_client=user_client,
    )


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
)
def create_task(
    data: TaskCreate,
    request: Request,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.create_task(
            data=data,
            request_id=request.state.request_id,
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=400,
            detail="User does not exist",
        )
    except UserServiceTimeoutError:
        raise HTTPException(
            status_code=503,
            detail="User service timeout",
        )
    except UserServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="User service unavailable",
        )
    except UserServiceError:
        raise HTTPException(
            status_code=503,
            detail="User service error",
        )
    except UnexpectedUserServiceResponseError:
        raise HTTPException(
            status_code=502,
            detail="Unexpected response from user service",
        )


@router.get(
    "/tasks",
    response_model=list[TaskResponse],
)
def list_tasks(
    service: TaskService = Depends(get_task_service),
):
    return service.list_tasks()


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.get_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )


@router.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    try:
        return service.update_task(
            task_id=task_id,
            data=data,
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service),
):
    try:
        service.delete_task(task_id)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return Response(status_code=204) 