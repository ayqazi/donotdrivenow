import sys
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from donotdrivenow import boot, util
from donotdrivenow.orm import Fixture


def run(team_names, match_day):
    engine = boot()

    with Session(engine) as session, session.begin():
        fixtures = session.scalars(
            select(Fixture)
            .where(text(r'start\:\:date = :now\:\:date'))
            .where(Fixture.home_team.in_(team_names)),
            params={'now': match_day},
        )
        for f in fixtures:
            print(f'{f.home_team} ({f.sport}) match starting {f.start.isoformat()}')


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date = datetime.fromisoformat(sys.argv[1])
    else:
        date = util.now()

    run(['Leicester', 'Leicester Tigers'], date)
