"""LangChain-based Language Tutor Service with Ollama and LangSmith"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# LangChain imports
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.tools import Tool
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client as LangSmithClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangChainTutorService:
    def __init__(self, 
                 translation_model: str = "translategemma:4b",
                 reasoning_model: str = "mixtral:8x7b",
                 langsmith_api_key: Optional[str] = None,
                 langsmith_project: str = "language-tutor"):
        """
        Initialize LangChain-based tutor service
        
        Args:
            translation_model: Ollama model for translation tasks
            reasoning_model: Ollama model for reasoning/memory tasks
            langsmith_api_key: LangSmith API key for observability
            langsmith_project: LangSmith project name
        """
        self.translation_model = translation_model
        self.reasoning_model = reasoning_model
        self.langsmith_project = langsmith_project
        
        # Configure LangSmith if API key provided
        if langsmith_api_key:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
            os.environ["LANGSMITH_PROJECT"] = langsmith_project
            self.langsmith_client = LangSmithClient()
            logger.info("LangSmith tracing enabled")
        else:
            logger.warning("LangSmith API key not provided - tracing disabled")
            self.langsmith_client = None
        
        # Initialize LangChain models
        self._initialize_models()
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=10, 
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create the agent
        self.agent = self._create_agent()
        
        logger.info("LangChain Tutor Service initialized successfully")
    
    def _initialize_models(self):
        """Initialize LangChain ChatOllama models"""
        try:
            # Translation model
            self.translation_llm = ChatOllama(
                model=self.translation_model,
                temperature=0.1,
                # Additional model parameters can be added here
            )
            
            # Reasoning model for complex tasks
            self.reasoning_llm = ChatOllama(
                model=self.reasoning_model,
                temperature=0.1,
            )
            
            logger.info(f"Models initialized: {self.translation_model}, {self.reasoning_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {str(e)}")
            raise
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the language tutor agent"""
        
        def translate_text_tool(query: str) -> str:
            """Translate text using the translation model"""
            try:
                # Parse query format: "text | target_language [source_language]"
                parts = query.split(" | ")
                if len(parts) < 2:
                    return "Error: Use format 'text | target_language' or 'text | target_language | source_language'"
                
                text = parts[0].strip()
                target_lang = parts[1].strip()
                source_lang = parts[2].strip() if len(parts) > 2 else "auto"
                
                result = self.translate_text(text, target_lang, source_lang)
                return self._format_translation_result(result)
                
            except Exception as e:
                logger.error(f"Translation tool error: {str(e)}")
                return f"Translation error: {str(e)}"
        
        def detect_language_tool(text: str) -> str:
            """Detect language of given text"""
            try:
                result = self.detect_language(text)
                if result['success']:
                    return f"Detected language: {result['detected_language']} (confidence: {result.get('confidence', 'unknown')})"
                else:
                    return f"Language detection failed: {result.get('error', 'Unknown error')}"
            except Exception as e:
                logger.error(f"Language detection tool error: {str(e)}")
                return f"Language detection error: {str(e)}"
        
        def generate_exercise_tool(query: str) -> str:
            """Generate language learning exercise"""
            try:
                # Parse query format: "language [difficulty]"
                parts = query.split()
                if not parts:
                    return "Error: Specify language and optionally difficulty (beginner/intermediate/advanced)"
                
                language = parts[0]
                difficulty = parts[1] if len(parts) > 1 else "beginner"
                
                result = self.generate_exercise(language, difficulty)
                if result['success']:
                    return result['exercise']
                else:
                    return f"Exercise generation failed: {result.get('error', 'Unknown error')}"
            except Exception as e:
                logger.error(f"Exercise generation tool error: {str(e)}")
                return f"Exercise generation error: {str(e)}"
        
        def get_progress_tool(query: str) -> str:
            """Get learning progress for a language"""
            try:
                # This would integrate with user progress tracking
                language = query.strip() if query.strip() else "general"
                return f"Progress tracking for {language} would be displayed here. (Integration with user_manager needed)"
            except Exception as e:
                logger.error(f"Progress tool error: {str(e)}")
                return f"Progress tracking error: {str(e)}"
        
        return [
            Tool(
                name="translate_text",
                description="Translate text. Use format: 'text | target_language' or 'text | target_language | source_language'",
                func=translate_text_tool
            ),
            Tool(
                name="detect_language", 
                description="Detect the language of given text",
                func=detect_language_tool
            ),
            Tool(
                name="generate_exercise",
                description="Generate a language learning exercise. Use format: 'language [difficulty]'",
                func=generate_exercise_tool
            ),
            Tool(
                name="get_progress",
                description="Get learning progress for a specific language",
                func=get_progress_tool
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the language tutor agent"""
        try:
            # Create the prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Language Tutor Assistant. 
                
                Your capabilities include:
                - Translating text between languages
                - Detecting languages
                - Generating personalized learning exercises
                - Tracking student progress
                
                Available tools: translate_text, detect_language, generate_exercise, get_progress
                
                Be helpful, educational, and adaptive to the student's level. 
                Provide explanations and context when helpful.
                Always maintain a supportive and encouraging tone."""),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Create the agent
            agent = create_openai_tools_agent(self.reasoning_llm, self.tools, prompt)
            
            # Create the executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                memory=self.memory,
                verbose=True,
                max_iterations=3,
                handle_parsing_errors=True
            )
            
            logger.info("Language tutor agent created successfully")
            return agent_executor
            
        except Exception as e:
            logger.error(f"Failed to create agent: {str(e)}")
            raise
    
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Dict[str, Any]:
        """Translate text using LangChain ChatOllama"""
        try:
            # Create translation prompt
            if source_language == "auto":
                prompt = f"Translate the following text to {target_language}: '{text}'"
            else:
                prompt = f"Translate the following {source_language} text to {target_language}: '{text}'"
            
            # Invoke the model
            response = self.translation_llm.invoke([HumanMessage(content=prompt)])
            
            return {
                'success': True,
                'original_text': text,
                'translated_text': response.content.strip(),
                'source_language': source_language,
                'target_language': target_language,
                'model': self.translation_model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'original_text': text
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language using LangChain ChatOllama"""
        try:
            prompt = f"What language is this text written in? Respond with just the language name: '{text}'"
            
            response = self.translation_llm.invoke([HumanMessage(content=prompt)])
            
            return {
                'success': True,
                'detected_language': response.content.strip(),
                'text': text,
                'model': self.translation_model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text
            }
    
    def generate_exercise(self, language: str, difficulty: str = "beginner") -> Dict[str, Any]:
        """Generate language learning exercise"""
        try:
            prompt = f"""Create a {difficulty} {language} language exercise. 
            Include:
            1. A short text in {language}
            2. A translation task
            3. A vocabulary question
            Format it clearly with sections."""
            
            response = self.reasoning_llm.invoke([HumanMessage(content=prompt)])
            
            return {
                'success': True,
                'exercise': response.content.strip(),
                'language': language,
                'difficulty': difficulty,
                'model': self.reasoning_model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Exercise generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def chat_with_tutor(self, message: str) -> Dict[str, Any]:
        """Chat with the language tutor agent"""
        try:
            response = self.agent.invoke({"input": message})
            
            return {
                'success': True,
                'response': response['output'],
                'intermediate_steps': response.get('intermediate_steps', []),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_translation_result(self, result: Dict[str, Any]) -> str:
        """Format translation result for display"""
        if result['success']:
            return f"""Translation: {result['translated_text']}
From: {result['source_language']} → To: {result['target_language']}
Model: {result['model']}"""
        else:
            return f"Translation failed: {result.get('error', 'Unknown error')}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history from memory"""
        try:
            messages = self.memory.chat_memory.messages
            history = []
            
            for message in messages:
                if isinstance(message, HumanMessage):
                    history.append({
                        'role': 'user',
                        'content': message.content,
                        'timestamp': datetime.now().isoformat()
                    })
                elif isinstance(message, AIMessage):
                    history.append({
                        'role': 'assistant',
                        'content': message.content,
                        'timestamp': datetime.now().isoformat()
                    })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def clear_conversation_memory(self):
        """Clear the conversation memory"""
        try:
            self.memory.clear()
            logger.info("Conversation memory cleared")
        except Exception as e:
            logger.error(f"Error clearing conversation memory: {str(e)}")
    
    def get_langsmith_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent LangSmith runs for observability"""
        if not self.langsmith_client:
            return []
        
        try:
            runs = list(self.langsmith_client.list_runs(
                project_name=self.langsmith_project,
                limit=limit
            ))
            
            return [
                {
                    'id': run.id,
                    'name': run.name,
                    'start_time': run.start_time,
                    'end_time': run.end_time,
                    'status': run.status,
                    'error': run.error
                }
                for run in runs
            ]
            
        except Exception as e:
            logger.error(f"Error getting LangSmith runs: {str(e)}")
            return []
