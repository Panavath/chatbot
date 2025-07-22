import json

from typing import Optional, List, Dict, Any, cast
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai.chat_models import ChatOpenAI

from langgraph.graph.message import StateGraph, add_messages, AnyMessage

from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.assistant_schema import AssistantState
from app import logger


class DecisionNode:
    def __init__(
            self
            , llm    : ChatOpenAI
            
    ):
        self.llm    = llm
        self.verbose = True
        
        template_content = """You are a decision maker for a POS intelligent assistant system.
            Your task is ONLY to determine which tasks are required to answer the user's query.
            
            MOST IMPORTANT RULES:
            1. ONLY use "stock_check" for direct product queries
            2. ONLY use "vision_analysis" for image or visual analysis requests
            3. NEVER combine unrelated tasks
            4. ALWAYS pick the MOST SPECIFIC task type for the query

            Task Types and Their EXACT Uses:
            
            "vision_analysis": MUST BE USED for:
            - ANY mention of pictures, images, photos
            - Requests to analyze, look at, or check visuals
            - Keywords: "picture", "image", "photo", "analyze", "look at", "scan"
            
            "stock_check": ONLY for:
            - Direct product inquiries
            - Stock level questions
            - Price checks
            - Product availability
            
            "web_search": ONLY for:
            - Market research requests
            - Competitor information
            - External data needs
            
            "knowledge_synthesis": MUST BE USED for:
            - Government/MPWT related queries
            - Questions about ministers, ministries, organizations
            - General system questions
            - Non-product, non-image queries
            - Help with POS usage
            - Keywords: "mpwt", "minister", "ministry", "government", "organization", "about", "tell me about"

            EXAMPLE QUERIES AND CORRECT RESPONSES:

            1. "Can you analyze this picture?"
            {
                "required_tasks": ["vision_analysis"],
                "requirements": ["Analyze provided image"],
                "priority_order": ["vision_analysis"],
                "confidence_score": 0.95
            }

            2. "How many products do we have?"
            {
                "required_tasks": ["stock_check"],
                "requirements": ["Check total product count"],
                "priority_order": ["stock_check"],
                "confidence_score": 0.95
            }

            3. "Tell me about MPWT"
            {
                "required_tasks": ["knowledge_synthesis"],
                "requirements": ["Provide MPWT information from content database"],
                "priority_order": ["knowledge_synthesis"],
                "confidence_score": 0.95
            }

            4. "Who is the current minister?"
            {
                "required_tasks": ["knowledge_synthesis"],
                "requirements": ["Get current minister information"],
                "priority_order": ["knowledge_synthesis"],
                "confidence_score": 0.95
            }

            User Query: {input}

            You must ONLY respond with the exact JSON format shown above."""

        self.decision_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=template_content)
        ])
        
        self.decision_chain = self.decision_prompt | self.llm

    def _detect_image_query(
            self
            , message    : str
            , state     : AssistantState
    ) -> bool:
        """Detect if query is image-related."""
        # Check message content
        image_indicators = [
            "picture", "image", "photo", "visual", "analyze", "look at"
            , "scan", "camera", "capture", "show me", "view"
        ]
        
        message_lower   = message.lower()
        has_indicators  = any(indicator in message_lower for indicator in image_indicators)
        
        # Check for actual image in message
        messages        = state.get("messages", [])
        latest_message  = messages[-1] if messages else None
        
        has_image      = (
            hasattr(latest_message, 'additional_kwargs') 
            and ('image_data' in latest_message.additional_kwargs 
                 or 'images' in latest_message.additional_kwargs)
        ) if latest_message else False
        
        return has_indicators or has_image

    def _detect_product_query(
            self
            , message    : str
    ) -> bool:
        """Detect if query is product-related."""
        product_indicators = [
            "stock", "price", "how much", "available", "inventory",
            "product", "item", "store", "sell", "buy", "cost",
            "how many", "quantity", "check"
        ]
        
        # Government/MPWT keywords that should NOT be classified as product queries
        government_indicators = [
            "mpwt", "minister", "ministry", "government", "organization", 
            "about", "tell me about", "sub org", "sub-org", "port", "autonomous",
            "inspectorate", "transport", "public works"
        ]
        
        message_lower = message.lower()
        
        # If it contains government keywords, it's NOT a product query
        if any(indicator in message_lower for indicator in government_indicators):
            return False
            
        return any(indicator in message_lower for indicator in product_indicators)

    async def __call__(
            self
            , state     : AssistantState
            , config    : Dict[str, Any]
    ) -> AssistantState:
        try:
            messages        = state.get("messages", [])
            
            if not messages:
                logger.warning("No messages in state")
                return {
                    **state,
                    "current_tasks"     : [TaskType.KNOWLEDGE_SYNTHESIS],
                    "requirements"      : ["Handle empty message"],
                    "confidence_score"  : 0.1
                }

            latest_message  = messages[-1].content if messages else ""
            logger.debug(f"Processing message: {latest_message}")

            if self._detect_image_query(latest_message, state):
                logger.info("Image-related query detected")
                return {
                    **state,
                    "current_tasks"     : [TaskType.VISION_ANALYSIS],
                    "requirements"      : ["Analyze visual content"],
                    "confidence_score"  : 0.95
                }


            if self._detect_product_query(latest_message):
                logger.info("Product-related query detected")
                return {
                    **state,
                    "current_tasks"     : [TaskType.STOCK_CHECK],
                    "requirements"      : ["Process product inquiry"],
                    "confidence_score"  : 0.95
                }
            else:
                logger.info("Not a product query, using LLM decision")

            try:

                decision        = await self.decision_chain.ainvoke(
                    {"input": latest_message}
                )
                
                logger.debug(f"LLM decision response: {decision.content}")
                
                decision_data   = json.loads(decision.content.strip())
                
                task_mapping   = {
                    "web_search"         : TaskType.WEB_SEARCH,
                    "vision_analysis"    : TaskType.VISION_ANALYSIS,
                    "stock_check"        : TaskType.STOCK_CHECK,
                    "knowledge_synthesis": TaskType.KNOWLEDGE_SYNTHESIS
                }
                
                current_tasks  = [
                    task_mapping[task.lower()] 
                    for task in decision_data.get("required_tasks", [])
                    if task.lower() in task_mapping
                ]
                
                if not current_tasks:
                    current_tasks = [TaskType.KNOWLEDGE_SYNTHESIS]
                
                return {
                    **state,
                    "current_tasks"     : current_tasks,
                    "requirements"      : decision_data.get("requirements", []),
                    "confidence_score"  : decision_data.get("confidence_score", 0.5)
                }

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from LLM: {str(e)}")
                return {
                    **state,
                    "current_tasks"     : [TaskType.KNOWLEDGE_SYNTHESIS],
                    "requirements"      : ["Handle invalid response format"],
                    "confidence_score"  : 0.1
                }
                
        except Exception as e:
            logger.error(f"Decision node error: {str(e)}")
            return {
                **state,
                "current_tasks"     : [TaskType.KNOWLEDGE_SYNTHESIS],
                "requirements"      : ["Handle unexpected error"],
                "confidence_score"  : 0.1
            }