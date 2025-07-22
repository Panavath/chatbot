import chromadb

from langchain_openai.chat_models import ChatOpenAI

from app.tools.retriever_tools import RetrieverTool

class RetrievalNode:
    """Node to handle document retrieval and relevance assessment with language context."""

    def __init__(self, retreiver: RetrieverTool, llm: ChatOpenAI):

        self.retriever      = retreiver

    ## Todo: Implement Retrival node flows
    def __call__(self) -> None:
        pass