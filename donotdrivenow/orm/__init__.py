import uuid
from datetime import datetime, timezone

import sqlalchemy.dialects.postgresql
import uuid6
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {
        str: sqlalchemy.dialects.postgresql.TEXT,
        uuid.UUID: sqlalchemy.dialects.postgresql.UUID(as_uuid=True),
        dict: sqlalchemy.dialects.postgresql.JSONB,
    }


class Id:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid6.uuid7)


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
