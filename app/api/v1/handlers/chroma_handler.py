
from fastapi import APIRouter, UploadFile

from app.services.chromdb_service import ChromaService


router = APIRouter()

chroma_service = ChromaService()

#Registers a POST request to /upload/document
@router.post("/upload/document", summary="Upload PDF document into the vector store")
async def uploadFile(file: UploadFile, collection_name: str):
    results = await chroma_service.uploadFile(
        file    = file
        , collection_name = collection_name
    )
    return results