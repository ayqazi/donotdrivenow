#!/usr/bin/env python3
import csv
import re
import sys
from datetime import datetime, timezone
from io import StringIO
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.grab import grab_simple_source
from donotdrivenow.orm import Ingest, FootballDataCoUkFixture, FootballDataCoUkTransform1, Fixture

CODE_VERSION = "2024021101"  # Format: YYYYMMDDNN where NN is a 0-padded number


# https://www.football-data.co.uk/matches.php
# Updates Tuesday at 13:00 UK time and Friday at 17:00 UK time
def grab_uk_football_fixtures(session):
    return grab_simple_source(name='football-data.co.uk',
                              url='https://www.football-data.co.uk/fixtures.csv',
                              content_type='text/csv',
                              session=session)


def ingest_uk_football_fixtures(session, grab):
    with session.begin():
        ingest = session.scalar(select(Ingest).where(Ingest.grab_id == grab.id))
        if ingest is None:
            print("football-data.co.uk: initiating ingestion", file=sys.stderr)
            ingested_data = []
            for row in csv.DictReader(StringIO(grab.data), delimiter=','):
                ingested_data.append(row)
            ingest = Ingest(grab=grab, ingested=datetime.now(timezone.utc), data=ingested_data)
            session.add(ingest)
            session.flush()
        else:
            print("football-data.co.uk: already ingested", file=sys.stderr)
    return ingest


def fixture_start_datetime_utc(ingested_fixture):
    dateparts = ingested_fixture['Date'].split('/')
    timeparts = ingested_fixture['Time'].split(':')

    uktime = datetime(day=int(dateparts[0]), month=int(dateparts[1]), year=int(dateparts[2]),
                      hour=int(timeparts[0]), minute=int(timeparts[1]),
                      tzinfo=ZoneInfo('Europe/London'))
    utctime = uktime.astimezone(ZoneInfo('UTC'))

    return utctime


def fixture_division_league(ingested_fixture):
    match = re.compile(r'\A([A-Z]{1,2})([0-9A-Z])\Z').match(ingested_fixture['Div'])
    assert match, f'"{ingested_fixture["Div"]}" not valid'
    return match.group(1), match.group(2)


# If the ingested fixture already has a transformation step for this code version, don't repeat it. But re-transform if
# the code version was bumped up even if all the data is the same.
def transform_stage1_uk_football_fixtures(session, ingest):
    with session.begin():
        t1 = session.execute(
            select(FootballDataCoUkTransform1)
            .where(FootballDataCoUkTransform1.ingest_id == ingest.id)
            .where(FootballDataCoUkTransform1.code_version == CODE_VERSION)
            .where(FootballDataCoUkTransform1.complete_success == True)  # noqa
        ).scalar()
        if t1 is None:
            print('No transform1 found for this code version and ingest - transforming', file=sys.stderr)
        else:
            print('Transform already exists', file=sys.stderr)
            return t1

        t1 = FootballDataCoUkTransform1(ingest=ingest,
                                        code_version=CODE_VERSION)
        session.add(t1)

        for index, ingested_fixture in enumerate(ingest.data):
            start = fixture_start_datetime_utc(ingested_fixture)
            league, division = fixture_division_league(ingested_fixture)
            t1_fixture = FootballDataCoUkFixture(
                transform=t1,
                league=league,
                division=division,
                start=start,
                home_team=ingested_fixture['HomeTeam'],
                away_team=ingested_fixture['AwayTeam'],
            )
            session.add(t1_fixture)
        t1.completed = datetime.now(timezone.utc)
        t1.complete_success = True
        session.add(t1)
        session.flush()

        return t1


# Enhancement: append-only gold fixture enable to notify and indicate when a fixture has been replaced. But not really
# needed for use-case. This would help us find situations where a mistake was made in the data source and an update was
# issued so we are able to tell between erroneous fixtures and corrected ones
def transform_final_uk_football_fixtures(session, transform1):
    with session.begin():
        for transform_fixture in transform1.fixtures:
            gold_fixture = session.execute(
                select(Fixture).where(Fixture.transform_fixture_id == transform_fixture.id)
            ).scalar()
            if gold_fixture is None:
                gold_fixture = Fixture(
                    transform_fixture_id=transform_fixture.id,
                    sport='football',
                    home_team=transform_fixture.home_team,
                    away_team=transform_fixture.away_team,
                    start=transform_fixture.start,
                )
                session.add(gold_fixture)
                session.flush()


def process_all():
    engine = boot()

    with Session(engine) as session:
        grab = grab_uk_football_fixtures(session)
        ingest = ingest_uk_football_fixtures(session, grab)
        transform1 = transform_stage1_uk_football_fixtures(session, ingest)
        transform_final_uk_football_fixtures(session, transform1)
        session.commit()


if __name__ == "__main__":
    process_all()
