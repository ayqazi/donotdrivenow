import datetime
import os

from sqlmodel import SQLModel, Field, create_engine, Relationship, Session, Column, DateTime


class Location(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name: str = Field(nullable=False, unique=True)
    fixtures: list["Fixture"] = Relationship(back_populates="location")


class Fixture(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    sport: str
    home_team: str
    away_team: str
    location_id: int = Field(foreign_key="location.id")
    location: Location = Relationship(back_populates="fixtures")
    start_time: datetime.datetime = Field(sa_column=Column(DateTime(timezone=True)))


engine = None


def init_db(db_uri="postgresql+psycopg2://localhost/donotdrivenow_dev", create_all=False):
    global engine

    if engine is not None:
        return engine

    db_uri = os.getenv("DB_URI", db_uri)
    engine = create_engine(db_uri, echo=True)
    if create_all:
        SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    with Session(engine) as s:
        yield s
