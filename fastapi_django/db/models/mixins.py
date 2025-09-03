from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import declarative_mixin, Mapped, mapped_column


@declarative_mixin
class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )


@declarative_mixin
class UpdatedAtMixin:
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
