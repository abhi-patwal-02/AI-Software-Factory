from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.project import Base


class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        primary_key=True
    )

    depends_on_task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        primary_key=True
    )