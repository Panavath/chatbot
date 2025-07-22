from typing import Optional, Any, List, Dict

from fastapi import HTTPException, status

# Langchain
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from langchain.tools import tool
from langchain_core.documents import Document
from langchain_community.document_transformers import EmbeddingsRedundantFilter, LongContextReorder
from langchain.retrievers import ContextualCompressionRetriever, MergerRetriever
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline


class RetrieverTool:
    """Collection of retriever-based tools for the agent."""

    def __init__(self, chroma_client
                , embedding_model: Optional[Any] = None
                , search_kwargs: Dict[str, Any] = {"k": 10}):

        self.chroma_client      = chroma_client
        self.embedding_model    = embedding_model or OpenAIEmbeddings()
        
        self.retriever          = None

        #self.collections        = self._initialized_collection()
    async def initialize(self):
        """Async initializer to set up collections."""
        self.collections = await self.chroma_client.list_collections()


    async def _initialized_collection(self) -> List[str]:
        try:
            self.collections    = self.chroma_client.list_collections()

            return self.collections
        
        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )

    async def initialize_retriever(self):
        """Initialize the merged or get retriever with collections."""

        try:

            await self._initialized_collection()

            retrievers = []
            collection_names = self.chroma_client.list_collections()

            for name in collection_names:
                collection = self.chroma_client.get_collection(name)
                vector_store = Chroma(
                    collection_name=name,
                    embedding_function=self.embedding_model,
                    client=self.chroma_client
                )
                retrievers.append(vector_store.as_retriever(search_kwargs={"k": 10}))

            merged_retriever    = MergerRetriever(
                retrievers      = retrievers
            )

            redundant_filters   = EmbeddingsRedundantFilter(
                embeddings      = self.embedding_model
            )

            reordering          = LongContextReorder()

            pipeline            = DocumentCompressorPipeline(
                transformers    = [redundant_filters, reordering]
            )

            self.retriever      = ContextualCompressionRetriever(
                base_compressor = pipeline
                , base_retriever= merged_retriever
            )

        except Exception as e:
            raise ValueError(f"Failed to initialize retriever: {str(e)}")

