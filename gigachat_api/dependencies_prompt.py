import asyncio
from typing import Annotated, Optional
from fastapi import Depends
from gigachat_api.managers.token_manager import PromptManager
from gigachat_api.dependencies import GigaChatTokenManagerDep

_cached_prompt_manager: Optional[PromptManager] = None
_lock = asyncio.Lock()

async def get_giga_prompt_manager(token_manager: GigaChatTokenManagerDep) -> PromptManager:
    global _cached_prompt_manager
    async with _lock:
        if _cached_prompt_manager is None:
            _cached_prompt_manager = PromptManager(token_manager=token_manager)
        return _cached_prompt_manager

GigaChatPromptManagerDep = Annotated[PromptManager, Depends(get_giga_prompt_manager)]