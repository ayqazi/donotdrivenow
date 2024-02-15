import json
import sys
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.grab import grab_simple_source
from donotdrivenow.orm import Ingest

CODE_VERSION = "2024021501"  # Format: YYYYMMDDNN where NN is a 0-padded number


# JSON file available from https://fixturedownload.com/feed/json/premiership-rugby-2023
# Updated once a day
def grab_uk_premier_league_fixtures(session):
    return grab_simple_source(name='rugbyunion-premiership-2023-fixturedownload.com',
                              url='https://fixturedownload.com/feed/json/premiership-rugby-2023',
                              content_type='application/json',
                              session=session)


def ingest_uk_premier_league_fixtures(session, grab):
    with session.begin():
        ingest = session.scalar(select(Ingest).where(Ingest.grab_id == grab.id))
        if ingest is None:
            print(f'{grab.data_source.name}: initiating ingestion', file=sys.stderr)
            ingested_data = json.loads(grab.data)
            ingest = Ingest(grab=grab, ingested=datetime.now(timezone.utc), data=ingested_data)
            session.add(ingest)
            session.flush()
        else:
            print(f'{grab.data_source.name}: already ingested', file=sys.stderr)
    return ingest


def process_all():
    engine = boot()

    with Session(engine) as session:
        grab = grab_uk_premier_league_fixtures(session)
        _ingest = ingest_uk_premier_league_fixtures(session, grab)
        # transform1 = ...(session, ingest)
        # ...(session, transform1)
        session.commit()


if __name__ == "__main__":
    process_all()
