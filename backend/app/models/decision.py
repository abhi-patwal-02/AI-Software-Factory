from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.project import Base


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    decision: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    decision_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    made_by_agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )