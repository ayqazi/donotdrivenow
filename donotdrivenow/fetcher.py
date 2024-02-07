from os import getenv

import requests
from sqlalchemy import create_engine, text

import donotdrivenow
from donotdrivenow.orm import Base
from donotdrivenow.orm.football_data import FootballDataFixturesRaw


# https://www.football-data.co.uk/matches.php
# Updates Tuesday at 13:00 UK time and Friday at 17:00 UK time
def fetch_england_football_fixtures():
    raw = requests.get('https://www.football-data.co.uk/fixtures.csv').text

    engine = create_engine(getenv('DATABASE_URI'), echo=True)
    Base.metadata.create_all(engine)

    print(["Used models:",
           FootballDataFixturesRaw])

    with engine.begin() as conn:
        result = conn.execute(text("select 'hello world'"))
        return result.all()


if __name__ == "__main__":
    donotdrivenow.boot()
    print(fetch_england_football_fixtures())
