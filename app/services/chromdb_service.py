import os
import tempfile
import chromadb

from typing import Any

from fastapi import UploadFile, HTTPException, status

# Langchain
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, UnstructuredWordDocumentLoader

# Core
from app.core.config import settings, is_supported_file_type
from app.core.utils.embedding_utils import EmbeddingUtils

# Schema
from app.database.schemas.base_schema import IResponseBase

# App
from app import logger

#handling document uploads, processing text embeddings, and managing vector storage using ChromaDB
class ChromaService:

    def __init__(self):
        #Connects to the ChromaDB vector database.
        self.client         = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
        # Initializes OpenAI’s Chat model
        self.llm            = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, temperature=0.7)
        #Loads utility functions for text processing and embedding creation
        self.embedding_utils= EmbeddingUtils()

    #Handling File Uploads
    async def uploadFile(self, file: UploadFile, collection_name: str) -> IResponseBase[Any]:
        #Checks if the file type is supported
        if not is_supported_file_type(file.content_type):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST
                , detail=f"Unsupported file type. Supported types are: {', '.join(settings.SUPPORTED_FORMATS.keys())}"
            )
            
        #Creates a temporary file
        suffix                  = settings.SUPPORTED_FORMATS[file.content_type]
        temp_file_path          = None

        logger.info(f"Checkig suffix {suffix}")

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content         = await file.read()
                temp_file.write(content)
                temp_file_path  = temp_file.name

            #Load Document and Extract Text
            loader              = self._get_document_loader(temp_file_path, file.content_type)
            documents           = loader.load()

            #Splits the extracted text into smaller chunks for better embedding performance.
            text_splitter       = self.embedding_utils.getTextSplitter(file.content_type)
            split_docs          = text_splitter.split_documents(documents)

            #Processes text chunks for vectorization.
            processed_texts     = self.embedding_utils.processChunk(split_docs, file.content_type)

            document_embeddings = await self.embedding_utils.createEmbedding(processed_texts)
            
            #Store Embeddings in ChromaDB
            vector_store_db     = self.client.get_or_create_collection(name=collection_name)

            #Stores each chunk’s text and its embedding along with metadata
            for i, (text, embedding) in enumerate(zip(processed_texts, document_embeddings)):
                metadata        = {
                    #Identifies which file and chunk the text comes from
                    "source": f"{file.filename}_chunk_{i}"
                    , "file_type": file.content_type
                    #The order of this chunk in the document
                    , "chunk_index": i
                    #The total number of chunks for this file
                    , "total_chunks": len(processed_texts)
                }

                vector_store_db.add(
                    ids=[f"doc_{i}"]
                    , metadatas=[metadata]
                    , documents=[text]
                    , embeddings=[embedding]
                )

            return IResponseBase[Any](
                success=1
                , code=''
                , message=f'File {file.filename} has been successfully processed and embedded'
                , data=None
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        
        finally:
            os.unlink(temp_file_path)

    #Retrieving a Collection
    async def getCollection(self, collection_name: str) -> IResponseBase[Any]:
        try:
            #Fetches an existing collection from ChromaDB
            collection  =   self.client.get_collection(collection_name=collection_name)

            if not collection:
                HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = f"Not found collection name {collection_name} in Database"  
                )

            #returns collection metadata and stored embeddings.
            return IResponseBase[Any](
                success = 1
                , data  = collection
                , code  = ''
                , messahge  = 'Success get collection name from vector store'
            )

        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Internal Error with Chromadb"
            )

    # Deleting a Collection
    async def deleteCollection(self, collection_name: str) -> bool:
        #Deletes the collection from ChromaDB.
        try:
            
            collection  = self.client.get_collection(collection_name = collection_name)

            if not collection:
                raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST
                    , detail    = f"Colleciton name {collection_name} in the vector store"
                )
            
            is_deleted  = self.client.delete_collection(collection_name=collection_name)


            return True
        
        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = "Something went wrong with vector store db"
            )

    #File Type Loader
    def _get_document_loader(self, file_path: str, file_type: str):
        #Returns the correct document loader based on the file type
        loaders             = {
            'application/pdf': PyPDFLoader
            , 'text/plain': TextLoader
            , 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': UnstructuredWordDocumentLoader
            , 'text/csv': CSVLoader
        }

        return loaders.get(file_type)(file_path)
