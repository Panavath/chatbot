"""
LLM Service for RAG Chatbot
Handles response generation using OpenAI or Gemini with fallback logic
"""

import logging
import os
from typing import List, Optional, Dict, Any
from openai import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from config import Config
from chatbot_prompt import ChatbotPrompt

logger = logging.getLogger(__name__)

class LLMService:
    """LLM service with OpenAI and Gemini support"""
    
    def __init__(self):
        self.openai_client = None
        self.openai_llm = None
        self.gemini_llm = None
        self._using_openai = True
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize LLM models"""
        # Initialize OpenAI
        if Config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                self.openai_llm = ChatOpenAI(
                    model=Config.CHAT_MODEL,
                    temperature=Config.LLM_TEMPERATURE
                )
                logger.info("✅ OpenAI LLM initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenAI: {e}")
        
        # Initialize Gemini
        if Config.GEMINI_API_KEY:
            try:
                # Set environment variable for Gemini
                os.environ["GOOGLE_API_KEY"] = Config.GEMINI_API_KEY
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model=Config.GEMINI_CHAT_MODEL,
                    temperature=Config.LLM_TEMPERATURE,
                    convert_system_message_to_human=True
                )
                logger.info("✅ Gemini LLM initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Gemini: {e}")
        
        # Set default LLM
        if self.openai_llm:
            self._using_openai = True
            logger.info("🎯 Using OpenAI as primary LLM")
        elif self.gemini_llm:
            self._using_openai = False
            logger.info("🎯 Using Gemini as primary LLM")
        else:
            raise RuntimeError("❌ No LLM models available")
    
    def generate_response(self, query: str, context: List[str], language: str = "auto") -> str:
        """Generate response using available LLM"""
        if not context:
            return self._no_context_response(language, query)
        
        try:
            if self._using_openai and self.openai_llm:
                return self._openai_response(query, context, language)
            elif self.gemini_llm:
                return self._gemini_response(query, context, language)
            else:
                return self._simple_response(query, context, language)
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return self._fallback_response(language)
    
    def _openai_response(self, query: str, context: List[str], language: str) -> str:
        """Generate response using OpenAI"""
        try:
            # Prepare context
            context_text = "\n\n".join(context)
            
            # Use the new MPWT prompt template
            if language == "km":
                system_prompt = """អ្នកគឺជា MPWT Assistant ដែលជាប្រព័ន្ធ AI កម្រិតខ្ពស់សម្រាប់ក្រសួងសាធារណការ និងដឹកជញ្ជូន។ ឆ្លើយតបដោយប្រើព័ត៌មានដែលបានផ្តល់ឱ្យប៉ុណ្ណោះ។"""
                user_prompt = f"បរិបទ:\n{context_text}\n\nសំណួរ: {query}\n\nឆ្លើយតប:"
            else:
                # Use the new MPWT prompt template
                prompt_template = ChatbotPrompt.get_simple_prompt()
                formatted_prompt = prompt_template.format(context=context_text, input=query)
                
                # Generate response using the formatted prompt
                response = self.openai_llm.invoke(formatted_prompt)
                return response.content
            
            # Generate response for Khmer language
            response = self.openai_llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ OpenAI response generation failed: {e}")
            # Try to fallback to Gemini
            if self.gemini_llm:
                logger.info("🔄 Falling back to Gemini")
                self._using_openai = False
                return self._gemini_response(query, context, language)
            else:
                return self._simple_response(query, context, language)
    
    def _gemini_response(self, query: str, context: List[str], language: str) -> str:
        """Generate response using Gemini"""
        try:
            # Prepare context
            context_text = "\n\n".join(context)
            
            # Use the new MPWT prompt template
            if language == "km":
                prompt = f"""អ្នកគឺជា MPWT Assistant ដែលជាប្រព័ន្ធ AI កម្រិតខ្ពស់សម្រាប់ក្រសួងសាធារណការ និងដឹកជញ្ជូន។ ឆ្លើយតបដោយប្រើព័ត៌មានដែលបានផ្តល់ឱ្យប៉ុណ្ណោះ។

បរិបទ:
{context_text}

សំណួរ: {query}

ឆ្លើយតប:"""
            else:
                # Use the new MPWT prompt template
                prompt_template = ChatbotPrompt.get_simple_prompt()
                formatted_prompt = prompt_template.format(context=context_text, input=query)
                
                # Generate response using the formatted prompt
                response = self.gemini_llm.invoke(formatted_prompt)
                return response.content
            
            # Generate response for Khmer language
            response = self.gemini_llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Gemini response generation failed: {e}")
            # Try to fallback to OpenAI
            if self.openai_llm:
                logger.info("🔄 Falling back to OpenAI")
                self._using_openai = True
                return self._openai_response(query, context, language)
            else:
                return self._simple_response(query, context, language)
    
    def _simple_response(self, query: str, context: List[str], language: str) -> str:
        """Generate simple response without LLM"""
        if language == "km":
            return f"រកឃើញព័ត៌មានពាក់ព័ន្ធចំនួន {len(context)} ប្រភេទ។ សូមពិនិត្យមើលព័ត៌មានខាងក្រោម៖\n\n" + "\n\n".join(context)
        else:
            return f"Found {len(context)} relevant pieces of information. Please review the following:\n\n" + "\n\n".join(context)
    
    def _no_context_response(self, language: str, query: str = "") -> str:
        """Response when no context is found"""
        # Check if this is a conversational query
        conversational_queries = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "sup", "greetings", "goodbye", "bye", "thanks", "thank you",
            "what can you do", "help", "who are you", "introduce yourself"
        ]
        
        query_lower = query.lower().strip()
        is_conversational = any(conv in query_lower for conv in conversational_queries)
        
        if is_conversational:
            if language == "km":
                return "សួស្តី! 👋 ខ្ញុំជា MPWT Assistant សម្រាប់ព័ត៌មានអំពីក្រសួងសាធារណការ និងដឹកជញ្ជូន។ ខ្ញុំអាចជួយអ្នកដោយ៖\n\n• បញ្ជីអគ្គនាយកដ្ឋានទាំងអស់\n• ព័ត៌មានលម្អិតអំពីអគ្គនាយកដ្ឋាននីមួយៗ\n• ការពិពណ៌នាអំពីភារកិច្ចនិងតួនាទី\n\nសូមសួរខ្ញុំអំពីអគ្គនាយកដ្ឋានណាមួយ!"
            else:
                return "Hello! 👋 I'm MPWT Assistant for information about the Ministry of Public Works and Transport. I can help you with:\n\n• List of all general departments\n• Detailed information about each department\n• Descriptions of responsibilities and roles\n\nFeel free to ask me about any department!"
        else:
            if language == "km":
                return "សូមអភ័យទោស ខ្ញុំមិនអាចរកឃើញព័ត៌មានពាក់ព័ន្ធនឹងសំណួររបស់អ្នកបានទេ។ សូមសួរអំពីក្រសួង ឬអង្គការរដ្ឋាភិបាល។"
            else:
                return "I'm sorry, I couldn't find any relevant information for your question. Please ask about ministries or government organizations."
    
    def _fallback_response(self, language: str) -> str:
        """Fallback response when all LLMs fail"""
        if language == "km":
            return "សូមអភ័យទោស មានបញ្ហាក្នុងការឆ្លើយតប។ សូមព្យាយាមម្តងទៀត។"
        else:
            return "I'm sorry, there was an error generating a response. Please try again."
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        return {
            "primary_model": "OpenAI" if self._using_openai else "Gemini",
            "openai_available": self.openai_llm is not None,
            "gemini_available": self.gemini_llm is not None,
            "openai_model": Config.CHAT_MODEL if self.openai_llm else None,
            "gemini_model": Config.GEMINI_CHAT_MODEL if self.gemini_llm else None
        }
    
    def switch_model(self, use_openai: bool = True) -> bool:
        """Switch between OpenAI and Gemini"""
        if use_openai and self.openai_llm:
            self._using_openai = True
            logger.info("🔄 Switched to OpenAI")
            return True
        elif not use_openai and self.gemini_llm:
            self._using_openai = False
            logger.info("🔄 Switched to Gemini")
            return True
        else:
            logger.warning("⚠️ Cannot switch to requested model - not available")
            return False 