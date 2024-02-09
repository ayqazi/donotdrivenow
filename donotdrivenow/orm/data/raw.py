from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from donotdrivenow.orm import Id, Timestamps, Base


class DataSource(Base, Id, Timestamps):
    __tablename__ = "data_source"

    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str]


class Grab(Id, Timestamps, Base):
    __tablename__ = "grab"

    data_source_id: Mapped[int] = mapped_column(ForeignKey("data_source.id"))
