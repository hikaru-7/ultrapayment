FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
COPY src ./src
COPY tests ./tests

RUN find src tests -type f -name "*.py" -exec chmod a-x {} +

COPY alembic.ini .
COPY alembic ./alembic

RUN pip install -r requirements.txt

ENV PYTHONPATH=/app/src

CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8002"]