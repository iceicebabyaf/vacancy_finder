from dataclasses import asdict, dataclass
from typing import Optional
import asyncio
import aiohttp
import time
from uuid import uuid4

from gigachat_api.managers.file_manager import StorageManager
from utils.config import settings
from utils.logger import logger

FILENAME = settings.LOG_FILE_GCHAT_DATA
DIRNAME = settings.LOG_DIR_TEMP_DATA


@dataclass
class GigaChatToken:
    access_token: str
    expires_at: float # ms

    def is_valid(self, margin: int = 120) -> bool:
        return (self.expires_at / 1000) - time.time() > margin


class GigaChatTokenStorage:
    def __init__(self):
        self.saver = StorageManager(filename=FILENAME, dirname=DIRNAME)

    async def get_token(self) -> Optional[GigaChatToken]:
        try:
            data = await self.saver.open_file()
            token = GigaChatToken(
                access_token=data.get("access_token"),
                expires_at=data.get("expires_at"),
            )
            if token.access_token and token.expires_at:
                logger.info("[GIGA JWT Storage]: Token loaded from file")
                return token
        except FileNotFoundError:
            logger.warning("[JWT Storage]: Tokens file not found")
            return {}
        except ValueError as e:
            logger.error(f"[JWT Storage]: Invalid tokens file: {e}")
            return {}
        return None

    async def save_token(self, token: GigaChatToken) -> None:
        # serialize to dict (json dumps)
        await self.saver.save(asdict(token))


class GigaChatTokenClient:
    @staticmethod
    async def post(url: str, headers: dict, data: dict):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, headers=headers, data=data, ssl=False) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f'[GIGA JWT Cli]: response status: {resp.status}')
                    raise RuntimeError(f"GIGA auth error {resp.status}: {text}")
                return await resp.json()


class GigaChatTokenManager:
    def __init__(self):
        self._token: Optional[GigaChatToken] = None
        self._lock = asyncio.Lock()
        self._storage = GigaChatTokenStorage()

        self.url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.auth_key = settings.AUTH_KEY_GIGACHAT
        self.scope = settings.SCOPE_GIGACHAT

    async def _refresh_token(self) -> GigaChatToken:
        logger.info("[GIGA JWT Manager] refreshing access_token ...")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid4()),
            "Authorization": f"Basic {self.auth_key}",
        }
        payload = {"scope": self.scope}

        response = await GigaChatTokenClient.post(self.url, headers, payload)

        token = GigaChatToken(
            access_token=response["access_token"],
            expires_at=response["expires_at"],
        )

        self._token = token
        await self._storage.save_token(token)
        logger.info(f"[GIGA JWT Manager] Token recieved! Valid for: {(token.expires_at/1000 - time.time())/60:.1f} min.")
        return token

    async def get_valid_token(self) -> str:
        async with self._lock:
            # None -> trying to load from file
            if self._token is None:
                loaded = await self._storage.get_token()
                if loaded and loaded.is_valid():
                    self._token = loaded

            # None or expired -> update
            if not self._token or not self._token.is_valid():
                self._token = await self._refresh_token()

            return self._token.access_token


_cached_manager: Optional[GigaChatTokenManager] = None


async def get_giga_token_manager() -> GigaChatTokenManager:
    global _cached_manager
    if _cached_manager is None:
        _cached_manager = GigaChatTokenManager()
    return _cached_manager