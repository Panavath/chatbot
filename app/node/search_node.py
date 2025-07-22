from typing import Optional, List, Dict, Any, cast
from datetime import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langgraph.graph.message import add_messages, AnyMessage

from app.database.schemas.base_schema import RequirementCheck
from app.database.schemas.data_schema import ValidationResult
from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.search_schema import SearchResult
from app.database.schemas.stock_schema import StockData
from app.database.schemas.market_schema import MarketAnalysis
from app.database.schemas.assistant_schema import AssistantState

from app.core.config import settings
from app import logger


class SearchNode:

    def __init__(
            self
            , llm    : ChatOpenAI
    ):
        self.llm            = llm
        
        logger.debug(f"Debugging the tavily_api_key {settings.TAVILY_API_KEY}")
        
        self.search_tool    = TavilySearchAPIWrapper(
            tavily_api_key  = settings.TAVILY_API_KEY
        )

        self.search_prompt  = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=
                """
                You are an expert search query optimizer.
                Your task is to convert user questions into precise search queries.
                Focus on:
                - Current market trends and conditions
                - Economic indicators and statistics
                - Business and industry updates
                - Local and regional developments
                - Price trends and market analysis
                - Industry specific information
                - Recent news and reports

                Format the search query to be concise and specific. Only return the search query, nothing else.
                Example: For "What is the current market in Cambodia", return "Cambodia current market trends economic indicators 2024"
                """
            ),
            HumanMessage(
                content="{user_input}"
            )
        ])

        self.search_agent   = self.search_prompt | self.llm


    async def generate_search_query(
            self
            , user_input    : str
    ) -> str:
        """Generate optimized search query from user input"""
        
        try:
            search_query    = await self.search_agent.ainvoke(
                {"user_input": user_input}
            )
            
            return search_query.content.strip()

        except Exception as e:
            logger.error(f"Error generating prompt for optimal search: {str(e)}")
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                , detail    = str(e)
            )


    async def __call__(
            self
            , state     : AssistantState
            , config    : Dict[str, Any]
    ) -> AssistantState:
        
        try:
            messages        = state["messages"][-1].content if state["messages"] else ""
            
            search_query    = await self.generate_search_query(messages)
            logger.info(f"Generated search query: {search_query}")

            new_state       = state.copy()
            new_state["search_results"] = []
            new_state["task_results"] = {} 

            search_results  = self.search_tool.results(search_query)

            if search_results:
                formatted_results   = [
                    {
                        "title"     : result.get("title", "")
                        , "content" : result.get("content", "")
                        , "url"     : result.get("url", "")
                        , "score"   : result.get("score", 0.0)
                    }
                    for result in search_results
                ]

                new_state["search_results"] = formatted_results
                new_state["task_results"][TaskType.WEB_SEARCH] = TaskResult(
                    task_type       = TaskType.WEB_SEARCH
                    , status        = TaskStatus.COMPLETED
                    , started_at    = datetime.now()
                    , completed_at  = datetime.now()
                    , result        = {"search_results": formatted_results}
                    , error         = None
                    , confidence_score = 1.0 if formatted_results else 0.0
                )
                
                logger.info(f"Search completed with {len(formatted_results)} results")
            
            else:
                logger.warning("No search results found")
                new_state["task_results"][TaskType.WEB_SEARCH] = TaskResult(
                    task_type       = TaskType.WEB_SEARCH
                    , status        = TaskStatus.FAILED
                    , started_at    = datetime.now()
                    , completed_at  = datetime.now()
                    , result        = None
                    , error         = "No search results found"
                    , confidence_score = 0.0
                )

            return new_state

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            new_state = state.copy()
            new_state["task_results"] = {}  
            new_state["task_results"][TaskType.WEB_SEARCH] = TaskResult(
                task_type       = TaskType.WEB_SEARCH
                , status        = TaskStatus.FAILED
                , started_at    = datetime.now()
                , completed_at  = datetime.now()
                , result        = None
                , error         = str(e)
                , confidence_score = 0.0
            )
            return new_state