from datetime import datetime, UTC

from litestar import get, post, Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Fixture, Location, provide_fixture_repository, FixtureRepository


class RootController(Controller):
    path = "/"

    dependencies = {"fixture_repo": Provide(provide_fixture_repository)}

    @post("/test_data")
    async def post_test_data(self, session: AsyncSession) -> dict:
        query = await session.execute(select(Location).where(Location.name == "Test City"))
        location = query.scalar()
        if location is None:
            location = Location(name="Test City")
            session.add(location)

        query = await session.execute(select(Fixture).where(
            (Fixture.location == location) &
            (Fixture.home_team == "Team 1") &
            (Fixture.away_team == "Team 2")
        ))
        fixture = query.scalar()

        if fixture is None:
            fixture = Fixture(
                location=location,
                sport="football",
                home_team="Team 1",
                away_team="Team 2",
                start_time=datetime.now(tz=UTC),
            )
            session.add(fixture)

        await session.commit()
        return {"status": "ok"}

    @get("/latest_fixture")
    async def get_latest_fixture(self, fixture_repo: FixtureRepository) -> Fixture:
        fixture = await fixture_repo.get_one_or_none()
        if fixture is None:
            raise NotFoundException("No fixture was found")
        return fixture
