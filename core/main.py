# core/main.py
import uvicorn
from shared.logger import get_logger
from shared.config import Config
from core.server import app as server_app

logger = get_logger(__name__)

def start():
    logger.info("🚀 Starting CalvinOS Core...")
    uvicorn.run(
        server_app,
        host="0.0.0.0",
        port=8000,
        log_level=Config.LOG_LEVEL.lower()
    )

if __name__ == '__main__':
    start()