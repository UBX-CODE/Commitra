import os
from pathlib import Path
from dotenv import load_dotenv

# Load from .env file if it exists
load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    MAX_DIFF_CHARS = int(os.getenv("MAX_DIFF_CHARS", "30000"))
    RECENT_COMMIT_COUNT = int(os.getenv("RECENT_COMMIT_COUNT", "5"))

config = Config()
