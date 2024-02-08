from os import getenv

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

from donotdrivenow.orm import Base
from donotdrivenow.orm.data.raw import DataSource, Fetch


def boot():
    load_dotenv(find_dotenv('.env'))
    load_dotenv(find_dotenv('.env.local'))

    print(["Used models:",
           DataSource,
           Fetch])

    engine = create_engine(getenv('DATABASE_URI'), echo=True)
    Base.metadata.create_all(engine)

    return engine
