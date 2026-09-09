# Task / User services

Учебный проект перед практикой.

Два FastAPI сервиса:
- user-service — пользователи
- task-service — задачи

У каждого сервиса своя PostgreSQL база.
Task-service проверяет пользователя через HTTP запрос в user-service.

## Запуск

```bash
docker compose up --build
```

После запуска:
- user-service: http://localhost:8001/docs
- task-service: http://localhost:8000/docs

## Пример

1. Создать пользователя через `POST /users`
2. Создать задачу через `POST /tasks` с `user_id`
3. Получить задачу через `GET /tasks/{id}`

## Что я здесь изучал

- FastAPI
- HTTP методы и статусы
- PostgreSQL
- SQLAlchemy ORM
- Docker / Docker Compose
- HTTPX для общения сервисов
- обработку connection error / timeout
- простые логи
- request id
- pytest
