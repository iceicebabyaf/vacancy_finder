import logging
import os

from utils.config import settings



os.makedirs(settings.LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(settings.LOG_FILE, mode="a")
    ]
)

logger = logging.getLogger(__name__)