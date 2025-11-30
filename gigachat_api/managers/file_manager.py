import os, json
from pathlib import Path

from utils.logger import logger

class StorageManager:
    def __init__(self, filename, dirname):
        self.dirname = Path(dirname)
        self.filename = self.dirname / filename

    async def save(self, data):
        logger.debug(f'[Storage]: Trying to save data to {self.filename}')
        try:
            os.makedirs(self.dirname, exist_ok=True)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f'[Storage]: Data saved succesfully to {self.dirname} // {self.filename}')
        except Exception as e:
            logger.exception(f'[Storage]: Unsuccessful saving {self.filename}: {e}')
            raise

    async def open_file(self):
        logger.debug(f'[Storage]: Trying to open: {self.filename}')
        if not self.filename.exists() or self.filename.stat().st_size == 0:
            raise FileNotFoundError(f"File not found or empty: {self.filename}")
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.exception(f'[Storage]: Invalid JSON in {self.filename}\nError:\n{e}')
            raise
