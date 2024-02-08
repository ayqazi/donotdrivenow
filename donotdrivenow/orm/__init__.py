from datetime import datetime, timezone

from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Id:
    id: Mapped[int] = mapped_column(primary_key=True)


class Timestamps:
    created: Mapped[datetime]
    modified: Mapped[datetime]


@event.listens_for(Timestamps, identifier='before_insert', propagate=True)
def timestamps_before_insert(_mapper, _connection, target):
    target.created = datetime.now(timezone.utc)
    target.modified = datetime.now(timezone.utc)


@event.listens_for(Timestamps, identifier='before_update', propagate=True)
def timestamps_before_insert(_mapper, _connection, target):
    target.modified = datetime.now(timezone.utc)
