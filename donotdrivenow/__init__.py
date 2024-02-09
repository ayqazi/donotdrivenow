from os import getenv

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

APP = {"booted": False}


def boot():
    if not APP["booted"]:
        load_dotenv(find_dotenv('.env'))
        load_dotenv(find_dotenv('.env.local'))

        APP["engine"] = create_engine(getenv('DATABASE_URI'), echo=True)
        APP["booted"] = True

    return APP["engine"]
