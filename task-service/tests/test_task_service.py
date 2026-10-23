from app.schemas.task import TaskCreate
from app.services.task_service import TaskService


class FakeUserClient:
    def __init__(self):
        self.checked_user_id = None

    def ensure_user_exists(
        self,
        user_id: int,
        request_id: str,
    ) -> None:
        self.checked_user_id = user_id


class FakeTaskRepository:
    def __init__(self):
        self.created_task = None

    def create(
        self,
        title: str,
        description: str | None,
        user_id: int,
    ):
        self.created_task = {
            "title": title,
            "description": description,
            "user_id": user_id,
        }

        return self.created_task


def test_create_task_checks_user_and_creates_task():
    repository = FakeTaskRepository()
    user_client = FakeUserClient()

    service = TaskService(
        repository=repository,
        user_client=user_client,
    )

    data = TaskCreate(
        title="Learn architecture",
        description="Week 1",
        user_id=5,
    )

    result = service.create_task(
        data=data,
        request_id="test-request-id",
    )

    assert user_client.checked_user_id == 5
    assert result["title"] == "Learn architecture"
    assert result["user_id"] == 5
