#!/usr/bin/env python3

import sys
from datetime import datetime, timezone

import requests
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.orm.data.raw import DataSource, Grab


# https://www.football-data.co.uk/matches.php
# Updates Tuesday at 13:00 UK time and Friday at 17:00 UK time
def grab_england_football_fixtures(session):
    with (session.begin()):
        source = session.execute(select(DataSource).where(DataSource.name == 'football-data.co.uk')).scalar()
        now = datetime.now(timezone.utc)

        if source is None:
            source = DataSource(name='football-data.co.uk',
                                url='https://www.football-data.co.uk/fixtures.csv')
            session.add(source)
            session.flush()

        existing_grab = session.execute(select(Grab).where(Grab.data_source_id == source.id)
                                        .where(text("grabbed::date = now()::date"))).scalar()
        if (existing_grab is not None and
                existing_grab.grabbed.year == now.year and
                existing_grab.grabbed.month == now.month and
                existing_grab.grabbed.day == now.day):
            print(f"{source.name}: already grabbed today", file=sys.stderr)
        else:
            print(f"{source.name}: grabbing for today", file=sys.stderr)
            rawdata = requests.get('https://www.football-data.co.uk/fixtures.csv').text

            grab = Grab(data_source_id=source.id,
                        grabbed=now,
                        data=rawdata,
                        content_type="text/csv")
            session.add(grab)
            session.flush()


def grab_all():
    engine = boot()

    with Session(engine) as session:
        grab_england_football_fixtures(session)


if __name__ == "__main__":
    grab_all()
