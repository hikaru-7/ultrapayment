from ..clients.user_client import UserClient
from ..models.task import Task
from ..repositories.task_repository import TaskRepository
from ..schemas.task import TaskCreate, TaskUpdate


class TaskNotFoundError(Exception):
    pass


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        user_client: UserClient,
    ):
        self.repository = repository
        self.user_client = user_client

    def create_task(
        self,
        data: TaskCreate,
        request_id: str,
    ) -> Task:
        self.user_client.ensure_user_exists(
            user_id=data.user_id,
            request_id=request_id,
        )

        return self.repository.create(
            title=data.title,
            description=data.description,
            user_id=data.user_id,
        )

    def list_tasks(self) -> list[Task]:
        return self.repository.list_all()

    def get_task(self, task_id: int) -> Task:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        return task

    def update_task(
        self,
        task_id: int,
        data: TaskUpdate,
    ) -> Task:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        values = data.model_dump(exclude_unset=True)

        return self.repository.update(
            task=task,
            values=values,
        )

    def delete_task(self, task_id: int) -> None:
        task = self.repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError()

        self.repository.delete(task)
