import logging
import os
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from typing import List

from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import autocommit_before_send_handler
from litestar import get, Litestar, status_codes
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.exceptions import NotFoundException, ClientException
from litestar.logging import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from sqlalchemy import select, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    fixtures: Mapped[List["Fixture"]] = relationship(back_populates="location")


class Fixture(Base):
    __tablename__ = "fixture"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport: Mapped[str]
    home_team: Mapped[str]
    away_team: Mapped[str]
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    location: Mapped["Location"] = relationship(back_populates="fixtures", lazy="selectin")
    start_time: Mapped[datetime]


async def provide_session(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@dataclass
class DriveNowFixture:
    answer: bool
    location: str
    start_time: datetime
    sport: str
    home_team: str


@get("/drive_now")
async def get_drive_now(session: AsyncSession) -> DriveNowFixture:
    result = await session.execute(
        select(Fixture)
        .join(Location)
        .where(Location.id == Fixture.location_id)
    )
    fixture = result.scalar_one_or_none()
    if fixture is None:
        raise NotFoundException("No fixture was found")

    return DriveNowFixture(
        answer=False,
        location=fixture.location.name,
        start_time=fixture.start_time,
        sport=fixture.sport,
        home_team=fixture.home_team,
    )


@get("/latest_fixture")
async def get_latest_fixture(session: AsyncSession) -> Fixture:
    result = await session.execute(select(Fixture))
    fixture = result.scalar_one_or_none()
    if fixture is None:
        raise NotFoundException("No fixture was found")
    return fixture


DB_CONFIG = SQLAlchemyAsyncConfig(
    connection_string=os.getenv("DB_URI", "postgresql+asyncpg://localhost/donotdrivenow_dev"),
    metadata=Base.metadata,
    create_all=True,
    before_send_handler=autocommit_before_send_handler,
)

LOGGING_CONFIG = LoggingConfig(
    root={"level": logging.getLevelName(logging.DEBUG), "handlers": ["console"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
)
LOGGING_MIDDLEWARE_CONFIG = LoggingMiddlewareConfig()

APPLICATION = Litestar(
    [get_drive_now, get_latest_fixture],
    dependencies={"session": provide_session},
    logging_config=LOGGING_CONFIG,
    middleware=[LOGGING_MIDDLEWARE_CONFIG.middleware],
    plugins=[
        SQLAlchemyPlugin(DB_CONFIG),
    ],
)
