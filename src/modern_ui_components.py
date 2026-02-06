"""Modern UI Components for Language Tutor"""

import customtkinter as ctk
from typing import Optional, Callable

class ModernCard(ctk.CTkFrame):
    """Modern card component with rounded corners and shadow effect"""
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, corner_radius=15, fg_color=("gray95", "gray10"), **kwargs)
        
        if title:
            title_label = ctk.CTkLabel(
                self, 
                text=title, 
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.pack(pady=(15, 10), padx=15, anchor="w")

class ModernButton(ctk.CTkButton):
    """Modern button with enhanced styling"""
    def __init__(self, parent, text: str, style: str = "primary", **kwargs):
        # Set colors based on style
        if style == "primary":
            kwargs.setdefault("fg_color", ("#3B82F6", "#2563EB"))
            kwargs.setdefault("hover_color", ("#2563EB", "#1D4ED8"))
        elif style == "secondary":
            kwargs.setdefault("fg_color", ("#6B7280", "#4B5563"))
            kwargs.setdefault("hover_color", ("#4B5563", "#374151"))
        elif style == "success":
            kwargs.setdefault("fg_color", ("#10B981", "#059669"))
            kwargs.setdefault("hover_color", ("#059669", "#047857"))
        
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("font", ctk.CTkFont(size=14, weight="bold"))
        
        super().__init__(parent, text=text, **kwargs)

class ModernSidebar(ctk.CTkFrame):
    """Modern sidebar navigation"""
    def __init__(self, parent, on_navigation: Optional[Callable] = None, **kwargs):
        super().__init__(parent, corner_radius=0, width=280, **kwargs)
        self.on_navigation = on_navigation
        self.nav_buttons = {}
        
        # User info section
        self.user_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.user_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.create_navigation()
    
    def create_navigation(self):
        """Create navigation buttons"""
        nav_items = [
            ("💬 Chat", "chat"),
            ("🔄 Translation", "translation"), 
            ("📚 Exercises", "exercises"),
            ("📊 Progress", "progress"),
            ("🔍 Analytics", "analytics"),
            ("⚙️ Settings", "settings")
        ]
        
        for icon_text, view_id in nav_items:
            btn = ModernButton(
                self,
                text=icon_text,
                style="secondary",
                command=lambda v=view_id: self.navigate(v)
            )
            btn.pack(fill="x", padx=15, pady=5)
            self.nav_buttons[view_id] = btn
    
    def navigate(self, view_id: str):
        """Handle navigation"""
        if self.on_navigation:
            self.on_navigation(view_id)
        
        # Update button states
        for view, btn in self.nav_buttons.items():
            if view == view_id:
                btn.configure(fg_color=("#3B82F6", "#2563EB"))
            else:
                btn.configure(fg_color=("#6B7280", "#4B5563"))
    
    def set_user_info(self, username: str, language: str):
        """Update user info display"""
        # Clear existing widgets
        for widget in self.user_frame.winfo_children():
            widget.destroy()
        
        # Username
        user_label = ctk.CTkLabel(
            self.user_frame,
            text=f"👤 {username}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        user_label.pack(anchor="w")
        
        # Current language
        lang_label = ctk.CTkLabel(
            self.user_frame,
            text=f"🌐 Learning: {language}",
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        lang_label.pack(anchor="w", pady=(2, 0))

class ModernChatInterface(ctk.CTkFrame):
    """Modern chat interface with scrollable chat and auto-resizing input"""
    def __init__(self, parent, on_send: Optional[Callable] = None, **kwargs):
        super().__init__(parent, corner_radius=15, **kwargs)
        self.on_send = on_send
        self.min_input_height = 40
        self.max_input_height = 150

        # Chat display - scrollable (disabled state prevents editing but allows scroll)
        self.chat_display = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=13),
            wrap="word",
            state="disabled",
            activate_scrollbars=True
        )
        self.chat_display.pack(fill="both", expand=True, padx=15, pady=(15, 10))

        # Input area container
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Use CTkTextbox for auto-resizing input
        self.chat_input = ctk.CTkTextbox(
            self.input_frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            height=self.min_input_height,
            fg_color=("gray90", "gray17"),
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=10
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        send_btn = ModernButton(
            self.input_frame,
            text="Send",
            style="primary",
            width=80,
            height=40,
            command=self.send_message
        )
        send_btn.pack(side="right", anchor="s")

        # Bind events for auto-resize and send
        self.chat_input.bind("<KeyRelease>", self._on_input_change)
        self.chat_input.bind("<Return>", self._on_enter)
        self.chat_input.bind("<Shift-Return>", self._on_shift_enter)

        # Add placeholder
        self._add_placeholder()

    def _add_placeholder(self):
        """Add placeholder text"""
        self.chat_input.insert("1.0", "Type your message...")
        self.chat_input.configure(text_color=("gray50", "gray50"))
        self.chat_input.bind("<FocusIn>", self._on_focus_in)
        self.chat_input.bind("<FocusOut>", self._on_focus_out)
        self._has_placeholder = True

    def _on_focus_in(self, event):
        """Remove placeholder on focus"""
        if self._has_placeholder:
            self.chat_input.delete("1.0", "end")
            self.chat_input.configure(text_color=("gray10", "gray90"))
            self._has_placeholder = False

    def _on_focus_out(self, event):
        """Add placeholder if empty"""
        content = self.chat_input.get("1.0", "end").strip()
        if not content:
            self._add_placeholder()

    def _on_input_change(self, event=None):
        """Auto-resize input based on content"""
        # Get number of lines
        content = self.chat_input.get("1.0", "end")
        lines = content.count('\n')

        # Calculate new height (approx 20px per line)
        new_height = min(self.max_input_height, max(self.min_input_height, 25 + (lines * 20)))
        self.chat_input.configure(height=new_height)

    def _on_enter(self, event):
        """Handle Enter key - send message"""
        if not event.state & 0x1:  # Not Shift+Enter
            self.send_message()
            return "break"  # Prevent newline

    def _on_shift_enter(self, event):
        """Handle Shift+Enter - add newline"""
        return None  # Allow default behavior (newline)

    def send_message(self):
        """Send message"""
        if self.on_send:
            message = self.chat_input.get("1.0", "end").strip()
            if message and not self._has_placeholder:
                self.on_send(message)
                self.chat_input.delete("1.0", "end")
                self.chat_input.configure(height=self.min_input_height)

    def add_message(self, role: str, message: str):
        """Add message to chat and auto-scroll"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{role}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")  # Auto-scroll to bottom

    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
