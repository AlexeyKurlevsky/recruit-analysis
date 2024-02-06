import os
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

HUNTFLOW_ACCESS_TOKEN = os.getenv('HUNTFLOW_ACCESS_TOKEN')
HUNTFLOW_REFRESH_TOKEN = os.getenv('HUNTFLOW_REFRESH_TOKEN')

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_HUNTFLOW = os.getenv('DATABASE_HUNTFLOW')
DATABASE_HUNTFLOW_USERNAME = os.getenv('DATABASE_HUNTFLOW_USERNAME')
DATABASE_HUNTFLOW_PASSWORD = os.getenv('DATABASE_HUNTFLOW_PASSWORD')

SQLALCHEMY_DB_URI = (f'postgresql+psycopg2://'
                     f'{DATABASE_HUNTFLOW_USERNAME}:{DATABASE_HUNTFLOW_PASSWORD}@'
                     f'{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_HUNTFLOW}')

MAX_ITEM_ON_PAGE = 50

engine = create_engine(SQLALCHEMY_DB_URI)
