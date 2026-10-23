FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
COPY app ./app
COPY tests ./tests
COPY alembic.ini .
COPY alembic ./alembic

RUN pip install -r requirements.txt

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]