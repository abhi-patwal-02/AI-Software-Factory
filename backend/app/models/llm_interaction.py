from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.project import Base


class LLMInteraction(Base):
    __tablename__ = "llm_interactions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False
    )

    agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("agents.id"),
        nullable=True
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    system_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    input_context: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    raw_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    parsed_decision: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success"
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    input_tokens: Mapped[int | None] = mapped_column(
        nullable=True
    )

    output_tokens: Mapped[int | None] = mapped_column(
        nullable=True
    )

    latency_ms: Mapped[int | None] = mapped_column(
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )