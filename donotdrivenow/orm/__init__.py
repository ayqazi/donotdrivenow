import uuid
from datetime import datetime, timezone
from typing import List
from uuid import UUID

import sqlalchemy.dialects.postgresql
import uuid6
from sqlalchemy import event, ForeignKey, Column, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


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


class DataSource(Base, Id, Timestamps):
    __tablename__ = "data_source"

    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]

    grabs: Mapped[List["Grab"]] = relationship(back_populates="data_source")


class Grab(Base, Id, Timestamps):
    __tablename__ = "grab"

    data_source_id: Mapped[UUID] = mapped_column(ForeignKey("data_source.id"))
    data_source: Mapped["DataSource"] = relationship(back_populates="grabs")
    grabbed: Mapped[datetime]
    data: Mapped[str]
    content_type: Mapped[str]

    ingests: Mapped[List["Ingest"]] = relationship(back_populates="grab")


class Ingest(Base, Id, Timestamps):
    __tablename__ = "ingest"

    grab_id: Mapped[UUID] = mapped_column(ForeignKey("grab.id"))
    grab: Mapped["Grab"] = relationship(back_populates="ingests")
    ingested: Mapped[datetime]
    data = Column(sqlalchemy.dialects.postgresql.JSONB)


# == Data source specific tables

class FootballDataCoUkFixture(Base, Id, Timestamps):
    __tablename__ = "football_data_co_uk_fixture"

    ingest_id: Mapped[UUID] = mapped_column(ForeignKey("ingest.id"))
    ingest: Mapped["Ingest"] = relationship()
    transformed: Mapped[datetime]
    code_version: Mapped[str]

    league: Mapped[str] = mapped_column(String(2))
    division: Mapped[str] = mapped_column(String(2))
    starting: Mapped[datetime]
    home_team: Mapped[str]
    away_team: Mapped[str]
