import asyncio
import json

from typing import Dict, List, Optional, cast
from datetime import datetime
from decimal import Decimal

from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI


from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.assistant_schema import AssistantState
from app import logger

#Converts Decimal values to float before encoding to JSON.
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class AssistantNode:
    """Assistant Node for POS System"""
    
    def __init__(
            self
            , runnable  : Runnable
            , llm       : ChatOpenAI
    ):
        self.runnable   = runnable
        self.llm       = llm

    #extracts and formats relevant data from the assistant's state before sending it to the LLM.
    def _prepare_context(
            self,
            state      : AssistantState
    ) -> Dict[str, str]:
        """Prepare comprehensive context from state components."""
        try:
            #Retrieves task results
            task_results = state.get('task_results', {})
            logger.debug(f"Task results keys: {task_results.keys()}")
            
            #Extracts image processing results (vision analysis).
            vision_data = None
            
            if TaskType.VISION_ANALYSIS in task_results:
                vision_result   = task_results[TaskType.VISION_ANALYSIS]
                if vision_result and vision_result.result:
                    vision_data = vision_result.result
                    logger.debug("Found vision data in task results")
            
            if not vision_data:
                if state.get("vision_analysis"):
                    vision_data = state["vision_analysis"]
                    logger.debug("Found vision data in vision_analysis")
                elif state.get("vision_data"):
                    vision_data = state["vision_data"]
                    logger.debug("Found vision data in vision_data")
            
            # Extract minister data from task results
            minister_data = None
            if TaskType.KNOWLEDGE_SYNTHESIS in task_results:
                knowledge_result = task_results[TaskType.KNOWLEDGE_SYNTHESIS]
                if knowledge_result and knowledge_result.result and "data" in knowledge_result.result:
                    minister_data = knowledge_result.result["data"]
                    logger.debug("Found minister data in task results")
            elif TaskType.STOCK_CHECK in task_results:
                stock_result = task_results[TaskType.STOCK_CHECK]
                if stock_result and stock_result.result and "data" in stock_result.result:
                    minister_data = stock_result.result["data"]
                    logger.debug("Found minister data in task results")
            
            if not minister_data:
                if state.get("minister_data"):
                    minister_data = state["minister_data"]
                    logger.debug("Found minister data in state")
                elif state.get("context", {}).get("minister_data"):
                    minister_data = state["context"]["minister_data"]
                    logger.debug("Found minister data in context")
            
            #Converts extracted data to JSON 
            context = {
                "vision_analysis"   : json.dumps(vision_data, indent=2, cls=CustomJSONEncoder) if vision_data else "",
                "minister_data"     : json.dumps(minister_data, indent=2, cls=CustomJSONEncoder) if minister_data else "{}",
                "search_results"    : json.dumps(state.get("search_results", []), indent=2)
            }
            
            # Add language information if available
            if state.get("context", {}).get("is_khmer_query"):
                context["response_language"] = "khmer"
            else:
                context["response_language"] = "english"

            for key, value in context.items():
                has_data = bool(value and value not in ['""', '{}', '[]', 'null'])
                logger.debug(f"{key} has data: {has_data}")
                if has_data:
                    logger.debug(f"{key} preview: {value[:200]}...")

            return context

        except Exception as e:
            logger.error(f"Error preparing context: {str(e)}", exc_info=True)
            return {
                "vision_analysis": "",
                "minister_data": "{}",
                "search_results": "[]"
            }

    """Determine confidence score based on task type."""
    def get_confidence_score(state: AssistantState) -> float:
        
        if TaskType.STOCK_CHECK in state.get("current_tasks", []):
            return 0.5  # AI lacks real-time stock data
        elif TaskType.KNOWLEDGE_SYNTHESIS in state.get("current_tasks", []):
            return 0.8  # AI can generate knowledge-based responses
        elif TaskType.VISION_ANALYSIS in state.get("current_tasks", []):
            return 0.9  # Vision processing is fairly accurate
        return 1.0  # Default high confidence

    #processes the assistant's response based on the current state.
    async def __call__(
            self,
            state      : AssistantState
    ) -> AssistantState:
        """Process the current state and generate a response."""
        try:
            logger.info(f"Assistant Node receiving state with keys: {state.keys()}")
            logger.debug(f"Current task results: {state.get('task_results', {}).keys()}")
            
            if not state.get("messages"):
                return state

            # Prepare context
            context = self._prepare_context(state)
            
            # Create input for LLM with all context
            runnable_input = {
                "messages": state.get("messages", []),
                **context
            }

            logger.debug(f"Sending to LLM with context keys: {context.keys()}")
            
            # Get LLM response
            result = await self.runnable.ainvoke(runnable_input)
            response = result.content if hasattr(result, 'content') else str(result)
            
            logger.debug(f"LLM Response: {response}")
            
            return {
                **state,
                "messages": [
                    *state.get("messages", []),
                    AIMessage(content=response)
                ],
                
                "task_results": {
                    **state.get("task_results", {}),
                    TaskType.KNOWLEDGE_SYNTHESIS: TaskResult(
                        task_type           = TaskType.KNOWLEDGE_SYNTHESIS,
                        status              = TaskStatus.COMPLETED,
                        message             = "Response generated",
                        started_at          = datetime.now(),
                        completed_at        = datetime.now(),
                        result              = {"response": response},
                        error               = None,
                        #confidence_score    = self.get_confidence_score(state)
                        confidence_score    = 1.0
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Assistant error: {str(e)}", exc_info=True)
            raise