import json
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph.message import StateGraph, add_messages, AnyMessage

from app.database.schemas.task_schema import TaskType, TaskResult, TaskStatus
from app.database.schemas.assistant_schema import AssistantState
from app.tools.minister_tools import MinisterTools
from app.utils.language_utils import should_respond_in_khmer
from app import logger

class MinisterNode:
    def __init__(self, llm: ChatOpenAI, db_session, minister_tools: MinisterTools):
        self.llm = llm
        self.db = db_session
        self.minister_tools = minister_tools
        self.verbose = True
        
    async def __call__(self, state: AssistantState) -> AssistantState:
        """Process minister and government-related queries."""
        try:
            logger.info("Minister Node processing government query")
            
            # Get the user's message
            messages = state.get("messages", [])
            if not messages:
                return state
                
            user_message = messages[-1].content if messages else ""
            
            # Detect language for response
            is_khmer_query = should_respond_in_khmer(user_message)
            
            # Determine what type of government query this is
            query_type = self._determine_query_type(user_message)
            logger.info(f"Query type determined: {query_type}")
            
            # Execute the appropriate query
            result = await self._execute_government_query(query_type, user_message)
            logger.info(f"Query result type: {type(result)}")
            if isinstance(result, dict):
                logger.info(f"Query result keys: {result.keys()}")
            
            # Create task result
            from datetime import datetime
            task_result = TaskResult(
                task_type=TaskType.KNOWLEDGE_SYNTHESIS,  # Use knowledge_synthesis for government queries
                status=TaskStatus.COMPLETED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                result={"data": result, "count": len(result) if isinstance(result, list) else 1},
                message=f"Successfully processed {query_type} query - found {len(result) if isinstance(result, list) else 1} items"
            )
            
            # Update state with results
            current_results = state.get("task_results", {})
            current_results[TaskType.KNOWLEDGE_SYNTHESIS] = task_result
            
            # Add minister data to state
            return {
                **state,
                "task_results": current_results,
                "minister_data": result,
                "context": {
                    "minister_data": result,
                    "data_count": len(result) if isinstance(result, list) else 1,
                    "query_type": query_type,
                    "is_khmer_query": is_khmer_query
                }
            }
            
        except Exception as e:
            logger.error(f"Error in minister operation: {str(e)}")
            # Return error result
            from datetime import datetime
            task_result = TaskResult(
                task_type=TaskType.KNOWLEDGE_SYNTHESIS,
                status=TaskStatus.FAILED,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                result={"error": str(e)},
                error=str(e),
                message="Failed to process MPWT query"
            )
            
            current_results = state.get("task_results", {})
            current_results[TaskType.KNOWLEDGE_SYNTHESIS] = task_result
            
            return {
                **state,
                "task_results": current_results,
                "minister_data": {"error": str(e)}
            }
    
    def _determine_query_type(self, message: str) -> str:
        """Determine what type of MPWT query this is."""
        message_lower = message.lower()
        
        # Check for historical queries first
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', message)
        if year_match and any(word in message_lower for word in ["minister", "ministers", "mpwt", "during", "year", "in"]):
            return "historical_minister"
        
        # Check for specific sub-organization queries (both English and Khmer)
        english_sub_orgs = ["pas", "sihanoukville", "ppap", "phnom penh", "general inspectorate", "inspectorate", "port autonomous"]
        khmer_sub_orgs = ["ការិយាល័យ", "អគ្គនាយកដ្ឋាន", "ស្ថាប័ន", "កំពង់ផែ", "ដឹកជញ្ជូន"]
        
        # Check if message contains any sub-organization keywords
        has_english_sub_org = any(word in message_lower for word in english_sub_orgs)
        has_khmer_sub_org = any(word in message for word in khmer_sub_orgs)  # Note: not lower() for Khmer
        
        if has_english_sub_org or has_khmer_sub_org:
            return "sub_org_content"
        
        if any(word in message_lower for word in ["minister", "ministers"]):
            return "minister"
        elif any(word in message_lower for word in ["sub org", "sub-org", "sub orgs", "sub-orgs", "organization", "organizations", "org", "orgs", "transport", "public works", "how many"]):
            return "sub_org"
        elif any(word in message_lower for word in ["content", "page", "policy", "road", "official", "information", "details", "about", "tell me about", "mpwt", "mission", "vision", "background"]):
            return "content"
        else:
            return "general"
    
    async def _execute_government_query(self, query_type: str, message: str) -> Dict[str, Any]:
        """Execute the appropriate MPWT query."""
        try:
            if query_type == "historical_minister":
                # Extract year from message
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', message)
                if year_match:
                    year = int(year_match.group())
                    return await self.minister_tools.get_minister_by_year(year)
                else:
                    return {"error": "Could not extract year from query"}
            elif query_type == "minister":
                # Get current MPWT minister
                return await self.minister_tools.get_current_minister()
            elif query_type == "sub_org":
                # Get all MPWT sub organizations
                return await self.minister_tools.get_sub_organizations()
            elif query_type == "content":
                # Try to get content for specific organizations or general content
                message_lower = message.lower()
                
                # Try to find the most relevant content based on the query
                try:
                    # First, try to find content that matches the specific query
                    content = await self.minister_tools.search_content_by_keywords(message)
                    if content and (content.get("en_content") or content.get("kh_content")):
                        return {
                            "type": "mpwt_content",
                            "content": content,
                            "message": "Found relevant MPWT information from content database"
                        }
                except Exception as e:
                    logger.debug(f"Could not find content matching query: {str(e)}")
                
                # Try keyword search for specific terms
                search_terms = []
                if "mpwt" in message_lower:
                    search_terms.extend(["mpwt", "ministry", "public works"])
                elif "mission" in message_lower:
                    search_terms.extend(["mission", "គោលបំណង"])
                elif "vision" in message_lower:
                    search_terms.extend(["vision", "ទស្សនវិស័យ"])
                elif "background" in message_lower:
                    search_terms.extend(["background", "ផ្ទាល់ខ្លួន"])
                elif "about" in message_lower:
                    search_terms.extend(["about", "អំពី"])
                else:
                    search_terms.extend(["mpwt", "ministry", "public works", "transport"])
                
                # Try each search term
                for term in search_terms:
                    try:
                        content = await self.minister_tools.search_content_by_keywords(term)
                        if content and (content.get("en_content") or content.get("kh_content")):
                            return {
                                "type": "mpwt_content",
                                "content": content,
                                "message": f"Found MPWT information for '{term}' from content database"
                            }
                    except Exception as e:
                        logger.debug(f"Could not find content for term '{term}': {str(e)}")
                
                # Check for specific organization content
                if "pas" in message_lower or "sihanoukville" in message_lower:
                    try:
                        # Try to get PAS content by Khmer name
                        return await self.minister_tools.get_content_by_name("កំពង់ផែស្វយ័តក្រុងព្រះសីហនុ (PAS)")
                    except:
                        return {"message": "PAS content not found in the database"}
                
                elif "ppap" in message_lower or "phnom penh" in message_lower:
                    try:
                        # Try to get PPAP content by Khmer name
                        return await self.minister_tools.get_content_by_name("កំពង់ផែស្វយ័តភ្នំពេញ (PPAP)")
                    except:
                        return {"message": "PPAP content not found in the database"}
                
                else:
                    # Final fallback: try to get any content that might be relevant
                    try:
                        content = await self.minister_tools.search_content_by_keywords("about")
                        if content:
                            return {
                                "type": "mpwt_content",
                                "content": content,
                                "message": "Found MPWT information from content database"
                            }
                    except Exception as e:
                        logger.debug(f"Could not find any relevant content: {str(e)}")
                    
                    return {"message": "MPWT content not found for the requested page"}
            
            elif query_type == "sub_org_content":
                # Handle specific sub-organization content queries
                message_lower = message.lower()
                
                # First, try to find content that matches the specific query
                try:
                    content = await self.minister_tools.search_content_by_keywords(message)
                    if content and (content.get("en_content") or content.get("kh_content")):
                        return {
                            "type": "sub_org_content",
                            "content": content,
                            "message": "Found sub-organization information from content database"
                        }
                except Exception as e:
                    logger.debug(f"Could not find content matching query: {str(e)}")
                
                # Handle specific known sub-organizations
                if "pas" in message_lower or "sihanoukville" in message_lower or "ការិយាល័យរាជធានីសីហនុ" in message:
                    logger.info("Processing PAS/Sihanoukville query")
                    try:
                        # Try multiple search strategies for PAS
                        search_terms = ["pas", "sihanoukville", "ការិយាល័យរាជធានីសីហនុ", "កំពង់ផែស្វយ័តក្រុងព្រះសីហនុ"]
                        for term in search_terms:
                            try:
                                logger.info(f"Trying search term: {term}")
                                content = await self.minister_tools.search_content_by_keywords(term)
                                if content:
                                    logger.info(f"Found content for term: {term}")
                                    return {
                                        "type": "sub_org_content",
                                        "content": content,
                                        "message": "Found PAS information from content database"
                                    }
                            except Exception as e:
                                logger.debug(f"Failed to find content for term '{term}': {str(e)}")
                                continue
                        logger.info("No PAS content found in database")
                        return {"message": "PAS content not found in the database"}
                    except Exception as e:
                        logger.error(f"Error processing PAS query: {str(e)}")
                        return {"message": "PAS content not found in the database"}
                
                elif "ppap" in message_lower or "phnom penh" in message_lower or "ការិយាល័យរាជធានីភ្នំពេញ" in message:
                    try:
                        # Try multiple search strategies for PPAP
                        search_terms = ["ppap", "phnom penh", "ការិយាល័យរាជធានីភ្នំពេញ", "កំពង់ផែស្វយ័តភ្នំពេញ"]
                        for term in search_terms:
                            try:
                                content = await self.minister_tools.search_content_by_keywords(term)
                                if content:
                                    return {
                                        "type": "sub_org_content",
                                        "content": content,
                                        "message": "Found PPAP information from content database"
                                    }
                            except:
                                continue
                        return {"message": "PPAP content not found in the database"}
                    except:
                        return {"message": "PPAP content not found in the database"}
                
                elif "general inspectorate" in message_lower or "inspectorate" in message_lower or "អគ្គនាយកដ្ឋាន" in message:
                    try:
                        # Try multiple search strategies for General Inspectorate
                        search_terms = ["inspectorate", "អគ្គនាយកដ្ឋាន", "អគ្គនាយកដ្ឋានផែនការ និងគោលនយោបាយ"]
                        for term in search_terms:
                            try:
                                content = await self.minister_tools.search_content_by_keywords(term)
                                if content:
                                    return {
                                        "type": "sub_org_content",
                                        "content": content,
                                        "message": "Found General Inspectorate information from content database"
                                    }
                            except:
                                continue
                        return {"message": "General Inspectorate content not found in the database"}
                    except:
                        return {"message": "General Inspectorate content not found in the database"}
                
                # For any other sub-organization, try to find content by searching for the organization name
                else:
                    try:
                        # Extract potential organization names from the message
                        # Look for Khmer organization terms
                        khmer_org_terms = ["ការិយាល័យ", "អគ្គនាយកដ្ឋាន", "ស្ថាប័ន"]
                        for term in khmer_org_terms:
                            if term in message:
                                try:
                                    content = await self.minister_tools.search_content_by_keywords(term)
                                    if content:
                                        return {
                                            "type": "sub_org_content",
                                            "content": content,
                                            "message": "Found sub-organization information from content database"
                                        }
                                except:
                                    continue
                        
                        # If no Khmer terms found, try the entire message as a search term
                        content = await self.minister_tools.search_content_by_keywords(message)
                        if content:
                            return {
                                "type": "sub_org_content",
                                "content": content,
                                "message": "Found sub-organization information from content database"
                            }
                    except Exception as e:
                        logger.debug(f"Could not find sub-organization content: {str(e)}")
                
                return {"message": "Sub-organization content not found"}
            else:
                # General MPWT information
                return {
                    "message": "MPWT Information Assistant",
                    "capabilities": [
                        "Information about MPWT ministers (current and historical)",
                        "MPWT sub-organization details", 
                        "Official MPWT content",
                        "Transport policies and road information",
                        "Public works and infrastructure projects"
                    ],
                    "suggestion": "Please ask specific questions about MPWT ministers, organizations, transport policies, or content. You can also ask about ministers from specific years (e.g., 'who was the minister in 2000?')."
                }
                
        except Exception as e:
            logger.error(f"Error executing MPWT query: {str(e)}")
            return {"error": str(e)} 