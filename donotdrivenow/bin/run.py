from sqlalchemy import select, text
from sqlalchemy.orm import Session

from donotdrivenow import boot, util
from donotdrivenow.orm import Fixture


def run(team_names):
    engine = boot()

    with Session(engine) as session, session.begin():
        fixtures = session.scalars(
            select(Fixture)
            .where(text(r'start\:\:date = :now\:\:date'))
            .where(Fixture.home_team.in_(team_names)),
            params={'now': util.now()},
        )
        for f in fixtures:
            print(f'{f.home_team} ({f.sport}) match starting {f.start.isoformat()}')


if __name__ == "__main__":
    run(['Alloa'])
