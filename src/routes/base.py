from fastapi import APIRouter, Depends
from helpers.config import get_config, Config
from datetime import datetime
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def root(config: Config = Depends(get_config)):
    return {
        "app_name": config.APP_NAME,
        "version": config.VERSION,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    }