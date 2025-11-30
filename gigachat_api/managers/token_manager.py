import aiohttp
import json
from fastapi import HTTPException


from gigachat_api.dependencies import GigaChatTokenManagerDep
from utils.config import settings
from utils.logger import logger

class PromptManager:
    """
    Manager for generating prompts and sending to GigaChat.

    --- file size < 80 MB
    """
    def __init__(self, token_manager: GigaChatTokenManagerDep):
        self.url = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
        self.model = settings.GIGACHAT_MODEL
        self._token_manager = token_manager
        self._prompt_message = settings.GIGACHAT_PROMPT_MESSAGE
        self.temperature = settings.GIGACHAT_TEMPERATURE
        self.top_p = settings.GIGACHAT_TOP_P
        self.max_tokens = settings.GIGACHAT_MAX_TOKENS

    async def send_text(self, text: str) -> str:
        access_token = await self._token_manager.get_valid_token()
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }


        payload = {
            'model': self.model,
            'messages': [
                {
                    "role": "system",
                    "content": self._prompt_message,
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            'stream': False,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'max_tokens': self.max_tokens,
            'repetition_penalty': 1.0,
            'update_interval': 0,

            'functions': [
                    {
                        'name': 'submit_vacancy_verdict',
                        'description': 'Возвращает вердикт: является ли текст вакансией',
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'answer': {
                                    'type': 'integer',
                                    'enum': [0, 1],
                                    'description': '1 — вакансия, 0 — не вакансия'
                                }
                            },
                            'required': ['answer'],
                            'additionalProperties': False
                        }
                    }
                ],
                'function_call': {'name': 'submit_vacancy_verdict'},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, headers=headers, json=payload, ssl=False) as response:
                logger.debug(f'[GIGACHAT CHAT]: status: {response.status}')
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f'[GIGACHAT CHAT]: Error {response.status}: {error_text}')
                    raise HTTPException(status_code=response.status, detail=error_text)

                try:
                    payload_response = await response.json()
                    content = payload_response["choices"][0]["message"]["content"]
                    logger.info(f'[GIGACHAT CHAT]: Success! Response length: {len(content)} chars')
                    return payload_response
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    error_text = await response.text() if not isinstance(e, json.JSONDecodeError) else str(e)
                    logger.error(f'[GIGACHAT CHAT]: Error parsing response: {e}. Raw: {error_text}')
                    raise HTTPException(status_code=500, detail="Invalid GigaChat response")
