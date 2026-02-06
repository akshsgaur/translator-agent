"""Enhanced Memory Service with LangChain Integration and Mem0"""

import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langsmith import Client as LangSmithClient

# Mem0 imports
from mem0ai import Memory

class EnhancedMemoryService:
    def __init__(self, 
                 user_id: str,
                 langsmith_client: Optional[LangSmithClient] = None,
                 langsmith_project: str = "language-tutor"):
        """
        Initialize enhanced memory service with LangChain and Mem0
        
        Args:
            user_id: Unique identifier for the user
            langsmith_client: LangSmith client for observability
            langsmith_project: LangSmith project name
        """
        self.user_id = user_id
        self.langsmith_client = langsmith_client
        self.langsmith_project = langsmith_project
        
        # Configure Mem0 with Ollama for both LLM and embedder
        config = {
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "mixtral:8x7b",
                    "temperature": 0.1,
                    "max_tokens": 2000,
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "mxbai-embed-large"
                }
            }
        }
        
        try:
            self.memory = Memory.from_config(config)
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"Enhanced Memory Service initialized for user {user_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory service: {str(e)}")
            raise
    
    def add_langchain_conversation(self, 
                                 messages: List[Any], 
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add LangChain conversation to memory
        
        Args:
            messages: List of LangChain message objects (HumanMessage, AIMessage, etc.)
            metadata: Optional metadata dictionary
        
        Returns:
            Result of memory addition
        """
        try:
            # Convert LangChain messages to Mem0 format
            mem0_messages = []
            
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    mem0_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    mem0_messages.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    mem0_messages.append({"role": "system", "content": msg.content})
                else:
                    # Handle other message types
                    mem0_messages.append({"role": "unknown", "content": str(msg)})
            
            # Add default metadata if not provided
            if metadata is None:
                metadata = {
                    "category": "language_learning",
                    "session_type": "chat",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Add to Mem0
            result = self.memory.add(mem0_messages, user_id=self.user_id, metadata=metadata)
            
            # Log to LangSmith if available
            if self.langsmith_client:
                try:
                    self.langsmith_client.create_run(
                        name="memory_add_conversation",
                        inputs={"messages": mem0_messages, "metadata": metadata},
                        outputs={"memory_id": result},
                        project_name=self.langsmith_project
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to log to LangSmith: {str(e)}")
            
            return {
                'success': True,
                'memory_id': result,
                'timestamp': datetime.now().isoformat(),
                'message_count': len(mem0_messages),
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add conversation to memory: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_translation_memory(self, 
                             original_text: str,
                             translated_text: str,
                             source_language: str,
                             target_language: str,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add translation to memory for future reference
        
        Args:
            original_text: Original text
            translated_text: Translated text
            source_language: Source language
            target_language: Target language
            metadata: Additional metadata
        
        Returns:
            Result of memory addition
        """
        try:
            messages = [
                {"role": "user", "content": f"Original ({source_language}): {original_text}"},
                {"role": "assistant", "content": f"Translation ({target_language}): {translated_text}"}
            ]
            
            # Add translation-specific metadata
            translation_metadata = {
                "category": "translation",
                "source_language": source_language,
                "target_language": target_language,
                "original_text": original_text,
                "translated_text": translated_text,
                "timestamp": datetime.now().isoformat()
            }
            
            if metadata:
                translation_metadata.update(metadata)
            
            result = self.memory.add(messages, user_id=self.user_id, metadata=translation_metadata)
            
            return {
                'success': True,
                'memory_id': result,
                'timestamp': datetime.now().isoformat(),
                'source_language': source_language,
                'target_language': target_language
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add translation to memory: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_exercise_completion(self,
                             language: str,
                             difficulty: str,
                             exercise_type: str,
                             performance_score: Optional[float] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add exercise completion to memory
        
        Args:
            language: Language being practiced
            difficulty: Exercise difficulty
            exercise_type: Type of exercise (translation, vocabulary, etc.)
            performance_score: Optional performance score (0-1)
            metadata: Additional metadata
        
        Returns:
            Result of memory addition
        """
        try:
            messages = [
                {"role": "system", "content": f"Exercise completed for {language} language learning"},
                {"role": "user", "content": f"Completed {difficulty} {exercise_type} exercise"}
            ]
            
            exercise_metadata = {
                "category": "exercise_completion",
                "language": language,
                "difficulty": difficulty,
                "exercise_type": exercise_type,
                "performance_score": performance_score,
                "timestamp": datetime.now().isoformat()
            }
            
            if metadata:
                exercise_metadata.update(metadata)
            
            result = self.memory.add(messages, user_id=self.user_id, metadata=exercise_metadata)
            
            return {
                'success': True,
                'memory_id': result,
                'timestamp': datetime.now().isoformat(),
                'language': language,
                'difficulty': difficulty,
                'exercise_type': exercise_type,
                'performance_score': performance_score
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add exercise completion to memory: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant memories based on query
        
        Args:
            query: Search query
            limit: Maximum number of memories to return
        
        Returns:
            Dictionary with relevant memories
        """
        try:
            memories = self.memory.search(query, user_id=self.user_id, limit=limit)
            
            # Log search to LangSmith if available
            if self.langsmith_client:
                try:
                    self.langsmith_client.create_run(
                        name="memory_search",
                        inputs={"query": query, "limit": limit},
                        outputs={"memories_found": len(memories)},
                        project_name=self.langsmith_project
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to log search to LangSmith: {str(e)}")
            
            return {
                'success': True,
                'memories': memories,
                'count': len(memories),
                'query': query
            }
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_learning_progress(self, language: str) -> Dict[str, Any]:
        """
        Get comprehensive learning progress for a specific language
        
        Args:
            language: Language to get progress for
        
        Returns:
            Dictionary with learning progress
        """
        try:
            # Search for different types of memories
            progress_queries = [
                f"progress milestones learning {language}",
                f"exercise completion {language}",
                f"translation {language}",
                f"practice session {language}"
            ]
            
            all_memories = []
            for query in progress_queries:
                result = self.get_relevant_memories(query, limit=20)
                if result['success']:
                    all_memories.extend(result['memories'])
            
            # Categorize memories
            milestones = []
            exercises = []
            translations = []
            sessions = []
            
            for memory in all_memories:
                metadata = memory.get('metadata', {})
                category = metadata.get('category', '')
                
                if category == 'progress_milestone':
                    milestones.append(memory)
                elif category == 'exercise_completion':
                    exercises.append(memory)
                elif category == 'translation':
                    translations.append(memory)
                elif category == 'practice_session':
                    sessions.append(memory)
            
            # Calculate statistics
            total_exercises = len(exercises)
            avg_performance = 0.0
            
            if exercises:
                performance_scores = [
                    ex.get('metadata', {}).get('performance_score', 0)
                    for ex in exercises
                    if ex.get('metadata', {}).get('performance_score') is not None
                ]
                if performance_scores:
                    avg_performance = sum(performance_scores) / len(performance_scores)
            
            return {
                'success': True,
                'language': language,
                'total_memories': len(all_memories),
                'milestones': milestones,
                'exercises': exercises,
                'translations': translations,
                'sessions': sessions,
                'statistics': {
                    'total_exercises': total_exercises,
                    'total_milestones': len(milestones),
                    'total_translations': len(translations),
                    'average_performance': avg_performance,
                    'last_activity': self._get_last_activity(all_memories)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get learning progress: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_translation_history(self, 
                               source_language: Optional[str] = None,
                               target_language: Optional[str] = None,
                               limit: int = 20) -> Dict[str, Any]:
        """
        Get translation history with optional filtering
        
        Args:
            source_language: Filter by source language
            target_language: Filter by target language
            limit: Maximum number of translations to return
        
        Returns:
            Dictionary with translation history
        """
        try:
            # Build search query
            query_parts = ["translation"]
            if source_language:
                query_parts.append(source_language)
            if target_language:
                query_parts.append(target_language)
            
            query = " ".join(query_parts)
            
            result = self.get_relevant_memories(query, limit=limit)
            
            if not result['success']:
                return result
            
            # Filter translations more precisely
            translations = []
            for memory in result['memories']:
                metadata = memory.get('metadata', {})
                if metadata.get('category') == 'translation':
                    # Apply additional filtering if specified
                    if source_language and metadata.get('source_language') != source_language:
                        continue
                    if target_language and metadata.get('target_language') != target_language:
                        continue
                    
                    translations.append(memory)
            
            return {
                'success': True,
                'translations': translations,
                'count': len(translations),
                'filters': {
                    'source_language': source_language,
                    'target_language': target_language
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get translation history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_last_activity(self, memories: List[Dict[str, Any]]) -> Optional[str]:
        """Get the timestamp of the most recent activity"""
        try:
            timestamps = []
            
            for memory in memories:
                metadata = memory.get('metadata', {})
                timestamp = metadata.get('timestamp')
                if timestamp:
                    timestamps.append(timestamp)
            
            if timestamps:
                return max(timestamps)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting last activity: {str(e)}")
            return None
    
    def export_memories(self, format: str = "json") -> Dict[str, Any]:
        """
        Export all memories for the user
        
        Args:
            format: Export format ("json" or "csv")
        
        Returns:
            Dictionary with exported data
        """
        try:
            all_memories = self.memory.get_all(user_id=self.user_id)
            
            if format.lower() == "json":
                return {
                    'success': True,
                    'format': 'json',
                    'data': all_memories,
                    'count': len(all_memories),
                    'exported_at': datetime.now().isoformat()
                }
            elif format.lower() == "csv":
                # Convert to CSV-friendly format
                csv_data = []
                for memory in all_memories:
                    metadata = memory.get('metadata', {})
                    csv_data.append({
                        'memory_id': memory.get('id', ''),
                        'category': metadata.get('category', ''),
                        'language': metadata.get('language', ''),
                        'timestamp': metadata.get('timestamp', ''),
                        'content': str(memory.get('memory', ''))
                    })
                
                return {
                    'success': True,
                    'format': 'csv',
                    'data': csv_data,
                    'count': len(csv_data),
                    'exported_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f"Unsupported format: {format}"
                }
                
        except Exception as e:
            self.logger.error(f"Failed to export memories: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
