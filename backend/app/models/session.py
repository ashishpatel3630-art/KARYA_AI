import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    refresh_token_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    # Unique ID of this exact refresh token
    jti: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
    )

    # Identifies the complete refresh-token chain
    token_family: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    parent_jti: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    absolute_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="sessions",
    )