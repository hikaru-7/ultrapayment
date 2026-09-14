from sqlalchemy.orm import Session

from ..models.task import Task


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        title: str,
        description: str | None,
        user_id: int,
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            completed=False,
            user_id=user_id,
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def list_all(self) -> list[Task]:
        return self.db.query(Task).all()

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def update(self, task: Task, values: dict) -> Task:
        for key, value in values.items():
            setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)

        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()