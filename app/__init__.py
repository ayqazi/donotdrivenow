import logging
from collections.abc import AsyncGenerator

from litestar import Litestar, status_codes
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from litestar.exceptions import ClientException
from litestar.logging import LoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.drive_now import DriveNowController
from app.controllers.root import RootController
from app.models import DB_CONFIG, Fixture, Location


async def provide_session(db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session
    except IntegrityError as exc:
        raise ClientException(
            status_code=status_codes.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


LOGGING_CONFIG = LoggingConfig(
    root={"level": logging.getLevelName(logging.DEBUG), "handlers": ["console"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
)
LOGGING_MIDDLEWARE_CONFIG = LoggingMiddlewareConfig()

APPLICATION = Litestar(
    [DriveNowController, RootController],
    dependencies={"session": provide_session},
    logging_config=LOGGING_CONFIG,
    middleware=[LOGGING_MIDDLEWARE_CONFIG.middleware],
    plugins=[
        SQLAlchemyPlugin(DB_CONFIG),
    ],
)
