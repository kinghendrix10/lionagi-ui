# config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["CEREBRAS_API_KEY"] = os.getenv('CEREBRAS_API_KEY')