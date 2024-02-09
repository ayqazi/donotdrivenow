from os import getenv

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

import donotdrivenow.orm.data.raw as raw
from donotdrivenow.orm import Base


def boot():
    load_dotenv(find_dotenv('.env'))
    load_dotenv(find_dotenv('.env.local'))

    print(["Used models:",
           raw.DataSource,
           raw.Grab])

    engine = create_engine(getenv('DATABASE_URI'), echo=True)
    Base.metadata.create_all(engine)

    return engine
