from functools import lru_cache

from app.services.assistant_service import AssistantService

@lru_cache()
def get_assistant_service() -> AssistantService:
    return AssistantService()

async def get_initialized_assistant_service() -> AssistantService:
    service = get_assistant_service()
    await service.ensure_initialized()
    return service
