import json
import sys
from datetime import datetime, timezone, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.grab import grab_simple_source
from donotdrivenow.orm import Ingest, FixturedownloadComTransform1, FixturedownloadComFixture
from donotdrivenow.transform import transform_final_common_format_fixtures

CODE_VERSION = "2024021501"  # Format: YYYYMMDDNN where NN is a 0-padded number


# JSON file available from https://fixturedownload.com/feed/json/premiership-rugby-2023
# Updated once a day
def grab_uk_premiership_fixtures(session):
    return grab_simple_source(name='rugbyunion-uk-premiership-2023-fixturedownload.com',
                              url='https://fixturedownload.com/feed/json/premiership-rugby-2023',
                              content_type='application/json',
                              session=session)


def ingest_uk_premiership_fixtures(session, grab):
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


def transform_stage1_uk_premiership_fixtures(session, ingest):
    with session.begin():
        t1 = session.execute(
            select(FixturedownloadComTransform1)
            .where(FixturedownloadComTransform1.ingest_id == ingest.id)
            .where(FixturedownloadComTransform1.code_version == CODE_VERSION)
            .where(FixturedownloadComTransform1.complete_success == True)  # noqa
        ).scalar()
        if t1 is None:
            print(f'{ingest.grab.data_source.name}: No transform1 found for this code version and ingest - '
                  'transforming', file=sys.stderr)
        else:
            print(f'{ingest.grab.data_source.name}: Transform already exists', file=sys.stderr)
            return t1

        t1 = FixturedownloadComTransform1(ingest=ingest,
                                          code_version=CODE_VERSION)
        session.add(t1)

        for ingested_fixture in ingest.data:
            t1_fixture = FixturedownloadComFixture(
                transform=t1,
                start=datetime.fromisoformat(ingested_fixture['DateUtc']).astimezone(UTC),
                home_team=ingested_fixture['HomeTeam'],
                away_team=ingested_fixture['AwayTeam'],
            )
            session.add(t1_fixture)
        t1.completed = datetime.now(timezone.utc)
        t1.complete_success = True
        session.add(t1)
        session.flush()

        return t1


def process_all():
    engine = boot()

    with Session(engine) as session:
        grab = grab_uk_premiership_fixtures(session)
        ingest = ingest_uk_premiership_fixtures(session, grab)
        transform1 = transform_stage1_uk_premiership_fixtures(session, ingest)
        transform_final_common_format_fixtures(session, 'rugbyunion', transform1)
        session.commit()


if __name__ == "__main__":
    process_all()
