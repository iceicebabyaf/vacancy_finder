from fastapi import APIRouter
import sys, os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from gigachat_api.managers.models_manager import ModelsManager


app = APIRouter()

@app.get('/all', description='showing all avaliable GigaChat models')
async def get_all_avaliable_models():
    model = ModelsManager()
    status, data = await model.get_models()
    return {
        "status": status,
        "payload": data
    }
