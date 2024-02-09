from sqlalchemy import select
from sqlalchemy.orm import Session

from donotdrivenow import boot
from donotdrivenow.orm.data.raw import DataSource


# https://www.football-data.co.uk/matches.php
# Updates Tuesday at 13:00 UK time and Friday at 17:00 UK time
def fetch_england_football_fixtures(engine):
    session = Session(engine)

    with session.begin():
        source = session.execute(select(DataSource).where(DataSource.name == 'football-data.co.uk')).scalar()

        if source is None:
            source = DataSource(name='football-data.co.uk',
                                url='https://www.football-data.co.uk/fixtures.csv')
            session.add(source)

    raw = "a,b\n1,2\n3,4\n"  # requests.get(source.url).text
    return raw


if __name__ == "__main__":
    dbengine = boot()
    print(fetch_england_football_fixtures(dbengine))
