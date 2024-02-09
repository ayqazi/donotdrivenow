from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from donotdrivenow.orm import Id, Timestamps, Base


class DataSource(Base, Id, Timestamps):
    __tablename__ = "data_source"

    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]


class Grab(Base, Id, Timestamps):
    __tablename__ = "grab"

    data_source_id: Mapped[UUID] = mapped_column(ForeignKey("data_source.id"))
    grabbed: Mapped[datetime]
    data: Mapped[str]
    content_type: Mapped[str]
