import os


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/tasks",
)

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://localhost:8001",
)

USER_SERVICE_TIMEOUT = float(
    os.getenv("USER_SERVICE_TIMEOUT", "2.0")
)