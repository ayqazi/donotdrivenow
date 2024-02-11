#!/usr/bin/env python3
import csv
import sys
from datetime import datetime, timezone
from io import StringIO

import requests
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.orm import DataSource, Grab, Ingest


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
            for row in csv.reader(StringIO(grab.data), delimiter=','):
                ingested_data.append(row)
            ingest = Ingest(grab=grab, ingested=datetime.now(timezone.utc), data=ingested_data)
            session.add(ingest)
            session.flush()
        else:
            print("football-data.co.uk: already ingested", file=sys.stderr)
    return ingest


def process_all():
    engine = boot()

    with Session(engine) as session:
        grab = grab_uk_football_fixtures(session)
        ingest_uk_football_fixtures(session, grab)


if __name__ == "__main__":
    process_all()
