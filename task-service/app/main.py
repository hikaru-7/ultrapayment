import logging
import os
import uuid
import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from .database import get_db
from .models import Task
from .schemas import TaskCreate, TaskResponse, TaskUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-service")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")


app = FastAPI(title="Task Service")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s", request_id, request.method, request.url.path, response.status_code)
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


def check_user(user_id: int, request_id: str):
    try:
        response = httpx.get(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers={"X-Request-ID": request_id},
            timeout=2.0,
        )
    except httpx.TimeoutException:
        logger.error("request_id=%s user-service timeout", request_id)
        raise HTTPException(status_code=503, detail="User service timeout")
    except httpx.RequestError:
        logger.error("request_id=%s user-service unavailable", request_id)
        raise HTTPException(status_code=503, detail="User service unavailable")

    if response.status_code == 404:
        raise HTTPException(status_code=400, detail="User does not exist")
    if response.status_code >= 500:
        raise HTTPException(status_code=503, detail="User service error")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected response from user service")


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, request: Request, db: Session = Depends(get_db)):
    check_user(data.user_id, request.state.request_id)

    task = Task(
        title=data.title,
        description=data.description,
        completed=False,
        user_id=data.user_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    values = data.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
