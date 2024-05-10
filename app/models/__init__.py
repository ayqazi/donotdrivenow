import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

from advanced_alchemy import SQLAlchemyAsyncRepository
from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.config import EngineConfig
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import autocommit_before_send_handler
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload


class Location(UUIDAuditBase):
    __tablename__ = "location"

    name: Mapped[str] = mapped_column(unique=True)
    fixtures: Mapped[List["Fixture"]] = relationship(back_populates="location")


class Fixture(UUIDAuditBase):
    __tablename__ = "fixture"

    sport: Mapped[str]
    home_team: Mapped[str]
    away_team: Mapped[str]
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    location: Mapped["Location"] = relationship(back_populates="fixtures", lazy="selectin")
    start_time: Mapped[datetime]


class FixtureRepository(SQLAlchemyAsyncRepository[Fixture]):
    model_type = Fixture


async def provide_fixture_repository(db_session: AsyncSession) -> FixtureRepository:
    return FixtureRepository(
        session=db_session,
        statement=select(Fixture).options(selectinload(Fixture.location)),
    )


@dataclass
class DriveNowFixture:
    answer: bool
    location: str
    start_time: datetime
    sport: str
    home_team: str


DB_CONFIG = SQLAlchemyAsyncConfig(
    connection_string=os.getenv("DB_URI", "postgresql+asyncpg://localhost/donotdrivenow_dev"),
    metadata=UUIDAuditBase.metadata,
    create_all=True,
    before_send_handler=autocommit_before_send_handler,
    engine_config=EngineConfig(echo=True),
)
