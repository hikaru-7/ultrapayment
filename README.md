# Task / User services

Учебный backend-проект для практики.

Проект состоит из двух FastAPI-сервисов:

- `user-service` — работа с пользователями
- `task-service` — работа с задачами

У каждого сервиса своя PostgreSQL база данных.

`task-service` не обращается напрямую к базе пользователей. Для проверки пользователя он отправляет HTTP-запрос в `user-service`.

## Архитектура

```text
Клиент
  |
  v
task-service ---> user-service
  |                  |
  v                  v
task-db            user-db
  v
task-service ---> user-service
  |                  |
  v                  v
task-db            user-db