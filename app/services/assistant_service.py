
import chromadb
import time
import uuid

from uuid import UUID
from fastapi import HTTPException, status

from typing import List, Dict, Optional

from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI

from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from app.prompt.pos_prompt_v1 import POSPromptV1
from app.prompt.pos_prompt_v2 import POSPromptV2
from app.prompt.government_prompt_v1 import GovernmentPromptV1

from app.node.assistant_node import AssistantNode
from app.node.search_node import SearchNode
from app.node.decision_node import DecisionNode
from app.node.vision_node import VisionNode
from app.node.minister_node import MinisterNode

from app.tools.retriever_tools import RetrieverTool
from app.tools.minister_tools import MinisterTools


from app.database.schemas.base_schema import RequirementCheck
from app.database.schemas.data_schema import ValidationResult
from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.search_schema import SearchResult
from app.database.schemas.stock_schema import StockData
from app.database.schemas.market_schema import MarketAnalysis
from app.database.schemas.assistant_schema import AssistantRequest, AssistantResponseData, AssistantResponse, AssistantState

from app.node.stock_node import StockNode

from app.database import get_db

from app.core.config import settings

from app import logger

from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

#from app.core.config import db
import os

from app.prompt.pos_prompt_sql import POSPromptSQL


# # Load OpenAI Key
# openai_key = os.getenv("OPENAI_API_KEY")
# llm_name = os.getenv("LLM_NAME")

# # Initialize LLM Model
# model = ChatOpenAI(api_key=openai_key, model=llm_name)

# # Create SQL Toolkit
# toolkit = SQLDatabaseToolkit(db=db, llm=model)

# # Create SQL Agent
# sql_agent = create_sql_agent(
#     prefix=POSPromptSQL.MSSQL_AGENT_PREFIX,
#     format_instructions=POSPromptSQL.MSSQL_AGENT_FORMAT_INSTRUCTIONS,
#     llm=model,
#     toolkit=toolkit,
#     top_k=30,
#     verbose=True
# )

# def query_database(question: str):
#     """Runs a SQL query using LangChain SQL Agent"""
#     return sql_agent.invoke(question)


# Concept skeleton
class AssistantService:
    _instance       = None
    _initialized    = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance   = super().__new__(cls)
        return cls._instance

    def __init__(self):
    
        if not self._initialized:
            
            #Initializes memory storage
            self.memory         = MemorySaver()
            
            #Connects to OpenAI’s LLM
            self.llm            = ChatOpenAI(
                                            #open API key
                                            openai_api_key=settings.OPENAI_API_KEY,
                                            #OpenAI model name
                                            model         =settings.MODEL_NAME,
                                            #moderate randomness in responses
                                            temperature   =0.7,
                                            #supports streaming responses
                                            streaming     =True
                                            )
            #Uses embeddings (OpenAIEmbeddings) for similarity search.
            self.embedding      = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            #Connects to a database (chroma_client) for knowledge retrieval.
            self.chroma_client  = chromadb.HttpClient(host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT)
            #Initializes a retriever tool (RetrieverTool) for fetching relevant data.
            self.retriever_tool = RetrieverTool(
                self.chroma_client
                , self.embedding
            )

            self._initialized   = False


    async def initialize(self):
        """Initialize all components of the service."""
        if not self._initialized:
            try:
                #set up the decision-making workflow.
                await self.initializeWorkflow()
                # prepare knowledge retrieval.
                await self.retriever_tool.initialize_retriever()
                #prevent redundant initialization
                self._initialized   = True

                logger.info("Service initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize service: {str(e)}")
                raise


    async def ensure_initialized(self):
        if not self._initialized:
            await self.initialize()

    
    
    async def initializeWorkflow(self):
        try:
            #Retrieves a pre-defined prompt
            prompt          = GovernmentPromptV1.get_prompt()
            #Creates a processing pipeline
            runnable        = prompt | self.llm
            #define a workflow with different processing nodes.
            builder         = StateGraph(AssistantState)

            # Initialize nodes with session
            db              = next(get_db())
            
            #General assistant chat processing.
            assistant_node  = AssistantNode(runnable, self.llm)
            #Handles web searches
            search_node     = SearchNode(self.llm)
            #Processes image-based tasks.
            vision_node     = VisionNode()
            #Determines which node to activate.
            decision_node   = DecisionNode(self.llm)
            
            #Handles MPWT and government queries.
            minister_tools   = MinisterTools(db_session=db)
            minister_node    = MinisterNode(self.llm, db, minister_tools)

            # Add nodes
            builder.add_node("assistant", assistant_node)
            builder.add_node("search", search_node)
            builder.add_node("vision", vision_node)
            builder.add_node("decider", decision_node)
            builder.add_node("minister", minister_node)

            # Start with decision node
            builder.add_edge(START, "decider")
            
            def route_based_on_decision(state: AssistantState) -> str:
                tasks = state.get("current_tasks", [])
                logger.info(f"Routing based on tasks: {tasks}")
                
                # Get the user message to determine routing
                messages = state.get("messages", [])
                user_message = messages[-1].content.lower() if messages else ""
                original_message = messages[-1].content if messages else ""
                
                logger.info(f"User message: '{original_message}'")
                logger.info(f"User message (lower): '{user_message}'")
                
                # Route MPWT and government queries to minister node
                # Check for English keywords
                english_keywords = ["minister", "sub org", "sub-org", "sub orgs", "sub-orgs", "organization", "organizations", "org", "orgs", "government", "mpwt", "transport", "public works", "how many", "inspectorate", "port", "autonomous"]
                
                # Check for Khmer keywords (common sub-organization terms)
                khmer_keywords = ["ការិយាល័យ", "អគ្គនាយកដ្ឋាន", "ស្ថាប័ន", "ក្រសួង", "រដ្ឋមន្ត្រី", "កំពង់ផែ", "ដឹកជញ្ជូន"]
                
                # Check if message contains any English or Khmer keywords
                has_english_keyword = any(word in user_message for word in english_keywords)
                has_khmer_keyword = any(word in original_message for word in khmer_keywords)
                
                logger.info(f"Has English keyword: {has_english_keyword}")
                logger.info(f"Has Khmer keyword: {has_khmer_keyword}")
                
                if has_english_keyword or has_khmer_keyword:
                    logger.info("Routing to minister node")
                    return "minister"
                
                #If the task involves vision analysis, route to vision.
                elif TaskType.VISION_ANALYSIS in tasks:
                    return "vision"
                #If it requires web search, route to search.
                elif TaskType.WEB_SEARCH in tasks:
                    return "search"
                
                logger.info("Routing to assistant node")
                return "assistant"
            
            # Add  edges from decision node
            builder.add_conditional_edges(
                "decider",
                route_based_on_decision,
                {
                    "minister"   : "minister",
                    "vision"     : "vision",
                    "search"     : "search",
                    "assistant"  : "assistant"
                }
            )

            builder.add_edge("minister", "assistant")  # Minister -> Assistant
            builder.add_edge("vision", "assistant")    # Vision -> Assistant
            builder.add_edge("search", "assistant")    # Search -> Assistant
            builder.add_edge("assistant", END)         # Assistant -> End

            # Compile workflow
            self.workflow = builder.compile(
                #track conversation history.
                checkpointer = self.memory,
                # debug       = True
            )

            logger.info("""Workflow configured:
                START -> decider -> [
                    minister -> assistant -> END,
                    vision -> assistant -> END,
                    search -> assistant -> END,
                    assistant -> END
                ]
            """)

            return self.workflow
            
        except Exception as e:
            logger.error(f"Failed to initialize workflow: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail     = str(e)
            )


    async def generateResponse(
            self
            , request: AssistantRequest
    ):
        try:
            starttime       = time.time()
            thread_id       = request.thread_id or str(uuid.uuid4())
                                                       
            message         = HumanMessage(content=request.messages)

            if request.image_data:
                message.additional_kwargs = {
                    "image_data": request.image_data,
                    "image_type": request.image_type
                }


            state           = {
                "messages"  : [message]
                , "context"   : ""
                , "current_tasks": []
                , "task_results": {}
                , "requirements": None
                , "search_results": []
                , "stock_data": None
                , "market_analysis": None
                , "validation_results": None
                , "conversation_context": {}
                , "thread_id": thread_id
                , "last_validation_time": None
                , "processing_metadata": {}
            }


            config          = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            logger.info("Invoking workflow")
            response        = await self.workflow.ainvoke(state, config)

            # logger.debug(f"Checking response from LLM {response}")

            #Extracts the assistant’s final response text
            if isinstance(response, dict) and "messages" in response:
                messages    = response["messages"]
                content     = (
                    messages[-1].content if isinstance(messages, list) 
                    else (messages.content if hasattr(messages, 'content') else str(messages))
                )

                confidence_score = 1.0
                if "task_results" in response:
                    for task_result in response["task_results"].values():
                        if task_result.confidence_score is not None:
                            confidence_score = min(
                                confidence_score
                                , task_result.confidence_score
                            )

                return AssistantResponse(
                    status          = True,
                    data            = AssistantResponseData(
                        response        = str(content)
                        , thread_id       = thread_id
                        , processing_time = time.time() - starttime
                        , confidence_score= confidence_score
                    )
                )

            return AssistantResponse(
                status          = False,
                data            = AssistantResponseData(
                    response        = "No valid response generated"
                    , thread_id       = thread_id
                    , processing_time = time.time() - starttime
                    , confidence_score= 0.0 
                )
            )

        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            return AssistantResponse(
                status          = False,
                data            = AssistantResponseData(
                    response        = str(e)
                    , thread_id       = thread_id
                    , processing_time = time.time() - starttime
                    , confidence_score= 0.0 
                )
            )