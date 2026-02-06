"""LangChain-based Language Tutor Service - OPTIMIZED for Speed

Architecture (2 LLM calls instead of 4):
1. FunctionGemma (270M): Fast tool routing via native Ollama tools API
2. Single execution model: TranslateGemma for translation, DeepSeek-R1 for everything else

This reduces latency from ~45s to ~15s per message.
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Ollama for native tools API
import ollama

# LangChain imports
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langsmith import Client as LangSmithClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# TUTOR TOOLS (for FunctionGemma's native tools API)
# =============================================================================

TUTOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "translate",
            "description": "Translate specific text to another language. ONLY use when user explicitly asks to translate specific words or phrases like 'translate X to Y' or 'how do you say X in Y'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The specific text to translate"},
                    "target_language": {"type": "string", "description": "Target language"}
                },
                "required": ["text", "target_language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "teach",
            "description": "Teach vocabulary, grammar, or language concepts. Use when user asks about specific words, grammar rules, or wants to learn a specific topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "What to teach"},
                    "language": {"type": "string", "description": "Target language"}
                },
                "required": ["topic", "language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exercise",
            "description": "Generate a practice exercise or quiz. Use when user wants to practice, test knowledge, or asks for exercises.",
            "parameters": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "Target language"},
                    "difficulty": {"type": "string", "description": "beginner, intermediate, or advanced"}
                },
                "required": ["language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "chat",
            "description": "General conversation and greetings. Use for: hello, hi, I want to learn, let's begin, thank you, questions about the tutor, or any casual conversation.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


class LangChainTutorService:
    """
    Optimized Multi-Model Language Tutor (2 LLM calls per message)

    - FunctionGemma: Fast routing (270M params, ~2s)
    - Ministral-3b: High-quality reasoning for language tutoring
    - TranslateGemma: Translation support (~4b params)
    """

    def __init__(self,
                 translation_model: str = "translategemma:4b",
                 reasoning_model: str = "ministral-3:3b",  # Better quality for language tutoring
                 function_model: str = "functiongemma",
                 langsmith_api_key: Optional[str] = None,
                 langsmith_project: str = "language-tutor"):

        self.translation_model = translation_model
        self.reasoning_model = reasoning_model
        self.function_model = function_model
        self.langsmith_project = langsmith_project

        # Configure LangSmith
        if langsmith_api_key:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
            os.environ["LANGSMITH_PROJECT"] = langsmith_project
            self.langsmith_client = LangSmithClient()
            logger.info("LangSmith tracing enabled")
        else:
            self.langsmith_client = None

        self._initialize_models()
        logger.info("Optimized Tutor Service ready (2 LLM calls per message)")

    def _initialize_models(self):
        """Initialize models"""
        logger.info("=" * 60)
        logger.info("INITIALIZING OPTIMIZED ARCHITECTURE")
        logger.info("=" * 60)

        # FunctionGemma - via Ollama native for tools API
        logger.info(f"[1/3] Router: {self.function_model} (270M, ~2s)")
        # Called via ollama.chat()

        # DeepSeek-R1 - for teaching, exercises, chat
        logger.info(f"[2/3] Reasoning: {self.reasoning_model}")
        self.reasoning_llm = ChatOllama(
            model=self.reasoning_model,
            temperature=0.6,
        )

        # TranslateGemma - for translations only
        logger.info(f"[3/3] Translation: {self.translation_model}")
        self.translation_llm = ChatOllama(
            model=self.translation_model,
            temperature=0.1,
        )

        logger.info("=" * 60)

    def _route_message(self, user_message: str) -> Dict[str, Any]:
        """
        STEP 1: FunctionGemma routes to the right tool (~2-3s)
        """
        logger.info("-" * 50)
        logger.info("STEP 1: FUNCTIONGEMMA (Fast Routing)")
        logger.info("-" * 50)

        messages = [
            {"role": "user", "content": user_message}
        ]

        try:
            logger.info(f"  Routing model: {self.function_model}")
            logger.info(f"  User message: {user_message}")
            logger.info(f"  Available tools: {[tool['function']['name'] for tool in TUTOR_TOOLS]}")
            
            response = ollama.chat(
                model=self.function_model,
                messages=messages,
                tools=TUTOR_TOOLS
            )

            logger.info(f"  Raw routing response: {response}")
            
            if response.message.tool_calls:
                tool_call = response.message.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments

                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except:
                        tool_args = {}

                logger.info(f"  → Tool: {tool_name}")
                logger.info(f"  → Args: {tool_args}")
                return {"tool": tool_name, "args": tool_args}
            else:
                logger.info("  → Tool: chat (default)")
                logger.info(f"  → Direct response: {response.message.content[:100]}...")
                return {"tool": "chat", "args": {}}

        except Exception as e:
            logger.error(f"  Routing error: {e}")
            return {"tool": "chat", "args": {}}

    def _execute_and_respond(self, tool: str, args: Dict, user_message: str,
                              memories: List[str], user_profile: Dict,
                              conversation_history: List[Dict]) -> str:
        """
        STEP 2: Execute tool and generate response in ONE call (~10-15s)
        """
        logger.info("-" * 50)
        logger.info(f"STEP 2: EXECUTE ({tool})")
        logger.info("-" * 50)

        user_name = user_profile.get("user_name", "Student") if user_profile else "Student"
        target_lang = user_profile.get("target_language", "Spanish") if user_profile else "Spanish"

        # Build context
        memory_str = ""
        logger.info(f"  Debug: memories parameter = {memories}")
        logger.info(f"  Debug: type(memories) = {type(memories)}")
        logger.info(f"  Debug: len(memories) if list = {len(memories) if isinstance(memories, list) else 'not a list'}")
        
        if memories:
            memory_str = "Relevant memories about the user:\n" + "\n".join(f"- {mem}" for mem in memories)
            logger.info(f"  Memories being used: {memories}")
            logger.info(f"  Debug: memory_str = '{memory_str}'")
        else:
            logger.info("  Debug: No memories found - memories is falsy")

        conv_str = ""
        if conversation_history:
            # Format conversation for context
            conv_lines = []
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:200]  # Truncate for logging
                conv_lines.append(f"{role}: {content}...")
            conv_str = "\n".join(conv_lines)
            logger.info(f"  Conversation history (last 6): {conv_lines}")

        # System prompt based on tool
        if tool == "translate":
            text = args.get("text", user_message)
            target = args.get("target_language", target_lang)

            logger.info(f"  [TranslateGemma] Translating to {target}")
            prompt = f"Translate to {target}: {text}"

            try:
                response = self.translation_llm.invoke([HumanMessage(content=prompt)])
                translation = response.content.strip()

                # Wrap in friendly tutor response
                return f"Here's the translation to {target}:\n\n**{translation}**\n\nWould you like me to break down any part of this?"
            except Exception as e:
                return f"Sorry, I had trouble translating that: {e}"

        # ALL OTHER TOOLS - Use DeepSeek-R1
        system_prompt = f"""You are a friendly language tutor helping {user_name} learn {target_lang}.

{memory_str}

Be warm, encouraging, and practical. Keep responses concise but helpful."""

        # Build task-specific prompt
        if tool == "teach":
            topic = args.get("topic", user_message)
            lang = args.get("language", target_lang)
            task = f"""Teach about: {topic} in {lang}

Include:
1. The word/phrase with pronunciation
2. Meaning and usage
3. 1-2 example sentences
4. A quick tip

Keep it concise and engaging."""

        elif tool == "exercise":
            ex_type = args.get("type", "mixed")
            lang = args.get("language", target_lang)
            difficulty = args.get("difficulty", "beginner")
            task = f"""Create a quick {difficulty} {lang} exercise.

- 3 questions max
- Include answer key
- Be encouraging"""

        else:  # chat
            task = f"""Student says: "{user_message}"

{conv_str}

Respond naturally as their tutor. Be friendly and helpful."""

        try:
            logger.info(f"  [{self.reasoning_model}] Generating response...")
            logger.info(f"  System prompt: {system_prompt[:200]}...")
            logger.info(f"  User task: {task[:200]}...")
            response = self.reasoning_llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=task)
            ])
            logger.info(f"  Raw response: {response.content[:200]}...")
            return response.content.strip()
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"

    def chat_with_tutor(self, message: str, conversation_history: List[Dict] = None,
                        mem0_memories: List[str] = None, user_profile: Dict = None) -> Dict[str, Any]:
        """
        Main chat method - OPTIMIZED (2 LLM calls)

        1. FunctionGemma routes (~2s)
        2. Execute + Respond (~12s)

        Total: ~15s instead of ~45s
        """
        try:
            logger.info("=" * 60)
            logger.info("TUTOR PIPELINE (Optimized)")
            logger.info("=" * 60)
            logger.info(f"Message: {message}")

            if mem0_memories:
                logger.info(f"Memories: {len(mem0_memories)}")

            # STEP 1: Route (~2s)
            route = self._route_message(message)
            tool = route["tool"]
            args = route["args"]

            # STEP 2: Execute + Respond (~12s)
            response = self._execute_and_respond(
                tool, args, message,
                mem0_memories or [],
                user_profile or {},
                conversation_history or []
            )

            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 60)

            return {
                'success': True,
                'response': response,
                'tool_used': tool if tool != "chat" else None,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}

    # Direct methods for backwards compatibility
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Dict[str, Any]:
        prompt = f"Translate to {target_language}: {text}"
        try:
            response = self.translation_llm.invoke([HumanMessage(content=prompt)])
            return {
                'success': True,
                'translated_text': response.content.strip(),
                'target_language': target_language
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_exercise(self, language: str, difficulty: str = "beginner") -> Dict[str, Any]:
        result = self.chat_with_tutor(
            f"Give me a {difficulty} {language} exercise",
            user_profile={"target_language": language}
        )
        return {
            'success': result.get('success', False),
            'exercise': result.get('response', '')
        }

    def get_langsmith_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.langsmith_client:
            return []
        try:
            runs = list(self.langsmith_client.list_runs(
                project_name=self.langsmith_project,
                limit=limit
            ))
            return [{'id': r.id, 'name': r.name, 'status': r.status} for r in runs]
        except:
            return []
