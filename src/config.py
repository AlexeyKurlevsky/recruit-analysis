import logging
import os

from airflow.exceptions import AirflowException
from airflow.models import Variable
from airflow.settings import DAGS_FOLDER
from dotenv import load_dotenv
from sqlalchemy import create_engine


def get_required_variable(name: str):
    # variable = os.getenv(name)
    variable = Variable.get(name)
    if variable is None or variable == "CHANGE_ME":
        raise AirflowException(f"Set {name}")
    return variable


load_dotenv()

FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)

# Для разработки
HUNTFLOW_ACCESS_TOKEN = get_required_variable("HUNTFLOW_ACCESS_TOKEN")
HUNTFLOW_REFRESH_TOKEN = get_required_variable("HUNTFLOW_REFRESH_TOKEN")

HUNTFLOW_USERNAME = os.getenv("HUNTFLOW_USERNAME")
HUNTFLOW_PASSWORD = os.getenv("HUNTFLOW_PASSWORD")
HUNTFLOW_URL = os.getenv("HUNTFLOW_URL", "https://huntflow.ru")
HUNTFLOW_URL_API = os.getenv("HUNTFLOW_URL_API", "https://api.huntflow.ru")

DATABASE_HOST = os.getenv("HUNTFLOW_DATABASE_HOST")
DATABASE_PORT = os.getenv("HUNTFLOW_DATABASE_PORT")
DATABASE_HUNTFLOW = os.getenv("HUNTFLOW_DATABASE_DB")
DATABASE_HUNTFLOW_USERNAME = os.getenv("HUNTFLOW_DATABASE_USERNAME")
DATABASE_HUNTFLOW_PASSWORD = os.getenv("HUNTFLOW_DATABASE_PASSWORD")

SELENIUM_URL = os.getenv("SELENIUM_URL", "http://remote_chromedriver:4444")

SQLALCHEMY_DB_URI = (
    f"postgresql+psycopg2://"
    f"{DATABASE_HUNTFLOW_USERNAME}:{DATABASE_HUNTFLOW_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_HUNTFLOW}"
)

MAX_ITEM_ON_PAGE = 50
TIME_OUT_LOADING_PAGE = 30

engine = create_engine(SQLALCHEMY_DB_URI)
