import sys
from datetime import datetime, timezone

import requests
from sqlalchemy import select, text

from donotdrivenow.orm import DataSource, Grab


def grab_simple_source(name, url, content_type, session):
    with session.begin():
        source = session.execute(select(DataSource).where(DataSource.name == 'football-data.co.uk')).scalar()
        now = datetime.now(timezone.utc)

        if source is None:
            source = DataSource(name=name, url=url)
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
            rawdata = requests.get(source.url).text

            grab = Grab(data_source_id=source.id,
                        grabbed=now,
                        data=rawdata,
                        content_type=content_type)
            session.add(grab)
            session.flush()
            session.commit()

    return grab
