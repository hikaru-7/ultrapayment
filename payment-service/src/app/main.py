from fastapi import FastAPI

from .api.payments import router as payments_router

app = FastAPI(title="Payment Service")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(payments_router)