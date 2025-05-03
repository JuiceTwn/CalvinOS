# shared/config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    CORE_WS_URL: str = os.getenv("CORE_WS_URL", "ws://localhost:8000/ws")
    STORAGE_DB_PATH: str = os.getenv("STORAGE_DB_PATH", "calvinos.db")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")