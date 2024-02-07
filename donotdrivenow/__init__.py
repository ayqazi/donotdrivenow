from dotenv import load_dotenv, find_dotenv


def boot():
    load_dotenv(find_dotenv('.env'))
    load_dotenv(find_dotenv('.env.local'))
