from datetime import datetime
from typing import List
from uuid import UUID

import sqlalchemy
from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from donotdrivenow.orm import Id, Timestamps, Base


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
