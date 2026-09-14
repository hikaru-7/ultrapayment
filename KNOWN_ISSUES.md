# Known Issues

## 1. Duplicate user email returns HTTP 500

Creating a user with an email that already exists causes a PostgreSQL `UniqueViolation`.

Currently this error is not handled by the application and results in HTTP 500.

Expected behaviour:
- Return HTTP 409 Conflict
- Return a clear error message

## 2. HTTP 503 is not documented in Swagger

When `user-service` is unavailable, `task-service` correctly returns HTTP 503.

However, this response is not currently documented in the generated OpenAPI / Swagger documentation.

## 3. Test coverage is still basic

Current tests cover only basic service behaviour and some service-to-service failure scenarios.

More tests can be added for CRUD operations, database errors and validation.