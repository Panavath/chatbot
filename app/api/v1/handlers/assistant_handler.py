from fastapi import APIRouter, Depends, File, UploadFile, Form, Query
from typing import List, Optional

from app.database.schemas.assistant_schema import AssistantRequest, AssistantResponse

from app.services.assistant_service import AssistantService

from app import logger
from app.api.deps.llm_deps import get_initialized_assistant_service, get_assistant_service

#from app.services.assistant_service import query_database

router  = APIRouter()

#Registers a POST request at /chat
@router.post("/chat", response_model=AssistantResponse)
async def chat_with_Assistant(
    #Required text message input from the user.
    messages    : str = Form(...)
    #Requires images input (optional)
    , image    : Optional[UploadFile] = File(None)
    #Optional thread ID (for tracking conversation history)
    , thread_id: Optional[str] = Form(None)
    #Injected AI assistant service for processing messages.
    , service   : AssistantService = Depends(get_initialized_assistant_service)
)-> AssistantResponse:
    try:
        #The user’s text message (messages).
        request = AssistantRequest(
            messages    = messages,
            thread_id   = thread_id
        )
        
        #image is uploaded, it reads the image data asynchronously.
        if image:
            image_data          = await image.read()
            request.image_data = image_data
            request.image_type = image.content_type
        
        #alls the AI assistant service (service.generateResponse(request)) asynchronously.
        result  = await service.generateResponse(request)
        return result

    #Catches any errors that occur during request processing.
    except Exception as e:
        logger.error(f"Error in chat with agent: {str(e)}")
        raise
