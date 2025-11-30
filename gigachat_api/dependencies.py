from typing import Annotated
from fastapi import Depends

from gigachat_api.managers.auth_manager import get_giga_token_manager,GigaChatTokenManager



GigaChatTokenManagerDep = Annotated[GigaChatTokenManager, Depends(get_giga_token_manager)]
