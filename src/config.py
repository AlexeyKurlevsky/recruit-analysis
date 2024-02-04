import os

from dotenv import load_dotenv

load_dotenv()

HUNTFLOW_ACCESS_TOKEN = os.getenv('HUNTFLOW_ACCESS_TOKEN')
HUNTFLOW_REFRESH_TOKEN = os.getenv('HUNTFLOW_REFRESH_TOKEN')

