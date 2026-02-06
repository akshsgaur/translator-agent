"""User Manager for Language Tutor Application"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List


class UserManager:
    def __init__(self, data_dir: str = None):
        """
        Initialize the user manager.

        Args:
            data_dir: Directory to store user data. Defaults to ~/Library/Application Support/LanguageTutor on macOS.
        """
        if data_dir is None:
            # Use a writable location in the user's home directory
            if os.name == 'posix':  # macOS/Linux
                app_support = os.path.expanduser('~/Library/Application Support')
                if os.path.exists(app_support):  # macOS
                    data_dir = os.path.join(app_support, 'LanguageTutor')
                else:  # Linux
                    data_dir = os.path.expanduser('~/.languagetutor')
            else:  # Windows
                data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'LanguageTutor')

        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self.sessions_file = os.path.join(data_dir, 'sessions.json')

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Load or initialize data
        self.users = self._load_json(self.users_file, {})
        self.sessions = self._load_json(self.sessions_file, {})

    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON file or return default if not exists."""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return default

    def _save_json(self, filepath: str, data: Any):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save to {filepath}: {e}")

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.

        Args:
            username: The username to look up.

        Returns:
            User dict or None if not found.
        """
        for user_id, user_data in self.users.items():
            if user_data.get('username') == username:
                return {'id': user_id, **user_data}
        return None

    def create_user(self, username: str, email: str = None) -> Dict[str, Any]:
        """
        Create a new user.

        Args:
            username: The username for the new user.
            email: Optional email address.

        Returns:
            Dict with 'success' and 'user' or 'error' message.
        """
        # Check if username already exists
        if self.get_user(username):
            return {'success': False, 'error': 'Username already exists'}

        user_id = str(uuid.uuid4())
        user_data = {
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'settings': {
                'native_language': 'English',
                'target_language': 'Spanish',
                'difficulty': 'beginner'
            },
            'stats': {
                'total_sessions': 0,
                'total_translations': 0,
                'total_exercises': 0,
                'streak_days': 0
            }
        }

        self.users[user_id] = user_data
        self._save_json(self.users_file, self.users)

        return {'success': True, 'user': {'id': user_id, **user_data}}

    def update_last_login(self, user_id: str):
        """Update the last login timestamp for a user."""
        if user_id in self.users:
            self.users[user_id]['last_login'] = datetime.now().isoformat()
            self._save_json(self.users_file, self.users)

    def update_user_settings(self, user_id: str, settings: Dict[str, Any]):
        """Update user settings."""
        if user_id in self.users:
            self.users[user_id]['settings'].update(settings)
            self._save_json(self.users_file, self.users)

    def start_learning_session(self, user_id: str, target_language: str = None,
                                difficulty: str = None) -> str:
        """
        Start a new learning session.

        Args:
            user_id: The user's ID.
            target_language: Language being learned.
            difficulty: Session difficulty level.

        Returns:
            Session ID.
        """
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'started_at': datetime.now().isoformat(),
            'ended_at': None,
            'target_language': target_language,
            'difficulty': difficulty,
            'activities': [],
            'stats': {
                'translations': 0,
                'exercises_completed': 0,
                'messages': 0
            }
        }

        self.sessions[session_id] = session_data
        self._save_json(self.sessions_file, self.sessions)

        # Update user stats
        if user_id in self.users:
            self.users[user_id]['stats']['total_sessions'] += 1
            self._save_json(self.users_file, self.users)

        return session_id

    def end_learning_session(self, session_id: str):
        """End a learning session."""
        if session_id in self.sessions:
            self.sessions[session_id]['ended_at'] = datetime.now().isoformat()
            self._save_json(self.sessions_file, self.sessions)

    def log_activity(self, session_id: str, activity_type: str, data: Dict[str, Any] = None):
        """Log an activity within a session."""
        if session_id in self.sessions:
            activity = {
                'type': activity_type,
                'timestamp': datetime.now().isoformat(),
                'data': data or {}
            }
            self.sessions[session_id]['activities'].append(activity)

            # Update stats
            if activity_type == 'translation':
                self.sessions[session_id]['stats']['translations'] += 1
            elif activity_type == 'exercise':
                self.sessions[session_id]['stats']['exercises_completed'] += 1
            elif activity_type == 'message':
                self.sessions[session_id]['stats']['messages'] += 1

            self._save_json(self.sessions_file, self.sessions)

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get aggregated stats for a user."""
        if user_id not in self.users:
            return {}

        user_stats = self.users[user_id].get('stats', {}).copy()

        # Calculate session stats
        user_sessions = [s for s in self.sessions.values() if s['user_id'] == user_id]
        user_stats['recent_sessions'] = len([
            s for s in user_sessions
            if s.get('started_at', '')[:10] == datetime.now().isoformat()[:10]
        ])

        return user_stats

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        return [{'id': uid, **data} for uid, data in self.users.items()]
