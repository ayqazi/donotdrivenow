# For situations where the final silver transform table has the same common layout
#
# Enhancement: append-only gold fixture enable to notify and indicate when a fixture has been replaced. But not really
# needed for use-case. This would help us find situations where a mistake was made in the data source and an update was
# issued so we are able to tell between erroneous fixtures and corrected ones
from sqlalchemy import select

from donotdrivenow.orm import Fixture


def transform_final_common_format_fixtures(session, sport, transform1):
    with session.begin():
        for transform_fixture in transform1.fixtures:
            gold_fixture = session.execute(
                select(Fixture).where(Fixture.transform_fixture_id == transform_fixture.id)
            ).scalar()
            if gold_fixture is None:
                gold_fixture = Fixture(
                    transform_fixture_id=transform_fixture.id,
                    sport=sport,
                    home_team=transform_fixture.home_team,
                    away_team=transform_fixture.away_team,
                    start=transform_fixture.start,
                )
                session.add(gold_fixture)
                session.flush()
