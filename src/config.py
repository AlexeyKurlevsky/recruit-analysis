import os
import logging
import json

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

HUNTFLOW_ACCESS_TOKEN = os.getenv('HUNTFLOW_ACCESS_TOKEN')
HUNTFLOW_REFRESH_TOKEN = os.getenv('HUNTFLOW_REFRESH_TOKEN')
HUNTFLOW_USERNAME = os.getenv('HUNTFLOW_USERNAME')
HUNTFLOW_PASSWORD = os.getenv('HUNTFLOW_PASSWORD')

DATABASE_HOST = os.getenv('HUNTFLOW_DATABASE_HOST')
DATABASE_PORT = os.getenv('HUNTFLOW_DATABASE_PORT')
DATABASE_HUNTFLOW = os.getenv('HUNTFLOW_DATABASE_DB')
DATABASE_HUNTFLOW_USERNAME = os.getenv('HUNTFLOW_DATABASE_USERNAME')
DATABASE_HUNTFLOW_PASSWORD = os.getenv('HUNTFLOW_DATABASE_PASSWORD')

SQLALCHEMY_DB_URI = (f'postgresql+psycopg2://'
                     f'{DATABASE_HUNTFLOW_USERNAME}:{DATABASE_HUNTFLOW_PASSWORD}@'
                     f'{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_HUNTFLOW}')

MAX_ITEM_ON_PAGE = 50

f = open('./config/applicant_statuses.json')
applicant_statuses = json.load(f)
APPLICANT_STATUSES = {elem['id']: elem['name'] for elem in applicant_statuses}

engine = create_engine(SQLALCHEMY_DB_URI)
