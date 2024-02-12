#!/usr/bin/env python3
import csv
import re
import sys
from datetime import datetime, timezone
from io import StringIO
from zoneinfo import ZoneInfo

import requests
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.orm import DataSource, Grab, Ingest, FootballDataCoUkFixture

CODE_VERSION = "2024021101"  # Format: YYYYMMDDNN where NN is a 0-padded number


# https://www.football-data.co.uk/matches.php
# Updates Tuesday at 13:00 UK time and Friday at 17:00 UK time
def grab_uk_football_fixtures(session):
    with session.begin():
        source = session.execute(select(DataSource).where(DataSource.name == 'football-data.co.uk')).scalar()
        now = datetime.now(timezone.utc)

        if source is None:
            source = DataSource(name='football-data.co.uk',
                                url='https://www.football-data.co.uk/fixtures.csv')
            session.add(source)
            session.flush()

        grab = session.execute(select(Grab).where(Grab.data_source_id == source.id)
                               .where(text("grabbed::date = now()::date"))).scalar()
        if (grab is not None and
                grab.grabbed.year == now.year and
                grab.grabbed.month == now.month and
                grab.grabbed.day == now.day):
            print(f"{source.name}: already grabbed today", file=sys.stderr)
        else:
            print(f"{source.name}: initiating grab", file=sys.stderr)
            rawdata = requests.get('https://www.football-data.co.uk/fixtures.csv').text

            grab = Grab(data_source_id=source.id,
                        grabbed=now,
                        data=rawdata,
                        content_type="text/csv")
            session.add(grab)
            session.flush()
            session.commit()

    return grab


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
        for index, ingested_fixture in enumerate(ingest.data):
            starting = fixture_start_datetime_utc(ingested_fixture)
            league, division = fixture_division_league(ingested_fixture)
            t1_fixture = session.execute(
                select(FootballDataCoUkFixture)
                .where(FootballDataCoUkFixture.ingest_id == ingest.id)
                .where(FootballDataCoUkFixture.code_version == CODE_VERSION)
                .where(FootballDataCoUkFixture.home_team == ingested_fixture['HomeTeam'])
                .where(FootballDataCoUkFixture.away_team == ingested_fixture['AwayTeam'])
            ).scalar()
            if t1_fixture is None:
                t1_fixture = FootballDataCoUkFixture(
                    ingest=ingest,
                    transformed=datetime.now(timezone.utc),
                    code_version=CODE_VERSION,
                    league=league,
                    division=division,
                    starting=starting,
                    home_team=ingested_fixture['HomeTeam'],
                    away_team=ingested_fixture['AwayTeam'],
                )
                session.add(t1_fixture)

        session.flush()


def process_all():
    engine = boot()

    with Session(engine) as session:
        grab = grab_uk_football_fixtures(session)
        ingest = ingest_uk_football_fixtures(session, grab)
        transform_stage1_uk_football_fixtures(session, ingest)
        session.commit()


if __name__ == "__main__":
    process_all()
