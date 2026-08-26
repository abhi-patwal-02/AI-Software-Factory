from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.project import Base


class ErrorAttempt(Base):
    __tablename__ = "error_attempts"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    error_id: Mapped[int] = mapped_column(
        ForeignKey("errors.id"),
        nullable=False
    )

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agents.id"),
        nullable=False
    )

    attempt_number: Mapped[int] = mapped_column(
        nullable=False
    )

    diagnosis: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    action_taken: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="in_progress"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )