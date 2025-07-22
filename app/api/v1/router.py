from fastapi import APIRouter

from app.api.v1.handlers import assistant_handler, chroma_handler

router = APIRouter()

router.include_router(assistant_handler.router  , prefix="/assistant"   , tags=["Assistant"])
router.include_router(chroma_handler.router   , prefix="/chroma"      , tags=["Chroma Vector Store"] )