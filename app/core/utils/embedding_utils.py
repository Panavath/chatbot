from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

class EmbeddingUtils:

    ## Todo: Implement Json embedding
    #Creates an instance of OpenAIEmbeddings for generating vector embeddings.
    def __init__(self):
        
        self.openai_emebedding  = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    #Takes a list of text chunks    
    async def createEmbedding(self, texts: List[str]) -> List[float]:

        return self.openai_emebedding.embed_documents(texts)

    #Text Splitting for Different File Types
    def getTextSplitter(self, file_type: str) -> Any:
        
        splitters = {
            'application/pdf': RecursiveCharacterTextSplitter(
                chunk_size=1000
                , chunk_overlap=100
            ),
            'text/plain': CharacterTextSplitter(
                chunk_size=2000
                , chunk_overlap=200
            ),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 
                RecursiveCharacterTextSplitter(
                    chunk_size=1500
                    , chunk_overlap=150
                ),
            'text/csv': CharacterTextSplitter(
                chunk_size=1000
                , chunk_overlap=0
            )
        }

        return splitters.get(file_type)
    
    #Extracts text from document chunks for embedding.
    def processChunk(self, chunks: List[Any], file_type: str) -> List[str]:
        if file_type == 'text/csv':
            return [self._format_csv_chunk(chunk.page_content) for chunk in chunks]
        
        return [chunk.page_content for chunk in chunks]
    
    def _format_csv_chunk(self, content: str) -> str:
        if isinstance(content, dict):
            return ". ".join([f"{k}: {v}" for k, v in content.items()])
        return str(content)