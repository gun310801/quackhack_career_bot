# config.py
from dotenv import load_dotenv
import os

load_dotenv("key.env")

OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")
