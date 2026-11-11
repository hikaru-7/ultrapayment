# Ultrapayment

Учебный backend-проект для практики, построенный на микросервисной архитектуре с использованием FastAPI, PostgreSQL, SQLAlchemy, Alembic и Docker.

## Сервисы

Проект состоит из трех FastAPI-сервисов:

- `user-service` — работа с пользователями
- `task-service` — работа с задачами
- `payment-service` — работа с платежами

У каждого сервиса своя PostgreSQL база данных.

`task-service` не обращается напрямую к базе пользователей. Для проверки пользователя он отправляет HTTP-запрос в `user-service`.

`payment-service` работает со своей базой данных и содержит отдельную бизнес-логику для платежей, транзакций и конкурентного доступа.

## Архитектура

```text
                         Клиент
                           |
              +------------+------------+
              |            |            |
              v            v            v
        user-service  task-service  payment-service
              |            |            |
              |            |            |
              v            v            v
           user-db       task-db     payment-db

                           |
task-service --------------+
          HTTP request
          to user-service
```

## Структура сервисов

Сервисы разделены на несколько слоев:

```text
api/
    HTTP endpoints

services/
    бизнес-логика

repositories/
    работа с базой данных

models/
    SQLAlchemy модели

schemas/
    Pydantic схемы

db/
    подключение к PostgreSQL
```

Такое разделение позволяет держать HTTP-логику, бизнес-логику и работу с базой данных отдельно друг от друга.

## Payment Service

`payment-service` реализует работу с платежами.

Основные возможности:

- создание платежей
- получение платежа по ID
- получение списка платежей с pagination
- валидация суммы платежа
- валидация валюты
- хранение суммы через `Decimal`
- PostgreSQL constraints
- Alembic migrations
- создание `PaymentAttempt`
- транзакции
- rollback при ошибках
- конкурентное обновление платежей
- PostgreSQL row-level locking

### Payment transaction

Создание `Payment` и `PaymentAttempt` выполняется в рамках одной транзакции.

Упрощенно:

```text
BEGIN

create Payment
create PaymentAttempt

COMMIT
```

Если между операциями возникает ошибка:

```text
BEGIN

create Payment
ERROR

ROLLBACK
```

В результате в базе не остается частично выполненной операции.

Подробнее:

```text
docs/transactions.md
```

## Concurrency

В проекте есть тест конкурентного обновления одного платежа из двух Python threads.

Оба потока работают с одной записью, но используется PostgreSQL:

```sql
SELECT ... FOR UPDATE
```

Первый поток получает row-level lock.

Второй поток пытается получить тот же lock и ждет завершения первой транзакции.

Пример:

```text
Initial amount: 100.00

Process 1:
100.00 -> 110.00
COMMIT

Process 2:
waits for Process 1
110.00 -> 120.00
COMMIT

Final amount: 120.00
```

Это предотвращает проблему `lost update`.

## Transactions and locking

Основные используемые механизмы:

- `BEGIN`
- `COMMIT`
- `ROLLBACK`
- `SELECT ... FOR UPDATE`
- PostgreSQL `READ COMMITTED`
- pessimistic locking
- row-level locks

Проект также использовался для практического изучения deadlock-сценариев между двумя PostgreSQL transactions.

## Docker

Проект можно запустить через Docker Compose:

```bash
docker compose up -d --build
```

Проверить контейнеры:

```bash
docker compose ps
```

Основные сервисы доступны локально:

```text
task-service     http://localhost:8000
user-service     http://localhost:8001
payment-service  http://localhost:8002
```

PostgreSQL:

```text
user-db     localhost:5433
task-db     localhost:5434
payment-db  localhost:5435
```

## Payment database

Для локального подключения к `payment-db`:

```text
Host: localhost
Port: 5435
Database: payments
Username: postgres
Password: postgres
```

Например, базу можно открыть через pgAdmin.

Основные таблицы:

```text
payments
payment_attempts
alembic_version
```

## Tests

Тесты `payment-service`:

```bash
docker compose exec payment-service python -m pytest -v
```

На текущей версии:

```text
6 passed
```

Отдельный concurrency-тест:

```bash
docker compose exec payment-service python -m pytest tests/test_transactions.py::test_concurrent_payment_update -s -v
```

Пример результата:

```text
Process 1 locked payment. Amount: 100.00
Process 2 is trying to lock the same payment...
Process 2 is blocked by Process 1
Process 1 committed. Amount: 110.00
Process 2 got the lock. Amount: 110.00
Process 2 committed. Amount: 120.00

PASSED
```

## Code quality

Проверка Ruff:

```bash
docker compose exec payment-service ruff check src tests
```

## Database migrations

Для управления структурой базы данных используется Alembic.

Миграции `payment-service` находятся в:

```text
payment-service/alembic/versions/
```

Они включают:

- создание таблицы `payments`
- создание таблицы `payment_attempts`
- изменение типа суммы платежа
- ограничения для суммы платежа

## Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Docker
- Docker Compose
- pytest
- Ruff

## Current version

Current release:

```text
v1.1.0
```

Основные изменения относительно `v1.0.0`:

- добавлен `payment-service`
- добавлена отдельная payment database
- добавлены Alembic migrations
- добавлены payment validation и pagination
- добавлен `PaymentAttempt`
- добавлены транзакции и rollback
- добавлены concurrency tests
- добавлен PostgreSQL row-level locking
- переработана структура `task-service`