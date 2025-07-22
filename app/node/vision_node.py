import json
from typing import Optional, List, Dict, Any, cast
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from google.generativeai import GenerativeModel
import google.generativeai as genai

from langgraph.graph.message import add_messages, AnyMessage

from app.database.schemas.base_schema import RequirementCheck
from app.database.schemas.data_schema import ValidationResult
from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.assistant_schema import AssistantState

from app.core.config import settings

from app import logger


class VisionNode:
    """Node for processing images and extracting text/document information"""

    def __init__(
            self
    ):
        # Initialize Gemini
        #genai.configure(api_key=settings.GOOGLE_GENAI_API_KEY)
        genai.configure(api_key=settings.OPENAI_API_KEY)
        self.vision_model   = GenerativeModel(
            model_name      = "gpt-4o-mini"
        )
        
        # self.vision_model   = GenerativeModel(
        #     model_name      = "gemini-1.5-flash"
        # )

        self.vision_prompt  = """You are a document and text extraction expert for a POS system.
            
            TASK:
            1. Extract ALL text visible in the image
            2. Identify document type (invoice, receipt, product label, etc.)
            3. Extract key information like:
               - Names, dates, numbers
               - Prices, quantities, totals
               - Product codes or SKUs
               - Company names or brands
            4. Organize information by category
            
            IMPORTANT: Respond ONLY with a raw JSON object like this:
            {
                "document_type": "type of document",
                "extracted_text": {
                    "raw_text": "all text found in image",
                    "structured": {
                        "headers": ["text1", "text2"],
                        "body": ["text1", "text2"],
                        "footer": ["text1", "text2"]
                    }
                },
                "key_information": {
                    "dates": ["date1", "date2"],
                    "amounts": ["amount1", "amount2"],
                    "product_codes": ["code1", "code2"],
                    "company_names": ["name1", "name2"]
                },
                "confidence_score": 0.95
            }

            ONLY return the JSON object. NO markdown, NO code blocks."""

    async def process_image(
            self
            , image_data    : bytes
            , mime_type     : str
    ) -> Dict[str, Any]:
        """Process image for text extraction"""
        try:
            image_part      = {
                "mime_type" : mime_type
                , "data"    : image_data
            }

            response        = self.vision_model.generate_content(
                contents    = [self.vision_prompt, image_part]
            )

            response.resolve()

            try:
                text_response       = response.text
                
                if text_response.startswith("```"):
                    text_response   = text_response.replace("```json", "").replace("```", "")
                
                text_response   = text_response.strip()
                logger.debug(f"Cleaned vision response: {text_response}")
                
                analysis        = json.loads(text_response)
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse vision response: {str(e)}")
                return {
                    "error": "Failed to parse text extraction",
                    "raw_response": text_response,
                    "document_type": "unknown",
                    "confidence_score": 0.0
                }

        except Exception as e:
            logger.error(f"Vision analysis error: {str(e)}")
            return {
                "error": str(e),
                "document_type": "error",
                "confidence_score": 0.0
            }


    async def __call__(
            self
            , state     : AssistantState
    ) -> AssistantState:
        """Process the current state and update with vision analysis"""
        
        try:
            if not state.get("messages"):
                return self._handle_error(state, "No messages in state")

            latest_message  = state["messages"][-1]
            
            if not hasattr(latest_message, 'additional_kwargs'):
                return self._handle_error(state, "No image data structure found")
            
            image_data     = latest_message.additional_kwargs.get('image_data')
            mime_type      = latest_message.additional_kwargs.get('mime_type', 'image/jpeg')
            
            if not image_data:
                return self._handle_error(state, "No image data found")

            logger.info("Processing image with Gemini Vision")
            
            # Process image
            analysis_result = await self.process_image(
                image_data  = image_data
                , mime_type = mime_type
            )

            new_state = state.copy()
            
            if "error" in analysis_result:
                return self._handle_error(new_state, analysis_result["error"], analysis_result)
            
            new_state["vision_data"]        = analysis_result
            new_state["vision_analysis"]    = analysis_result
            new_state["extracted_text"]     = analysis_result.get("extracted_text", {})
            
            # Update task results
            new_state["task_results"] = {
                **state.get("task_results", {}),
                TaskType.VISION_ANALYSIS: TaskResult(
                    task_type           = TaskType.VISION_ANALYSIS
                    , status            = TaskStatus.COMPLETED
                    , message           = "Vision analysis completed"
                    , started_at        = datetime.now()
                    , completed_at      = datetime.now()
                    , result            = analysis_result
                    , error             = None
                    , confidence_score  = analysis_result.get("confidence_score", 1.0)
                )
            }


            # logger.debug(f"Vision results: {TaskType.VISION_ANALYSIS in new_state['task_results']}")

            return new_state

        except Exception as e:
            logger.error(f"Vision node error: {str(e)}")
            return self._handle_error(state, str(e))

    def _handle_error(
            self
            , state     : AssistantState
            , error_msg : str
            , raw_result: Optional[Dict] = None
    ) -> AssistantState:
        """Handle errors in vision processing"""
        
        new_state = state.copy()
        
        error_result = raw_result if raw_result else {
            "error": error_msg
            , "document_type"   : "error"
            , "confidence_score": 0.0
            , "extracted_text"  : {
                "raw_text"      : ""
                , "structured"  : {
                    "headers" : []
                    , "body"    : []
                    , "footer"  : []
                }
            }
        }

        # Preserve existing task results
        new_state["task_results"] = {
            **state.get("task_results", {}),
            TaskType.VISION_ANALYSIS: TaskResult(
                task_type       = TaskType.VISION_ANALYSIS
                , status        = TaskStatus.FAILED
                , message       = error_msg
                , started_at    = datetime.now()
                , completed_at  = datetime.now()
                , result        = error_result
                , error         = error_msg
                , confidence_score = 0.0
            )
        }
        
        return new_state
    