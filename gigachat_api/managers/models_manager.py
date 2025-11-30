import aiohttp 

from gigachat_api.dependencies import GigaChatTokenManagerDep
from gigachat_api.managers.file_manager import StorageManager
from utils.config import settings
from utils.logger import logger

FILENAME = settings.LOG_FILE_GHCHAT_MODELS
DIRNAME = settings.LOG_DIR_TEMP_DATA

class ModelsManager:
    def __init__(self, token_manager: GigaChatTokenManagerDep):
        self.url = 'https://gigachat.devices.sberbank.ru/api/v1/models'
        self.tokens = token_manager
        self.saver = StorageManager(filename=FILENAME, dirname=DIRNAME)

    async def get_models(self):
        logger.debug(f'[GIGA_MODELS]: Starting recieving all giga models ...')
        access_token = await self.tokens.ensure_valid_tokens()
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url, headers=headers, ssl=False) as response:
                logger.debug(f'[GIGA_MODELS]: response status: {response.status}')
                try:
                    data = await response.json()
                    logger.info(f'[GIGA_MODELS]: response converted to json! Saving data ...')
                    await self.saver.save(data=data)
                    return response.status, data
                except Exception as e:
                    logger.error(f'[GIGA_MODELS]: Exception: {e}')
                
                
