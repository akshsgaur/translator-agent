"""
Ollama-Style Language Tutor Application
A clean, modern chat interface for language learning
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import threading
import logging
import json
import os

# Mem0 for semantic memory
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    try:
        from mem0ai import Memory
        MEM0_AVAILABLE = True
    except ImportError:
        MEM0_AVAILABLE = False
        Memory = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_data_dir():
    """Get the data directory for the application."""
    if os.name == 'posix':
        app_support = os.path.expanduser('~/Library/Application Support')
        if os.path.exists(app_support):
            data_dir = os.path.join(app_support, 'LanguageTutor')
        else:
            data_dir = os.path.expanduser('~/.languagetutor')
    else:
        data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'LanguageTutor')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_user_profile() -> Optional[Dict[str, Any]]:
    """Load user profile if it exists."""
    profile_path = os.path.join(get_data_dir(), 'profile.json')
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r') as f:
                return json.load(f)
        except:
            return None
    return None


def save_user_profile(profile: Dict[str, Any]):
    """Save user profile."""
    profile_path = os.path.join(get_data_dir(), 'profile.json')
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)

# Color scheme (Ollama-inspired dark theme)
COLORS = {
    "bg_dark": "#0d0d0d",
    "bg_sidebar": "#171717",
    "bg_chat": "#1a1a1a",
    "bg_input": "#262626",
    "bg_hover": "#2a2a2a",
    "bg_selected": "#333333",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "text_muted": "#666666",
    "accent": "#10a37f",
    "accent_hover": "#0d8c6d",
    "border": "#333333",
    "user_bubble": "#2d2d2d",
    "assistant_bubble": "#1e1e1e",
}

# Supported languages
SUPPORTED_LANGUAGES = [
    "Spanish", "French", "German", "Italian",
    "Portuguese", "Russian", "Chinese", "Japanese"
]

# Available models
AVAILABLE_MODELS = [
    "llama3",
    "translategemma:4b",
    "llama3.2",
    "gemma2:9b",
]


class ConversationItem(ctk.CTkFrame):
    """A single conversation item in the sidebar"""

    def __init__(self, master, conversation_id: str, title: str,
                 timestamp: str, on_click: Callable, on_delete: Callable,
                 is_selected: bool = False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.conversation_id = conversation_id
        self.on_click = on_click
        self.on_delete = on_delete
        self.is_selected = is_selected

        self.configure(cursor="hand2")

        # Container frame
        self.container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_selected"] if is_selected else "transparent",
            corner_radius=8
        )
        self.container.pack(fill="x", padx=5, pady=2)

        # Title label
        self.title_label = ctk.CTkLabel(
            self.container,
            text=title[:30] + "..." if len(title) > 30 else title,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"] if is_selected else COLORS["text_secondary"],
            anchor="w"
        )
        self.title_label.pack(fill="x", padx=10, pady=(8, 2))

        # Timestamp label
        self.time_label = ctk.CTkLabel(
            self.container,
            text=self._format_timestamp(timestamp),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.time_label.pack(fill="x", padx=10, pady=(0, 8))

        # Bind click events
        for widget in [self, self.container, self.title_label, self.time_label]:
            widget.bind("<Button-1>", lambda e: self.on_click(self.conversation_id))
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp)
            now = datetime.now()
            delta = now - dt

            if delta < timedelta(minutes=1):
                return "Just now"
            elif delta < timedelta(hours=1):
                mins = int(delta.total_seconds() / 60)
                return f"{mins}m ago"
            elif delta < timedelta(days=1):
                hours = int(delta.total_seconds() / 3600)
                return f"{hours}h ago"
            elif delta < timedelta(days=7):
                return dt.strftime("%A")
            else:
                return dt.strftime("%b %d")
        except:
            return ""

    def _on_enter(self, event):
        if not self.is_selected:
            self.container.configure(fg_color=COLORS["bg_hover"])

    def _on_leave(self, event):
        if not self.is_selected:
            self.container.configure(fg_color="transparent")

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.container.configure(
            fg_color=COLORS["bg_selected"] if selected else "transparent"
        )
        self.title_label.configure(
            text_color=COLORS["text_primary"] if selected else COLORS["text_secondary"]
        )


class ChatMessage(ctk.CTkFrame):
    """A single chat message bubble"""

    def __init__(self, master, role: str, content: str, timestamp: str = None, 
                 message_id: str = None, on_delete: Callable = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.role = role
        self.message_id = message_id
        self.on_delete = on_delete
        is_user = role == "user"

        # Message container
        self.bubble = ctk.CTkFrame(
            self,
            fg_color=COLORS["user_bubble"] if is_user else COLORS["assistant_bubble"],
            corner_radius=12
        )

        # Position bubble based on role
        if is_user:
            self.bubble.pack(anchor="e", padx=(50, 10), pady=5)
        else:
            self.bubble.pack(anchor="w", padx=(10, 50), pady=5)

        # Header with role and delete button
        header_frame = ctk.CTkFrame(self.bubble, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(10, 2))

        # Role label
        role_text = "You" if is_user else "Tutor"
        self.role_label = ctk.CTkLabel(
            header_frame,
            text=role_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["accent"] if not is_user else COLORS["text_secondary"],
            anchor="w"
        )
        self.role_label.pack(side="left")

        # Delete button
        if self.on_delete and self.message_id:
            self.delete_btn = ctk.CTkButton(
                header_frame,
                text="×",
                width=20,
                height=20,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                text_color=COLORS["text_muted"],
                hover_color=COLORS["bg_hover"],
                corner_radius=10,
                command=self._delete_message
            )
            self.delete_btn.pack(side="right", padx=(5, 0))

        # Message content
        self.content_label = ctk.CTkLabel(
            self.bubble,
            text=content,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_primary"],
            anchor="w",
            justify="left",
            wraplength=500
        )
        self.content_label.pack(fill="x", padx=12, pady=(2, 10))

    def _delete_message(self):
        """Handle message deletion"""
        if self.on_delete and self.message_id:
            self.on_delete(self.message_id)


class Sidebar(ctk.CTkFrame):
    """Left sidebar with conversation history"""

    def __init__(self, master, on_new_chat: Callable, on_select_chat: Callable,
                 on_delete_chat: Callable, on_settings: Callable, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_sidebar"], width=250, **kwargs)

        self.on_new_chat = on_new_chat
        self.on_select_chat = on_select_chat
        self.on_delete_chat = on_delete_chat
        self.on_settings = on_settings
        self.conversation_items: Dict[str, ConversationItem] = {}
        self.current_conversation_id: Optional[str] = None

        self.pack_propagate(False)

        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.header.pack(fill="x", padx=10, pady=10)
        self.header.pack_propagate(False)

        # App title
        self.title_label = ctk.CTkLabel(
            self.header,
            text="Language Tutor",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.pack(anchor="w", pady=(5, 0))

        # New Chat button
        self.new_chat_btn = ctk.CTkButton(
            self,
            text="+ New Chat",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            height=40,
            corner_radius=8,
            command=self.on_new_chat
        )
        self.new_chat_btn.pack(fill="x", padx=10, pady=(0, 10))

        # Conversations list container
        self.conversations_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_hover"],
            scrollbar_button_hover_color=COLORS["border"]
        )
        self.conversations_container.pack(fill="both", expand=True, padx=5)

        # Today section
        self.today_label = ctk.CTkLabel(
            self.conversations_container,
            text="Today",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.today_label.pack(fill="x", padx=10, pady=(10, 5))

        # Today conversations frame
        self.today_frame = ctk.CTkFrame(self.conversations_container, fg_color="transparent")
        self.today_frame.pack(fill="x")

        # This Week section
        self.week_label = ctk.CTkLabel(
            self.conversations_container,
            text="This Week",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.week_label.pack(fill="x", padx=10, pady=(15, 5))

        # Week conversations frame
        self.week_frame = ctk.CTkFrame(self.conversations_container, fg_color="transparent")
        self.week_frame.pack(fill="x")

        # Older section
        self.older_label = ctk.CTkLabel(
            self.conversations_container,
            text="Older",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text_muted"],
            anchor="w"
        )
        self.older_label.pack(fill="x", padx=10, pady=(15, 5))

        # Older conversations frame
        self.older_frame = ctk.CTkFrame(self.conversations_container, fg_color="transparent")
        self.older_frame.pack(fill="x")

        # Bottom settings button
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.settings_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        self.settings_frame.pack_propagate(False)

        self.settings_btn = ctk.CTkButton(
            self.settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            height=35,
            corner_radius=8,
            anchor="w",
            command=self.on_settings
        )
        self.settings_btn.pack(fill="x")

    def update_conversations(self, conversations: List[Dict[str, Any]],
                            current_id: Optional[str] = None):
        """Update the conversation list"""
        self.current_conversation_id = current_id

        # Clear existing items
        for item in self.conversation_items.values():
            item.destroy()
        self.conversation_items.clear()

        # Group conversations by date
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())

        for conv in conversations:
            conv_id = conv.get("id", "")
            title = conv.get("title", "New Chat")
            timestamp = conv.get("created_at", now.isoformat())

            try:
                conv_time = datetime.fromisoformat(timestamp)
            except:
                conv_time = now

            # Determine which section
            if conv_time >= today_start:
                parent = self.today_frame
            elif conv_time >= week_start:
                parent = self.week_frame
            else:
                parent = self.older_frame

            # Create conversation item
            item = ConversationItem(
                parent,
                conversation_id=conv_id,
                title=title,
                timestamp=timestamp,
                on_click=self._on_conversation_click,
                on_delete=self.on_delete_chat,
                is_selected=(conv_id == current_id)
            )
            item.pack(fill="x")
            self.conversation_items[conv_id] = item

    def _on_conversation_click(self, conversation_id: str):
        """Handle conversation click"""
        # Update selection visuals
        for cid, item in self.conversation_items.items():
            item.set_selected(cid == conversation_id)
        self.current_conversation_id = conversation_id
        self.on_select_chat(conversation_id)


class ChatArea(ctk.CTkFrame):
    """Main chat display area with scrolling"""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_chat"], **kwargs)

        # Use CTkScrollableFrame with proper mousewheel support
        self.messages_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#666666",
            scrollbar_button_hover_color="#888888"
        )
        self.messages_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Simple mousewheel binding that works
        def _on_mousewheel(event):
            if event.delta:
                # macOS
                self.messages_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Linux/Windows
                self.messages_frame._parent_canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

        # Bind to the canvas directly
        self.messages_frame._parent_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.messages_frame._parent_canvas.bind("<Button-4>", _on_mousewheel)
        self.messages_frame._parent_canvas.bind("<Button-5>", _on_mousewheel)

        # Welcome message (shown when empty)
        self.welcome_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        self.welcome_label = ctk.CTkLabel(
            self.welcome_frame,
            text="Language Tutor",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.welcome_label.pack(pady=(100, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.welcome_frame,
            text="Your personal AI language learning assistant",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_secondary"]
        )
        self.subtitle_label.pack(pady=(0, 20))

        self.hint_label = ctk.CTkLabel(
            self.welcome_frame,
            text="Start by typing a message below.\nAsk for translations, practice conversations, or get grammar help!",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_muted"],
            justify="center"
        )
        self.hint_label.pack()

        self.welcome_frame.pack(fill="both", expand=True)

        self.message_widgets: List[ChatMessage] = []

    def show_welcome(self):
        """Show welcome message"""
        self.welcome_frame.pack(fill="both", expand=True)

    def hide_welcome(self):
        """Hide welcome message"""
        self.welcome_frame.pack_forget()

    def add_message(self, role: str, content: str, timestamp: str = None, message_id: str = None):
        """Add a message to the chat"""
        if self.message_widgets == []:
            self.hide_welcome()

        msg = ChatMessage(
            self.messages_frame,  # Add to messages_frame
            role=role,
            content=content,
            timestamp=timestamp,
            message_id=message_id,
            on_delete=self._delete_message
        )
        msg.pack(fill="x", padx=5, pady=2)
        self.message_widgets.append(msg)

        # Scroll to bottom
        self.after(50, self._scroll_to_bottom)

    def _delete_message(self, message_id: str):
        """Delete a specific message"""
        # Find and remove the message widget
        for i, msg_widget in enumerate(self.message_widgets):
            if msg_widget.message_id == message_id:
                msg_widget.destroy()
                self.message_widgets.pop(i)
                break
        
        # Notify parent to delete from storage
        if hasattr(self, 'on_delete_message'):
            self.on_delete_message(message_id)

    def clear_messages(self):
        """Clear all messages"""
        for msg in self.message_widgets:
            msg.destroy()
        self.message_widgets.clear()
        self.show_welcome()

    def load_messages(self, messages: List[Dict[str, Any]]):
        """Load messages into the chat"""
        self.clear_messages()
        for msg in messages:
            self.add_message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp"),
                message_id=msg.get("id")
            )

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        self.messages_frame.update_idletasks()
        self.messages_frame._parent_canvas.yview_moveto(1.0)


class InputBar(ctk.CTkFrame):
    """Bottom input bar with text entry and controls"""

    def __init__(self, master, on_send: Callable, models: List[str], on_clear_chat: Callable = None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_chat"], **kwargs)

        self.on_send = on_send
        self.on_clear_chat = on_clear_chat
        self.min_height = 45
        self.max_height = 150

        # Inner container
        self.container = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_input"],
            corner_radius=12
        )
        self.container.pack(fill="x", padx=20, pady=15)

        # Text input - auto-resizing
        self.text_input = ctk.CTkTextbox(
            self.container,
            height=self.min_height,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            border_width=0,
            wrap="word"
        )
        self.text_input.pack(side="left", fill="both", expand=True, padx=(15, 10), pady=8)
        self.text_input.bind("<Return>", self._on_enter)
        self.text_input.bind("<Shift-Return>", lambda e: None)  # Allow shift+enter for newline
        self.text_input.bind("<KeyRelease>", self._auto_resize)

        # Controls frame
        self.controls = ctk.CTkFrame(self.container, fg_color="transparent")
        self.controls.pack(side="right", padx=(0, 10), pady=8)

        # Model selector
        self.model_var = ctk.StringVar(value=models[0] if models else "translategemma:4b")
        self.model_dropdown = ctk.CTkOptionMenu(
            self.controls,
            values=models if models else AVAILABLE_MODELS,
            variable=self.model_var,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_hover"],
            button_color=COLORS["bg_hover"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["bg_sidebar"],
            dropdown_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"],
            width=140,
            height=30,
            corner_radius=6
        )
        self.model_dropdown.pack(side="left", padx=(0, 10))

        # Clear chat button
        if self.on_clear_chat:
            self.clear_btn = ctk.CTkButton(
                self.controls,
                text="Clear",
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["bg_hover"],
                hover_color=COLORS["border"],
                text_color=COLORS["text_secondary"],
                width=50,
                height=30,
                corner_radius=6,
                command=self.on_clear_chat
            )
            self.clear_btn.pack(side="left", padx=(0, 10))

        # Send button
        self.send_btn = ctk.CTkButton(
            self.controls,
            text="Send",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_primary"],
            width=70,
            height=35,
            corner_radius=8,
            command=self._send_message
        )
        self.send_btn.pack(side="left")

    def _on_enter(self, event):
        """Handle enter key"""
        if not event.state & 0x1:  # Shift not pressed
            self._send_message()
            return "break"

    def _auto_resize(self, event=None):
        """Auto-resize input based on content"""
        content = self.text_input.get("1.0", "end-1c")
        # Count actual lines including wrapped lines
        lines = content.count('\n') + 1

        # Estimate wrapped lines based on content length per line (~60 chars per line)
        if content:
            for line in content.split('\n'):
                extra_lines = len(line) // 60
                lines += extra_lines

        # Calculate height: ~24px per line, with padding
        new_height = min(self.max_height, max(self.min_height, lines * 24))

        # Update textbox height
        self.text_input.configure(height=new_height)

        # Update container height to match
        container_height = new_height + 16  # Add padding
        self.container.configure(height=container_height)

    def _send_message(self):
        """Send the current message"""
        message = self.text_input.get("1.0", "end-1c").strip()
        if message:
            self.text_input.delete("1.0", "end")
            # Reset heights
            self.text_input.configure(height=self.min_height)
            self.container.configure(height=self.min_height + 16)
            self.on_send(message, self.model_var.get())

    def get_selected_model(self) -> str:
        """Get the currently selected model"""
        return self.model_var.get()

    def set_enabled(self, enabled: bool):
        """Enable or disable the input"""
        state = "normal" if enabled else "disabled"
        self.text_input.configure(state=state)
        self.send_btn.configure(state=state)


class WelcomeDialog(ctk.CTkToplevel):
    """Welcome dialog for first-time users to enter their name"""

    def __init__(self, master, on_complete: Callable, **kwargs):
        super().__init__(master, **kwargs)

        self.on_complete = on_complete
        self.user_name = None
        self.target_language = None

        self.title("Welcome to Language Tutor")
        self.geometry("450x400")
        self.configure(fg_color=COLORS["bg_dark"])

        # Make modal
        self.transient(master)
        self.grab_set()

        # Prevent closing without entering name
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 400) // 2
        self.geometry(f"+{x}+{y}")

        # Welcome message
        self.title_label = ctk.CTkLabel(
            self,
            text="Welcome to Language Tutor",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.pack(pady=(40, 10))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Your personal AI language learning assistant",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.subtitle_label.pack(pady=(0, 30))

        # Name input
        self.name_label = ctk.CTkLabel(
            self,
            text="What should I call you?",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_primary"]
        )
        self.name_label.pack(pady=(0, 10))

        self.name_entry = ctk.CTkEntry(
            self,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"],
            placeholder_text="Enter your name..."
        )
        self.name_entry.pack(pady=(0, 20))
        self.name_entry.bind("<Return>", lambda e: self._submit())

        # Language selection
        self.language_label = ctk.CTkLabel(
            self,
            text="What language do you want to learn?",
            font=ctk.CTkFont(size=16),
            text_color=COLORS["text_primary"]
        )
        self.language_label.pack(pady=(10, 10))

        # List of popular languages
        languages = [
            "Spanish",
            "French", 
            "German",
            "Italian",
            "Portuguese",
            "Chinese (Mandarin)",
            "Japanese",
            "Korean",
            "Russian",
            "Arabic",
            "Hindi",
            "Dutch",
            "Swedish",
            "Polish",
            "Turkish"
        ]

        self.language_dropdown = ctk.CTkOptionMenu(
            self,
            values=languages,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_input"],
            dropdown_text_color=COLORS["text_primary"]
        )
        self.language_dropdown.pack(pady=(0, 20))
        self.language_dropdown.set("Spanish")  # Default selection

        # Start button
        self.start_btn = ctk.CTkButton(
            self,
            text="Start Learning",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_primary"],
            width=150,
            height=40,
            corner_radius=8,
            command=self._submit
        )
        self.start_btn.pack()

        # Focus on entry
        self.after(100, lambda: self.name_entry.focus())

    def _submit(self):
        name = self.name_entry.get().strip()
        language = self.language_dropdown.get()
        
        if name:
            self.user_name = name
            self.target_language = language
            # Create profile
            profile = {
                "user_name": name,
                "user_id": name.lower().replace(" ", "_"),
                "created_at": datetime.now().isoformat(),
                "target_language": language
            }
            save_user_profile(profile)
            logger.info(f"Created profile for user: {name}, learning {language}")
            self.on_complete(profile)
            self.destroy()

    def _on_close(self):
        # Don't allow closing without a name
        pass


class SettingsPanel(ctk.CTkToplevel):
    """Settings panel as a modal dialog"""

    def __init__(self, master, current_language: str, on_save: Callable, **kwargs):
        super().__init__(master, **kwargs)

        self.on_save = on_save

        self.title("Settings")
        self.geometry("400x300")
        self.configure(fg_color=COLORS["bg_sidebar"])

        # Make modal
        self.transient(master)
        self.grab_set()

        # Center on parent
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 400) // 2
        y = master.winfo_y() + (master.winfo_height() - 300) // 2
        self.geometry(f"+{x}+{y}")

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.title_label.pack(pady=(20, 20))

        # Target language selector
        self.lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.lang_frame.pack(fill="x", padx=30, pady=10)

        self.lang_label = ctk.CTkLabel(
            self.lang_frame,
            text="Target Language",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"]
        )
        self.lang_label.pack(anchor="w")

        self.lang_var = ctk.StringVar(value=current_language)
        self.lang_dropdown = ctk.CTkOptionMenu(
            self.lang_frame,
            values=SUPPORTED_LANGUAGES,
            variable=self.lang_var,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_input"],
            button_color=COLORS["bg_input"],
            button_hover_color=COLORS["bg_hover"],
            dropdown_fg_color=COLORS["bg_sidebar"],
            dropdown_hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_primary"],
            width=200,
            height=35
        )
        self.lang_dropdown.pack(anchor="w", pady=(5, 0))

        # Save button
        self.save_btn = ctk.CTkButton(
            self,
            text="Save Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_primary"],
            width=150,
            height=40,
            corner_radius=8,
            command=self._save
        )
        self.save_btn.pack(pady=30)

    def _save(self):
        """Save settings and close"""
        self.on_save(self.lang_var.get())
        self.destroy()


class TutorApp(ctk.CTk):
    """Main Ollama-style Language Tutor Application"""

    def __init__(self, langsmith_api_key: Optional[str] = None):
        super().__init__()

        self.langsmith_api_key = langsmith_api_key
        self.user_profile: Optional[Dict[str, Any]] = None

        # Configure window
        self.title("Language Tutor")
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.configure(fg_color=COLORS["bg_dark"])

        # Check for existing profile
        self.user_profile = get_user_profile()

        if self.user_profile:
            # Existing user - initialize normally
            logger.info(f"Welcome back, {self.user_profile.get('user_name', 'User')}!")
            self._initialize_app()
        else:
            # New user - show welcome dialog first
            logger.info("First time user - showing welcome dialog")
            self.after(100, self._show_welcome_dialog)

    def _show_welcome_dialog(self):
        """Show welcome dialog for first-time users"""
        WelcomeDialog(self, on_complete=self._on_profile_created)

    def _on_profile_created(self, profile: Dict[str, Any]):
        """Called when user completes the welcome dialog"""
        self.user_profile = profile
        logger.info(f"Profile created for: {profile.get('user_name')}")
        self._initialize_app()

    def _initialize_app(self):
        """Initialize the app after profile is available"""
        # Set user_id from profile
        self.user_id = self.user_profile.get("user_id", "local_user") if self.user_profile else "local_user"

        # Initialize services
        self._init_services()

        # State
        self.current_conversation_id: Optional[str] = None
        self.target_language = self.user_profile.get("target_language", "Spanish") if self.user_profile else "Spanish"
        self.is_processing = False

        # Build UI
        self._build_ui()

        # Load initial data
        self._load_conversations()

        logger.info("TutorApp initialized")

    def _init_services(self):
        """Initialize backend services"""
        try:
            # Get user_id from profile
            user_id = self.user_profile.get("user_id", "local_user") if self.user_profile else "local_user"
            user_name = self.user_profile.get("user_name", "User") if self.user_profile else "User"

            logger.info("=" * 60)
            logger.info("INITIALIZING SERVICES")
            logger.info(f"User: {user_name} (ID: {user_id})")
            logger.info("=" * 60)

            from simple_memory_service import SimpleMemoryService
            from langchain_service import LangChainTutorService

            # Initialize memory service with user's ID
            logger.info("[1/3] Initializing SimpleMemoryService...")
            logger.info(f"      User ID: {user_id}")
            logger.info("      Storage: File-based JSON in ~/Library/Application Support/LanguageTutor/")
            self.memory_service = SimpleMemoryService(user_id=user_id)
            logger.info("      SimpleMemoryService ready")

            # Initialize tutor service
            logger.info("[2/3] Initializing LangChainTutorService...")
            logger.info("      LangSmith API Key: " + ("configured" if self.langsmith_api_key else "not set"))
            self.tutor_service = LangChainTutorService(
                langsmith_api_key=self.langsmith_api_key
            )
            logger.info("      LangChainTutorService ready")

            # Store user_id for Mem0 operations
            self.user_id = user_id

            # Initialize Mem0 for semantic memory
            logger.info("[3/3] Initializing Mem0 Semantic Memory...")
            self.mem0 = None
            if MEM0_AVAILABLE:
                try:
                    from simple_memory_service import get_data_dir as get_mem_data_dir
                    mem0_db_path = os.path.join(get_mem_data_dir(), "mem0_db")
                    os.makedirs(mem0_db_path, exist_ok=True)

                    logger.info("      Mem0 Configuration:")
                    logger.info(f"        User ID: {user_id}")
                    logger.info("        LLM Provider: Ollama")
                    logger.info("        LLM Model: llama3")
                    logger.info("        Embedder Provider: Ollama")
                    logger.info("        Embedder Model: mxbai-embed-large (1024 dims)")
                    logger.info("        Vector Store: ChromaDB")
                    logger.info(f"        Vector Store Path: {mem0_db_path}")

                    mem0_config = {
                        "llm": {
                            "provider": "ollama",
                            "config": {
                                "model": "llama3",
                                "temperature": 0.1,
                                "max_tokens": 2000,
                            }
                        },
                        "embedder": {
                            "provider": "ollama",
                            "config": {
                                "model": "mxbai-embed-large",
                                "embedding_dims": 1024
                            }
                        },
                        "vector_store": {
                            "provider": "chroma",
                            "config": {
                                "collection_name": "language_tutor",
                                "path": mem0_db_path,
                            }
                        },
                        "version": "v1.1"
                    }
                    logger.info("      Calling Memory.from_config()...")
                    self.mem0 = Memory.from_config(mem0_config)
                    logger.info("      Mem0 ready for semantic memory storage and retrieval")
                except Exception as e:
                    logger.warning(f"      Mem0 initialization failed: {e}")
                    logger.warning("      Continuing without semantic memory")
                    self.mem0 = None
            else:
                logger.warning("      Mem0 not available - install with: pip install mem0ai")

            logger.info("=" * 60)
            logger.info("ALL SERVICES INITIALIZED SUCCESSFULLY")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            self.memory_service = None
            self.tutor_service = None
            self.mem0 = None

    def _build_ui(self):
        """Build the main UI"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = Sidebar(
            self.main_container,
            on_new_chat=self._new_chat,
            on_select_chat=self._select_conversation,
            on_delete_chat=self._delete_conversation,
            on_settings=self._show_settings
        )
        self.sidebar.pack(side="left", fill="y")

        # Update title with user's name
        if self.user_profile:
            user_name = self.user_profile.get("user_name", "User")
            self.sidebar.title_label.configure(text=f"Hi, {user_name}!")

        # Right side container
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_container.pack(side="left", fill="both", expand=True)

        # Chat area
        self.chat_area = ChatArea(self.right_container)
        self.chat_area.pack(fill="both", expand=True)
        
        # Connect delete message callback
        self.chat_area.on_delete_message = self._delete_message

        # Input bar
        self.input_bar = InputBar(
            self.right_container,
            on_send=self._send_message,
            models=AVAILABLE_MODELS,
            on_clear_chat=self._clear_chat
        )
        self.input_bar.pack(fill="x", side="bottom")

    def _load_conversations(self):
        """Load conversations into sidebar"""
        if not self.memory_service:
            return

        try:
            conversations = self.memory_service.get_all_conversations()
            self.sidebar.update_conversations(
                conversations,
                self.current_conversation_id
            )

            # Auto-select first conversation or create new one
            if conversations and not self.current_conversation_id:
                self._select_conversation(conversations[0]["id"])
            elif not conversations:
                self._new_chat()

        except Exception as e:
            logger.error(f"Failed to load conversations: {e}")

    def _new_chat(self):
        """Create a new chat conversation"""
        if not self.memory_service:
            return

        try:
            conv_id = self.memory_service.create_new_conversation()
            self.current_conversation_id = conv_id
            self.chat_area.clear_messages()
            self._load_conversations()
            logger.info(f"Created new conversation: {conv_id}")
        except Exception as e:
            logger.error(f"Failed to create new chat: {e}")

    def _select_conversation(self, conversation_id: str):
        """Switch to a different conversation"""
        if not self.memory_service:
            return

        try:
            self.current_conversation_id = conversation_id
            messages = self.memory_service.load_conversation(conversation_id)
            self.chat_area.load_messages(messages)
            self.sidebar.update_conversations(
                self.memory_service.get_all_conversations(),
                conversation_id
            )
            logger.info(f"Switched to conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to select conversation: {e}")

    def _delete_conversation(self, conversation_id: str):
        """Delete a conversation"""
        if not self.memory_service:
            return

        try:
            self.memory_service.delete_conversation(conversation_id)

            # If deleted current conversation, switch to another
            if conversation_id == self.current_conversation_id:
                conversations = self.memory_service.get_all_conversations()
                if conversations:
                    self._select_conversation(conversations[0]["id"])
                else:
                    self._new_chat()
            else:
                self._load_conversations()

            logger.info(f"Deleted conversation: {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to delete conversation: {e}")

    def _send_message(self, message: str, model: str):
        """Send a message and get response"""
        if self.is_processing or not message.strip():
            return

        if not self.tutor_service:
            self.chat_area.add_message(
                "assistant",
                "Sorry, the tutor service is not available. Please check if Ollama is running."
            )
            return

        self.is_processing = True
        self.input_bar.set_enabled(False)

        # Add user message to UI
        self.chat_area.add_message("user", message)

        # Save user message
        if self.memory_service and self.current_conversation_id:
            self.memory_service.add_message_to_conversation(
                self.current_conversation_id,
                "user",
                message
            )

        # Get conversation history for context
        conversation_history = []
        if self.memory_service and self.current_conversation_id:
            conversation_history = self.memory_service.load_conversation(self.current_conversation_id)

        # Get relevant memories from Mem0
        mem0_memories = []
        logger.info("=" * 60)
        logger.info("STEP 1: User sends message")
        logger.info(f"  User message: {message}")
        logger.info("=" * 60)

        logger.info("STEP 2: Searching Mem0 for relevant memories")
        logger.info(f"  Query: '{message}'")
        logger.info(f"  User ID: '{self.user_id}'")
        if self.mem0:
            try:
                logger.info("  Calling Mem0.search()...")
                mem0_results = self.mem0.search(query=message, user_id=self.user_id, limit=5)
                logger.info(f"  Mem0 raw response type: {type(mem0_results)}")
                logger.info(f"  Mem0 raw response: {mem0_results}")

                # Handle different response formats from Mem0
                results_list = []
                if isinstance(mem0_results, dict):
                    # Response might be {'results': [...]} or {'memories': [...]}
                    results_list = mem0_results.get("results", mem0_results.get("memories", []))
                elif isinstance(mem0_results, list):
                    results_list = mem0_results
                else:
                    logger.warning(f"  Unexpected Mem0 response type: {type(mem0_results)}")

                logger.info(f"  Mem0 returned {len(results_list)} results")

                if results_list:
                    for i, m in enumerate(results_list):
                        # Handle both dict and string results
                        if isinstance(m, dict):
                            memory_text = m.get("memory", m.get("text", ""))
                            score = m.get("score", m.get("similarity", "N/A"))
                        elif isinstance(m, str):
                            memory_text = m
                            score = "N/A"
                        else:
                            memory_text = str(m)
                            score = "N/A"
                        logger.info(f"  Memory {i+1}: '{memory_text}' (score: {score})")
                        if memory_text:
                            mem0_memories.append(memory_text)
                else:
                    logger.info("  No relevant memories found in Mem0")
            except Exception as e:
                logger.warning(f"  Mem0 search failed: {e}")
                import traceback
                logger.warning(f"  Traceback: {traceback.format_exc()}")
        else:
            logger.info("  Mem0 not available, skipping memory search")

        # Store the current message for later Mem0 storage
        self._pending_user_message = message

        logger.info("=" * 60)
        logger.info("STEP 3: Loading conversation history from file")
        logger.info(f"  Conversation ID: {self.current_conversation_id}")
        logger.info(f"  Messages in history: {len(conversation_history)}")
        if conversation_history:
            for i, msg in enumerate(conversation_history[-5:]):  # Show last 5
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:100]
                logger.info(f"  [{i+1}] {role}: {content}...")
        logger.info("=" * 60)

        logger.info("STEP 4: Calling LangChain Tutor Service")
        logger.info(f"  Passing {len(mem0_memories)} Mem0 memories")
        logger.info(f"  Passing {len(conversation_history)} conversation messages")

        # Get response in background thread
        def get_response():
            try:
                # Use the tutor service to get a response with conversation context, memories, and profile
                result = self.tutor_service.chat_with_tutor(
                    message,
                    conversation_history,
                    mem0_memories,
                    self.user_profile  # Pass user profile for personalization
                )

                if result.get("success"):
                    response = result.get("response", "I didn't understand that. Could you try again?")
                    logger.info("=" * 60)
                    logger.info("STEP 6: Received response from LangChain")
                    logger.info(f"  Response length: {len(response)} chars")
                    logger.info(f"  Response preview: {response[:200]}...")
                    logger.info("=" * 60)
                else:
                    response = f"Sorry, I encountered an error: {result.get('error', 'Unknown error')}"
                    logger.error(f"  LangChain returned error: {result.get('error')}")

                # Update UI on main thread
                self.after(0, lambda: self._handle_response(response))

            except Exception as e:
                logger.error(f"Error getting response: {e}")
                self.after(0, lambda: self._handle_response(
                    f"Sorry, I encountered an error: {str(e)}"
                ))

        threading.Thread(target=get_response, daemon=True).start()

    def _handle_response(self, response: str):
        """Handle response from tutor service"""
        # Add response to UI
        self.chat_area.add_message("assistant", response)

        # Save assistant message
        if self.memory_service and self.current_conversation_id:
            self.memory_service.add_message_to_conversation(
                self.current_conversation_id,
                "assistant",
                response
            )
            # Update conversation title if first message
            self._update_conversation_title()

        # Store in Mem0 asynchronously (don't block the UI)
        if self.mem0 and hasattr(self, '_pending_user_message'):
            def store_in_mem0():
                try:
                    user_name = self.user_profile.get("user_name", "Student") if self.user_profile else "Student"
                    target_lang = self.user_profile.get("target_language", "Spanish") if self.user_profile else "Spanish"
                    messages = [
                        {"role": "user", "content": f"{user_name} (learning {target_lang}) said: {self._pending_user_message}"},
                        {"role": "assistant", "content": f"Tutor responded: {response}"}
                    ]
                    self.mem0.add(messages, user_id=self.user_id)
                    logger.info("  [Async] Mem0 storage complete")
                except Exception as e:
                    logger.warning(f"  [Async] Mem0 storage failed: {e}")

            threading.Thread(target=store_in_mem0, daemon=True).start()
            logger.info("  Mem0 storage started (async)")

        logger.info("=" * 40)
        logger.info("RESPONSE DELIVERED")
        logger.info("=" * 40)

        self.is_processing = False
        self.input_bar.set_enabled(True)

    def _update_conversation_title(self):
        """Update conversation title based on first message"""
        if not self.memory_service or not self.current_conversation_id:
            return

        try:
            messages = self.memory_service.load_conversation(self.current_conversation_id)
            if messages and len(messages) >= 1:
                first_msg = messages[0].get("content", "New Chat")
                # Use first ~50 chars as title
                title = first_msg[:50] + ("..." if len(first_msg) > 50 else "")
                self.memory_service.update_conversation_title(
                    self.current_conversation_id,
                    title
                )
                self._load_conversations()
        except Exception as e:
            logger.error(f"Failed to update conversation title: {e}")

    def _show_settings(self):
        """Show settings panel"""
        SettingsPanel(
            self,
            current_language=self.target_language,
            on_save=self._save_settings
        )

    def _save_settings(self, target_language: str):
        """Save settings"""
        self.target_language = target_language
        logger.info(f"Settings saved: target_language={target_language}")

    def _delete_message(self, message_id: str):
        """Delete a specific message from the current conversation"""
        if not self.memory_service or not self.current_conversation_id:
            return
        
        try:
            # Delete from storage
            self.memory_service.delete_message_from_conversation(
                self.current_conversation_id, 
                message_id
            )
            
            # Reload conversation to refresh UI
            messages = self.memory_service.load_conversation(self.current_conversation_id)
            self.chat_area.load_messages(messages)
            
            logger.info(f"Deleted message {message_id} from conversation {self.current_conversation_id}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")

    def _clear_chat(self):
        """Clear all messages in the current conversation"""
        if not self.memory_service or not self.current_conversation_id:
            return
        
        try:
            # Clear all messages in the conversation
            self.memory_service.clear_conversation(self.current_conversation_id)
            
            # Clear UI
            self.chat_area.clear_messages()
            
            logger.info(f"Cleared conversation {self.current_conversation_id}")
        except Exception as e:
            logger.error(f"Failed to clear chat: {e}")

    def run(self):
        """Start the application"""
        self.mainloop()
