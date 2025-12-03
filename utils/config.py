from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional
import os, sys
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

BASE_DIR = Path(__file__).resolve().parent.parent

"""


"""

class Settings(BaseSettings):
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    VK_TOKEN: Optional[str] = None
    
    CLIENT_ID_GIGACHAT: str
    AUTH_KEY_GIGACHAT: str
    SCOPE_GIGACHAT: str = "GIGACHAT_API_PERS"
    # === GigaChat settings ===
    GIGACHAT_MODEL: str = 'GigaChat'
    GIGACHAT_PROMPT_MESSAGE: str = "Привет! Ты аналитик-твоя роль просматривать посты в социальной сети и делать вердикт: является ли пост вакансией на работу. Ответ верни строго в json формате: {'answer': 1 - если вакансия / 0 - если не вакансия}"
    GIGACHAT_TEMPERATURE: float = 0.0
    GIGACHAT_TOP_P: float = 0.1
    GIGACHAT_MAX_TOKENS: int=100
    # ==========================
    
    LOG_DIR: Path = BASE_DIR / "logs"  
    LOG_FILE: Path = LOG_DIR / "hh.log"
    LOG_DIR_TEMP_DATA: Path = BASE_DIR / "storage/temp_data"
    LOG_FILE_TEMP_DATA: Path = LOG_DIR_TEMP_DATA / "tokens.json"
    LOG_FILE_RESUME_DATA: Path = LOG_DIR_TEMP_DATA / "resume.json"
    LOG_FILE_VACANCY_DATA: Path = LOG_DIR_TEMP_DATA / "vacancy.json"
    LOG_FILE_VACANCY_RESPOND_STATUS: Path = LOG_DIR_TEMP_DATA / "respond_status.json"
    LOG_FILE_DICT_DATA: Path = LOG_DIR_TEMP_DATA / "dictionary.json"
    LOG_FILE_GCHAT_DATA: Path = LOG_DIR_TEMP_DATA / "gigachat_tokens.json"
    LOG_FILE_GHCHAT_MODELS: Path = LOG_DIR_TEMP_DATA / "gigachat_models.json"



    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )
settings = Settings()