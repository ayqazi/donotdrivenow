import logging
import sys
from os import getenv

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

APP = {"booted": False}


def boot():
    if not APP["booted"]:
        load_dotenv(find_dotenv('.env'))
        load_dotenv(find_dotenv('.env.local'))

        logging.basicConfig(stream=sys.stderr,
                            format='%(asctime)s %(levelname)s: %(message)s',
                            encoding='utf-8')
        logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

        APP["engine"] = create_engine(getenv('DATABASE_URI'))
        APP["booted"] = True

    return APP["engine"]
