from litestar import get, Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException

from app.models import DriveNowFixture, provide_fixture_repository, FixtureRepository


class DriveNowController(Controller):
    path = "/drive_now"

    dependencies = {"fixture_repo": Provide(provide_fixture_repository)}

    @get("/")
    async def get_drive_now(self, fixture_repo: FixtureRepository) -> DriveNowFixture:
        fixture = await fixture_repo.get_one_or_none()
        if fixture is None:
            raise NotFoundException("No fixture was found")

        return DriveNowFixture(
            answer=False,
            location=fixture.location.name,
            start_time=fixture.start_time,
            sport=fixture.sport,
            home_team=fixture.home_team,
        )
