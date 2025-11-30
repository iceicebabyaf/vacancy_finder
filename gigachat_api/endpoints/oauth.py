from fastapi import APIRouter, HTTPException
import sys, os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from gigachat_api.dependencies import GigaChatTokenManagerDep
from utils.logger import logger


app = APIRouter()

@app.get('/update_access', description='FOA endpoint - saving access_token to the cache & storage/temp_data/_.json')
async def get_token(manager: GigaChatTokenManagerDep):
    try:
        token = await manager.get_valid_token()
    except RuntimeError as e:
        logger.error(f"[JWT API]: Token refresh failed: {e}")
        raise HTTPException(status_code=502, detail="GigaChat token refresh failed")
    except Exception as e:
        logger.exception(f"[JWT API]: Unexpected error in GigaChat auth: {e}")
        raise HTTPException(status_code=500, detail="Internal authorization error")
    if not token:
        raise HTTPException(status_code=500, detail="No valid token after refresh attempt")
    return {'access token:': token}