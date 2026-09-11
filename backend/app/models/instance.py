import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Instance(Base):
    __tablename__ = "instances"

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

    deployment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deployments.id", ondelete="SET NULL"),
        nullable=True
    )

    environment: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    container_id: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    container_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    host_port: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    container_port: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    status: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )