import datetime
import os

from sqlmodel import SQLModel, Field, create_engine


class Fixture(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    sport: str
    home_team: str
    away_team: str
    start_time: datetime.datetime


db_uri = os.getenv("DB_URI", "postgresql+psycopg2://localhost/donotdrivenow_dev")
engine = create_engine(db_uri, echo=True)
SQLModel.metadata.create_all(engine)
