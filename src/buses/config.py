""" API key loader. """

import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = os.path.join(ROOT_DIR, 'api_key.env')

load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv('API_KEY')
