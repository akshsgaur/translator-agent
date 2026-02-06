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
    """Modern chat interface"""
    def __init__(self, parent, on_send: Optional[Callable] = None, **kwargs):
        super().__init__(parent, corner_radius=15, **kwargs)
        self.on_send = on_send
        
        # Chat display
        self.chat_display = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.chat_display.pack(fill="both", expand=True, padx=15, pady=(15, 10))
        
        # Input area
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder="Type your message...",
            font=ctk.CTkFont(size=12),
            height=40
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        send_btn = ModernButton(
            input_frame,
            text="Send",
            style="primary",
            width=80,
            command=self.send_message
        )
        send_btn.pack(side="right")
        
        # Bind Enter key
        self.chat_input.bind("<Return>", lambda e: self.send_message())
    
    def send_message(self):
        """Send message"""
        if self.on_send:
            message = self.chat_input.get().strip()
            if message:
                self.on_send(message)
                self.chat_input.delete(0, "end")
    
    def add_message(self, role: str, message: str):
        """Add message to chat"""
        self.chat_display.insert("end", f"{role}: {message}\n\n")
        self.chat_display.see("end")
    
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.delete("1.0", "end")
