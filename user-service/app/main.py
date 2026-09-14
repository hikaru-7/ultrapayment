import logging
import uuid
from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .schemas import UserCreate, UserResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user-service")

app = FastAPI(title="User Service")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_id=%s method=%s path=%s status=%s", request_id, request.method, request.url.path, response.status_code)
    return response


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = User(name=data.name, email=data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
