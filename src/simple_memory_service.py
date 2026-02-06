"""Simple Memory Service using LangChain built-in memory"""

import json
import os
import uuid
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# LangChain imports
from langchain_classic.memory import ConversationBufferWindowMemory


def get_data_dir():
    """Get the writable data directory for the application."""
    if os.name == 'posix':  # macOS/Linux
        app_support = os.path.expanduser('~/Library/Application Support')
        if os.path.exists(app_support):  # macOS
            data_dir = os.path.join(app_support, 'LanguageTutor')
        else:  # Linux
            data_dir = os.path.expanduser('~/.languagetutor')
    else:  # Windows
        data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'LanguageTutor')

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_conversations_dir():
    """Get the directory for storing conversations."""
    conv_dir = os.path.join(get_data_dir(), 'conversations')
    os.makedirs(conv_dir, exist_ok=True)
    return conv_dir


class SimpleMemoryService:
    def __init__(self, user_id: str, memory_window: int = 10):
        """
        Initialize simple memory service using LangChain

        Args:
            user_id: Unique identifier for the user
            memory_window: Number of conversations to keep in memory
        """
        self.user_id = user_id
        self.memory_window = memory_window
        self.logger = logging.getLogger(__name__)
        self.data_dir = get_data_dir()

        # Initialize LangChain conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            return_messages=True,
            memory_key="chat_history"
        )

        # File-based storage for persistence
        self.storage_file = os.path.join(self.data_dir, f"memory_{user_id}.json")
        self._ensure_storage_dir()
        self._load_memory()
        
        self.logger.info(f"Simple Memory Service initialized for user {user_id}")
    
    def _ensure_storage_dir(self):
        """Ensure storage directory exists"""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
    
    def _load_memory(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    
                # Restore conversation history
                for msg_data in data.get('messages', []):
                    if msg_data['type'] == 'human':
                        self.memory.chat_memory.add_user_message(msg_data['content'])
                    elif msg_data['type'] == 'ai':
                        self.memory.chat_memory.add_ai_message(msg_data['content'])
                
                self.logger.info(f"Loaded {len(data.get('messages', []))} messages from storage")
        except Exception as e:
            self.logger.error(f"Failed to load memory: {str(e)}")
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            messages = []
            for message in self.memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    messages.append({
                        'type': 'human',
                        'content': message.content,
                        'timestamp': datetime.now().isoformat()
                    })
                elif isinstance(message, AIMessage):
                    messages.append({
                        'type': 'ai',
                        'content': message.content,
                        'timestamp': datetime.now().isoformat()
                    })
            
            data = {
                'user_id': self.user_id,
                'messages': messages,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save memory: {str(e)}")
    
    def add_conversation(self, messages: List[Dict[str, str]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add conversation to memory
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            metadata: Optional metadata dictionary
        
        Returns:
            Result of memory addition
        """
        try:
            for msg in messages:
                if msg['role'] == 'user':
                    self.memory.chat_memory.add_user_message(msg['content'])
                elif msg['role'] == 'assistant':
                    self.memory.chat_memory.add_ai_message(msg['content'])
            
            # Save to file
            self._save_memory()
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'message_count': len(messages),
                'metadata': metadata or {}
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
        Add translation to memory
        
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
            # Add as a structured conversation
            translation_msg = f"Translation ({source_language} → {target_language}): {original_text} → {translated_text}"
            
            self.memory.chat_memory.add_user_message(f"I want to translate: {original_text}")
            self.memory.chat_memory.add_ai_message(f"Translation: {translated_text}")
            
            # Save to file
            self._save_memory()
            
            # Also save to separate translation log
            self._save_translation_to_log(original_text, translated_text, source_language, target_language, metadata)
            
            return {
                'success': True,
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
    
    def _save_translation_to_log(self, original_text: str, translated_text: str, 
                                source_language: str, target_language: str, 
                                metadata: Optional[Dict[str, Any]] = None):
        """Save translation to separate log file"""
        try:
            log_file = os.path.join(self.data_dir, f"translations_{self.user_id}.json")
            
            translation_entry = {
                'original_text': original_text,
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Load existing translations
            translations = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    translations = json.load(f)
            
            # Add new translation
            translations.append(translation_entry)
            
            # Keep only last 100 translations
            if len(translations) > 100:
                translations = translations[-100:]
            
            # Save
            with open(log_file, 'w') as f:
                json.dump(translations, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save translation log: {str(e)}")
    
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
            exercise_type: Type of exercise
            performance_score: Optional performance score (0-1)
            metadata: Additional metadata
        
        Returns:
            Result of memory addition
        """
        try:
            exercise_msg = f"Completed {difficulty} {exercise_type} exercise in {language}"
            if performance_score is not None:
                exercise_msg += f" (Score: {performance_score:.1%})"
            
            self.memory.chat_memory.add_user_message(f"I completed an exercise")
            self.memory.chat_memory.add_ai_message(f"Great job! {exercise_msg}")
            
            # Save to file
            self._save_memory()
            
            # Also save to exercise log
            self._save_exercise_to_log(language, difficulty, exercise_type, performance_score, metadata)
            
            return {
                'success': True,
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
    
    def _save_exercise_to_log(self, language: str, difficulty: str, exercise_type: str,
                            performance_score: Optional[float], metadata: Optional[Dict[str, Any]]):
        """Save exercise to separate log file"""
        try:
            log_file = os.path.join(self.data_dir, f"exercises_{self.user_id}.json")
            
            exercise_entry = {
                'language': language,
                'difficulty': difficulty,
                'exercise_type': exercise_type,
                'performance_score': performance_score,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Load existing exercises
            exercises = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    exercises = json.load(f)
            
            # Add new exercise
            exercises.append(exercise_entry)
            
            # Keep only last 50 exercises
            if len(exercises) > 50:
                exercises = exercises[-50:]
            
            # Save
            with open(log_file, 'w') as f:
                json.dump(exercises, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save exercise log: {str(e)}")
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Get recent memories (simple keyword-based search)
        
        Args:
            query: Search query
            limit: Maximum number of memories to return
        
        Returns:
            Dictionary with relevant memories
        """
        try:
            # Get recent messages from memory
            messages = self.memory.chat_memory.messages
            
            # Simple keyword matching (since we don't have semantic search)
            relevant_memories = []
            query_lower = query.lower()
            
            for message in messages[-20:]:  # Look at last 20 messages
                content_lower = message.content.lower()
                if any(word in content_lower for word in query_lower.split() if len(word) > 2):
                    relevant_memories.append({
                        'content': message.content,
                        'type': 'human' if isinstance(message, HumanMessage) else 'ai',
                        'timestamp': datetime.now().isoformat()
                    })
            
            return {
                'success': True,
                'memories': relevant_memories[:limit],
                'count': len(relevant_memories[:limit]),
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
        Get learning progress for a specific language
        
        Args:
            language: Language to get progress for
        
        Returns:
            Dictionary with learning progress
        """
        try:
            # Load exercise data
            exercise_file = os.path.join(self.data_dir, f"exercises_{self.user_id}.json")
            exercises = []
            if os.path.exists(exercise_file):
                with open(exercise_file, 'r') as f:
                    exercises = json.load(f)
            
            # Filter by language
            language_exercises = [ex for ex in exercises if ex.get('language') == language]
            
            # Load translation data
            translation_file = os.path.join(self.data_dir, f"translations_{self.user_id}.json")
            translations = []
            if os.path.exists(translation_file):
                with open(translation_file, 'r') as f:
                    translations = json.load(f)
            
            # Calculate statistics
            total_exercises = len(language_exercises)
            avg_performance = 0.0
            
            if language_exercises:
                performance_scores = [
                    ex['performance_score'] for ex in language_exercises
                    if ex.get('performance_score') is not None
                ]
                if performance_scores:
                    avg_performance = sum(performance_scores) / len(performance_scores)
            
            # Get last activity
            all_activities = language_exercises + translations
            last_activity = None
            if all_activities:
                last_activity = max(
                    [activity.get('timestamp', '') for activity in all_activities]
                )
            
            return {
                'success': True,
                'language': language,
                'exercises': language_exercises,
                'translations': translations,
                'statistics': {
                    'total_exercises': total_exercises,
                    'total_translations': len(translations),
                    'average_performance': avg_performance,
                    'last_activity': last_activity
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
        Get translation history
        
        Args:
            source_language: Filter by source language
            target_language: Filter by target language
            limit: Maximum number of translations to return
        
        Returns:
            Dictionary with translation history
        """
        try:
            translation_file = os.path.join(self.data_dir, f"translations_{self.user_id}.json")
            translations = []
            if os.path.exists(translation_file):
                with open(translation_file, 'r') as f:
                    translations = json.load(f)
            
            # Apply filters
            filtered_translations = translations
            if source_language:
                filtered_translations = [
                    t for t in filtered_translations 
                    if t.get('source_language') == source_language
                ]
            if target_language:
                filtered_translations = [
                    t for t in filtered_translations 
                    if t.get('target_language') == target_language
                ]
            
            return {
                'success': True,
                'translations': filtered_translations[-limit:],
                'count': len(filtered_translations[-limit:]),
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
            self.logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def clear_conversation_memory(self):
        """Clear the conversation memory"""
        try:
            self.memory.clear()
            self._save_memory()
            self.logger.info("Conversation memory cleared")
        except Exception as e:
            self.logger.error(f"Error clearing conversation memory: {str(e)}")
    
    def export_memories(self, format: str = "json") -> Dict[str, Any]:
        """
        Export all memories for the user

        Args:
            format: Export format ("json")

        Returns:
            Dictionary with exported data
        """
        try:
            # Collect all data
            memory_data = {
                'conversation_history': self.get_conversation_history(),
                'exercises': [],
                'translations': []
            }

            # Load exercises
            exercise_file = os.path.join(self.data_dir, f"exercises_{self.user_id}.json")
            if os.path.exists(exercise_file):
                with open(exercise_file, 'r') as f:
                    memory_data['exercises'] = json.load(f)

            # Load translations
            translation_file = os.path.join(self.data_dir, f"translations_{self.user_id}.json")
            if os.path.exists(translation_file):
                with open(translation_file, 'r') as f:
                    memory_data['translations'] = json.load(f)

            return {
                'success': True,
                'format': format,
                'data': memory_data,
                'exported_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to export memories: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    # ==================== Conversation Management Methods ====================

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Get list of all conversations for the sidebar.

        Returns:
            List of conversation metadata dictionaries with id, title, created_at
        """
        try:
            conversations = []
            conv_dir = get_conversations_dir()

            # List all conversation files
            for filename in os.listdir(conv_dir):
                if filename.endswith('.json') and filename.startswith('conv_'):
                    filepath = os.path.join(conv_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            conversations.append({
                                'id': data.get('id', filename[5:-5]),  # Remove 'conv_' and '.json'
                                'title': data.get('title', 'New Chat'),
                                'created_at': data.get('created_at', datetime.now().isoformat()),
                                'updated_at': data.get('updated_at', data.get('created_at', datetime.now().isoformat())),
                                'message_count': len(data.get('messages', []))
                            })
                    except Exception as e:
                        self.logger.error(f"Failed to read conversation file {filename}: {e}")

            # Sort by updated_at (most recent first)
            conversations.sort(key=lambda x: x.get('updated_at', ''), reverse=True)

            return conversations

        except Exception as e:
            self.logger.error(f"Failed to get conversations: {e}")
            return []

    def create_new_conversation(self, title: str = "New Chat") -> str:
        """
        Create a new conversation.

        Args:
            title: Initial title for the conversation

        Returns:
            The ID of the new conversation
        """
        try:
            conv_id = str(uuid.uuid4())[:8]  # Short ID for simplicity
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conv_id}.json")

            conversation_data = {
                'id': conv_id,
                'title': title,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'messages': []
            }

            with open(filepath, 'w') as f:
                json.dump(conversation_data, f, indent=2)

            self.logger.info(f"Created new conversation: {conv_id}")
            return conv_id

        except Exception as e:
            self.logger.error(f"Failed to create conversation: {e}")
            raise

    def load_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Load messages from a conversation.

        Args:
            conversation_id: The conversation ID to load

        Returns:
            List of message dictionaries with role, content, timestamp
        """
        try:
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conversation_id}.json")

            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return data.get('messages', [])
            else:
                self.logger.warning(f"Conversation not found: {conversation_id}")
                return []

        except Exception as e:
            self.logger.error(f"Failed to load conversation {conversation_id}: {e}")
            return []

    def add_message_to_conversation(self, conversation_id: str, role: str, content: str) -> bool:
        """
        Add a message to a conversation.

        Args:
            conversation_id: The conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content

        Returns:
            True if successful, False otherwise
        """
        try:
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conversation_id}.json")

            if not os.path.exists(filepath):
                self.logger.error(f"Conversation not found: {conversation_id}")
                return False

            with open(filepath, 'r') as f:
                data = json.load(f)

            message = {
                'id': str(uuid.uuid4()),  # Generate unique ID
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }

            data['messages'].append(message)
            data['updated_at'] = datetime.now().isoformat()

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            self.logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            return False

    def update_conversation_title(self, conversation_id: str, title: str) -> bool:
        """
        Update a conversation's title.

        Args:
            conversation_id: The conversation ID
            title: New title

        Returns:
            True if successful, False otherwise
        """
        try:
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conversation_id}.json")

            if not os.path.exists(filepath):
                self.logger.error(f"Conversation not found: {conversation_id}")
                return False

            with open(filepath, 'r') as f:
                data = json.load(f)

            data['title'] = title
            data['updated_at'] = datetime.now().isoformat()

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True

        except Exception as e:
            self.logger.error(f"Failed to update conversation title {conversation_id}: {e}")
            return False

    def delete_message_from_conversation(self, conversation_id: str, message_id: str) -> bool:
        """
        Delete a specific message from a conversation.

        Args:
            conversation_id: The conversation ID
            message_id: The ID of the message to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conversation_id}.json")

            if not os.path.exists(filepath):
                self.logger.error(f"Conversation not found: {conversation_id}")
                return False

            with open(filepath, 'r') as f:
                data = json.load(f)

            # Find and remove the message
            original_count = len(data['messages'])
            data['messages'] = [msg for msg in data['messages'] if msg.get('id') != message_id]
            
            if len(data['messages']) == original_count:
                self.logger.warning(f"Message {message_id} not found in conversation {conversation_id}")
                return False

            data['updated_at'] = datetime.now().isoformat()

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Deleted message {message_id} from conversation {conversation_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete message from conversation {conversation_id}: {e}")
            return False

    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear all messages from a conversation.

        Args:
            conversation_id: The conversation ID to clear

        Returns:
            True if successful, False otherwise
        """
        try:
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conversation_id}.json")

            if not os.path.exists(filepath):
                self.logger.error(f"Conversation not found: {conversation_id}")
                return False

            with open(filepath, 'r') as f:
                data = json.load(f)

            # Clear all messages but keep metadata
            data['messages'] = []
            data['updated_at'] = datetime.now().isoformat()

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Cleared conversation {conversation_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clear conversation {conversation_id}: {e}")
            return False

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: The conversation ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conv_dir = get_conversations_dir()
            filepath = os.path.join(conv_dir, f"conv_{conversation_id}.json")

            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"Deleted conversation: {conversation_id}")
                return True
            else:
                self.logger.warning(f"Conversation not found: {conversation_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False
