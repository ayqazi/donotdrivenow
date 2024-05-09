import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import List

from litestar import get, Litestar, status_codes
from litestar.contrib.sqlalchemy.plugins import SQLAlchemySerializationPlugin
from litestar.datastructures import State
from litestar.exceptions import NotFoundException, ClientException
from litestar.logging import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from sqlalchemy import select, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


@dataclass
class DriveNow:
    answer: bool
    location: str
    start_time: datetime
    sport: str
    home_team: str


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


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None:
        db_uri = os.getenv("DB_URI", "postgresql+asyncpg://localhost/donotdrivenow_dev")
        engine = create_async_engine(url=db_uri, echo=True)
        app.state.engine = engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        await engine.dispose()


SESSION_MAKER = async_sessionmaker(expire_on_commit=False)


async def provide_session(state: State) -> AsyncGenerator[AsyncSession, None]:
    async with SESSION_MAKER(bind=state.engine) as session:
        try:
            async with session.begin():
                yield session
        except IntegrityError as exc:
            raise ClientException(
                status_code=status_codes.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc


@get("/drive_now")
async def get_drive_now(session: AsyncSession) -> DriveNow:
    result = await session.execute(select(Fixture))
    fixture = result.scalar_one_or_none()
    if fixture is None:
        raise NotFoundException("No fixture was found")

    return DriveNow(
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
    lifespan=[db_connection],
    logging_config=LOGGING_CONFIG,
    middleware=[LOGGING_MIDDLEWARE_CONFIG.middleware],
    plugins=[SQLAlchemySerializationPlugin()],
)
