import logging
import uuid

from fastapi import FastAPI, Request

from .api.tasks import router as tasks_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-service")


app = FastAPI(title="Task Service")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_id=%s method=%s path=%s status=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )

    return response


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(tasks_router) 