import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False
    )

    version: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    image: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    commit_sha: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    target_environment: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    strategy: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="blue_green"
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )