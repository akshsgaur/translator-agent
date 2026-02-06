"""Modern Language Tutor Desktop Application with Enhanced UI"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Any, Optional
import threading
import json
import os
from datetime import datetime

# Import our services and components
from langchain_service import LangChainTutorService
from simple_memory_service import SimpleMemoryService
from user_manager import UserManager
from modern_ui_components import ModernCard, ModernButton, ModernSidebar, ModernChatInterface

class ModernLanguageTutorApp:
    def __init__(self, langsmith_api_key: Optional[str] = None):
        # Set up CustomTkinter with modern theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🌐 Language Tutor - Modern Edition")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 800)
        
        # Initialize services
        self.user_manager = UserManager()
        self.langsmith_api_key = langsmith_api_key
        
        # Current user and session state
        self.current_user = None
        self.current_language = None
        self.tutor_service = None
        self.memory_service = None
        self.current_session_id = None
        
        # Supported languages
        self.languages = {
            "Spanish": "es",
            "French": "fr", 
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Arabic": "ar"
        }
        
        # UI components
        self.sidebar = None
        self.main_content = None
        self.current_view = "login"
        
        self.setup_ui()
        self.show_login_screen()
    
    def setup_ui(self):
        """Set up the main UI structure"""
        # Main container with grid layout
        self.main_container = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid for responsive layout
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
    
    def clear_main_container(self):
        """Clear all widgets from main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Show modern login screen"""
        self.clear_main_container()
        self.current_view = "login"
        
        # Centered login card
        login_card = ModernCard(self.main_container)
        login_card.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        
        # Configure centering
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Title section
        title_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        title_frame.pack(pady=(30, 20))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="🌐 Language Tutor",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="AI-Powered Language Learning",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray40")
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Form section
        form_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        form_frame.pack(pady=20, padx=40, fill="x")
        
        # Username field
        username_label = ctk.CTkLabel(form_frame, text="Username", font=ctk.CTkFont(size=14, weight="bold"))
        username_label.pack(anchor="w", pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(form_frame, height=40, font=ctk.CTkFont(size=12))
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Email field (optional)
        email_label = ctk.CTkLabel(form_frame, text="Email (Optional)", font=ctk.CTkFont(size=14))
        email_label.pack(anchor="w", pady=(5, 5))
        
        self.email_entry = ctk.CTkEntry(form_frame, height=40, font=ctk.CTkFont(size=12))
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # LangSmith API key (optional)
        langsmith_label = ctk.CTkLabel(form_frame, text="LangSmith API Key (Optional)", font=ctk.CTkFont(size=14))
        langsmith_label.pack(anchor="w", pady=(5, 5))
        
        self.langsmith_entry = ctk.CTkEntry(form_frame, height=40, font=ctk.CTkFont(size=12), show="*")
        self.langsmith_entry.pack(fill="x", pady=(0, 25))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 20))
        
        login_btn = ModernButton(
            button_frame, 
            text="Login", 
            style="primary",
            command=self.login_user
        )
        login_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        create_btn = ModernButton(
            button_frame, 
            text="Create Account", 
            style="secondary",
            command=self.create_user
        )
        create_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.login_user())
        self.email_entry.bind("<Return>", lambda e: self.login_user())
        self.langsmith_entry.bind("<Return>", lambda e: self.login_user())
    
    def show_main_app(self):
        """Show main application with modern layout"""
        self.clear_main_container()
        self.current_view = "main"
        
        # Create sidebar
        self.sidebar = ModernSidebar(self.main_container, on_navigation=self.navigate_to_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        
        # Update sidebar with user info
        self.sidebar.set_user_info(self.current_user['username'], self.current_language)
        
        # Create main content area
        self.main_content = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # Show default view (chat)
        self.show_chat_view()
    
    def navigate_to_view(self, view_id: str):
        """Navigate to different views"""
        if view_id == "chat":
            self.show_chat_view()
        elif view_id == "translation":
            self.show_translation_view()
        elif view_id == "exercises":
            self.show_exercises_view()
        elif view_id == "progress":
            self.show_progress_view()
        elif view_id == "analytics":
            self.show_analytics_view()
        elif view_id == "settings":
            self.show_settings_view()
    
    def show_chat_view(self):
        """Show chat interface"""
        self.clear_main_content()
        
        # Header
        header = ModernCard(self.main_content, title="💬 AI Language Tutor")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Language selector in header
        lang_frame = ctk.CTkFrame(header, fg_color="transparent")
        lang_frame.pack(pady=(10, 15), padx=15, fill="x")
        
        lang_label = ctk.CTkLabel(lang_frame, text="Learning Language:", font=ctk.CTkFont(size=12, weight="bold"))
        lang_label.pack(side="left", padx=(0, 10))
        
        self.language_var = tk.StringVar(value=self.current_language)
        language_dropdown = ctk.CTkComboBox(
            lang_frame,
            values=list(self.languages.keys()),
            variable=self.language_var,
            width=150,
            command=self.on_language_change
        )
        language_dropdown.pack(side="left")
        
        # Chat interface
        chat_card = ModernCard(self.main_content)
        chat_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.chat_interface = ModernChatInterface(
            chat_card,
            on_send=self.send_chat_message
        )
        self.chat_interface.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Welcome message
        self.chat_interface.add_message(
            "🤖 Tutor", 
            f"Hello! I'm your AI language tutor. I can help you learn {self.current_language} through conversations, translations, and exercises. What would you like to practice today?"
        )
    
    def show_translation_view(self):
        """Show translation interface"""
        self.clear_main_content()
        
        # Header
        header = ModernCard(self.main_content, title="🔄 Smart Translation")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Translation controls
        controls_card = ModernCard(self.main_content)
        controls_card.pack(fill="x", padx=20, pady=(0, 10))
        
        # Language selection
        lang_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        lang_frame.pack(fill="x", padx=15, pady=15)
        
        # Source language
        source_label = ctk.CTkLabel(lang_frame, text="From:", font=ctk.CTkFont(size=12, weight="bold"))
        source_label.pack(side="left", padx=(0, 5))
        
        self.source_lang_var = tk.StringVar(value="Auto-detect")
        source_dropdown = ctk.CTkComboBox(
            lang_frame,
            values=["Auto-detect"] + list(self.languages.keys()),
            variable=self.source_lang_var,
            width=120
        )
        source_dropdown.pack(side="left", padx=(0, 20))
        
        # Target language
        target_label = ctk.CTkLabel(lang_frame, text="To:", font=ctk.CTkFont(size=12, weight="bold"))
        target_label.pack(side="left", padx=(0, 5))
        
        self.target_lang_var = tk.StringVar(value=self.current_language)
        target_dropdown = ctk.CTkComboBox(
            lang_frame,
            values=list(self.languages.keys()),
            variable=self.target_lang_var,
            width=120
        )
        target_dropdown.pack(side="left")
        
        # Translation areas
        translation_card = ModernCard(self.main_content)
        translation_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Input area
        input_label = ctk.CTkLabel(translation_card, text="Text to translate:", font=ctk.CTkFont(size=12, weight="bold"))
        input_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.translation_input = ctk.CTkTextbox(translation_card, height=150, font=ctk.CTkFont(size=12))
        self.translation_input.pack(fill="x", padx=15, pady=(0, 15))
        
        # Translate button
        translate_btn = ModernButton(
            translation_card,
            text="Translate",
            style="primary",
            command=self.translate_text
        )
        translate_btn.pack(padx=15, pady=(0, 15))
        
        # Result area
        result_label = ctk.CTkLabel(translation_card, text="Translation:", font=ctk.CTkFont(size=12, weight="bold"))
        result_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.translation_result = ctk.CTkTextbox(translation_card, height=150, font=ctk.CTkFont(size=12))
        self.translation_result.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    def show_exercises_view(self):
        """Show exercises interface"""
        self.clear_main_content()
        
        # Header
        header = ModernCard(self.main_content, title="📚 Adaptive Exercises")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Exercise controls
        controls_card = ModernCard(self.main_content)
        controls_card.pack(fill="x", padx=20, pady=(0, 10))
        
        controls_frame = ctk.CTkFrame(controls_card, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=15)
        
        # Difficulty selector
        diff_label = ctk.CTkLabel(controls_frame, text="Difficulty:", font=ctk.CTkFont(size=12, weight="bold"))
        diff_label.pack(side="left", padx=(0, 10))
        
        self.difficulty_var = tk.StringVar(value="beginner")
        diff_dropdown = ctk.CTkComboBox(
            controls_frame,
            values=["beginner", "intermediate", "advanced"],
            variable=self.difficulty_var,
            width=120
        )
        diff_dropdown.pack(side="left", padx=(0, 20))
        
        # Exercise type
        type_label = ctk.CTkLabel(controls_frame, text="Type:", font=ctk.CTkFont(size=12, weight="bold"))
        type_label.pack(side="left", padx=(0, 10))
        
        self.exercise_type_var = tk.StringVar(value="comprehensive")
        type_dropdown = ctk.CTkComboBox(
            controls_frame,
            values=["comprehensive", "translation", "vocabulary", "grammar"],
            variable=self.exercise_type_var,
            width=150
        )
        type_dropdown.pack(side="left", padx=(0, 20))
        
        # Generate button
        generate_btn = ModernButton(
            controls_frame,
            text="Generate Exercise",
            style="primary",
            command=self.generate_exercise
        )
        generate_btn.pack(side="left")
        
        # Exercise display
        exercise_card = ModernCard(self.main_content)
        exercise_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.exercise_display = ctk.CTkTextbox(exercise_card, font=ctk.CTkFont(size=12))
        self.exercise_display.pack(fill="both", expand=True, padx=15, pady=15)
    
    def show_progress_view(self):
        """Show progress view"""
        self.clear_main_content()
        
        # Header
        header = ModernCard(self.main_content, title="📊 Learning Progress")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Progress display
        progress_card = ModernCard(self.main_content)
        progress_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.progress_display = ctk.CTkTextbox(progress_card, font=ctk.CTkFont(size=12))
        self.progress_display.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Load progress
        self.update_progress()
    
    def show_analytics_view(self):
        """Show analytics view"""
        self.clear_main_content()
        
        # Header
        header = ModernCard(self.main_content, title="🔍 Learning Analytics")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Analytics content
        analytics_card = ModernCard(self.main_content)
        analytics_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        analytics_text = ctk.CTkTextbox(analytics_card, font=ctk.CTkFont(size=12))
        analytics_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        analytics_text.insert("1.0", "📈 Learning Analytics\n\n")
        analytics_text.insert("end", "• Total Sessions: 0\n")
        analytics_text.insert("end", "• Average Session Duration: 0 min\n")
        analytics_text.insert("end", "• Exercises Completed: 0\n")
        analytics_text.insert("end", "• Translation Accuracy: 0%\n")
        analytics_text.insert("end", "• Most Active Language: None\n\n")
        analytics_text.insert("end", "Detailed analytics coming soon...")
    
    def show_settings_view(self):
        """Show settings view"""
        self.clear_main_content()
        
        # Header
        header = ModernCard(self.main_content, title="⚙️ Settings")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Settings content
        settings_card = ModernCard(self.main_content)
        settings_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # User settings
        user_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        user_frame.pack(fill="x", padx=15, pady=15)
        
        user_label = ctk.CTkLabel(user_frame, text="User Settings", font=ctk.CTkFont(size=14, weight="bold"))
        user_label.pack(anchor="w", pady=(0, 10))
        
        # Logout button
        logout_btn = ModernButton(
            user_frame,
            text="Logout",
            style="secondary",
            command=self.logout
        )
        logout_btn.pack(pady=10)
    
    def clear_main_content(self):
        """Clear main content area"""
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def login_user(self):
        """Login existing user"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        user = self.user_manager.get_user(username)
        if user:
            self.current_user = user
            self.user_manager.update_last_login(user['id'])
            
            # Get LangSmith API key
            langsmith_key = self.langsmith_entry.get().strip() or None
            
            # Initialize services
            self.initialize_services(langsmith_key)
            self.current_language = "Spanish"  # Default language
            self.show_main_app()
        else:
            messagebox.showerror("Error", "User not found. Please create a new user.")
    
    def create_user(self):
        """Create new user"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return
        
        email = self.email_entry.get().strip() or None
        langsmith_key = self.langsmith_entry.get().strip() or None
        
        result = self.user_manager.create_user(username, email)
        if result['success']:
            self.current_user = {
                'id': result['user_id'],
                'username': username,
                'email': email
            }
            
            # Initialize services
            self.initialize_services(langsmith_key)
            self.current_language = "Spanish"  # Default language
            self.show_main_app()
        else:
            messagebox.showerror("Error", result['error'])
    
    def initialize_services(self, langsmith_key: Optional[str]):
        """Initialize services"""
        try:
            self.tutor_service = LangChainTutorService(
                langsmith_api_key=langsmith_key,
                langsmith_project=f"language-tutor-{self.current_user['username']}"
            )
            
            self.memory_service = SimpleMemoryService(
                user_id=f"user_{self.current_user['id']}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize services: {str(e)}")
            raise
    
    def on_language_change(self, selected_language):
        """Handle language change"""
        self.current_language = selected_language
        if self.sidebar:
            self.sidebar.set_user_info(self.current_user['username'], self.current_language)
    
    def send_chat_message(self, message: str):
        """Send chat message"""
        if not self.tutor_service:
            return
        
        # Add user message
        self.chat_interface.add_message("You", message)
        
        # Process in background
        threading.Thread(
            target=self.process_chat_message,
            args=(message,),
            daemon=True
        ).start()
    
    def process_chat_message(self, message: str):
        """Process chat message"""
        try:
            result = self.tutor_service.chat_with_tutor(message)
            
            if result['success']:
                response = result['response']
                self.chat_interface.add_message("🤖 Tutor", response)
                
                # Store in memory
                messages = [
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": response}
                ]
                self.memory_service.add_conversation(messages)
            else:
                self.chat_interface.add_message("❌ Error", f"Sorry, I encountered an error: {result['error']}")
                
        except Exception as e:
            self.chat_interface.add_message("❌ Error", f"Error: {str(e)}")
    
    def translate_text(self):
        """Translate text"""
        text = self.translation_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
        
        # Process in background
        threading.Thread(
            target=self.perform_translation,
            args=(text,),
            daemon=True
        ).start()
    
    def perform_translation(self, text: str):
        """Perform translation"""
        try:
            source_lang = "auto" if self.source_lang_var.get() == "Auto-detect" else self.source_lang_var.get()
            target_lang = self.target_lang_var.get()
            
            result = self.tutor_service.translate_text(text, target_lang, source_lang)
            
            if result['success']:
                self.translation_result.delete("1.0", tk.END)
                self.translation_result.insert("1.0", result['translated_text'])
                
                # Store in memory
                self.memory_service.add_translation_memory(
                    text, result['translated_text'], source_lang, target_lang
                )
            else:
                messagebox.showerror("Error", f"Translation failed: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Translation error: {str(e)}")
    
    def generate_exercise(self):
        """Generate exercise"""
        difficulty = self.difficulty_var.get()
        exercise_type = self.exercise_type_var.get()
        
        # Process in background
        threading.Thread(
            target=self.perform_exercise_generation,
            args=(difficulty, exercise_type),
            daemon=True
        ).start()
    
    def perform_exercise_generation(self, difficulty: str, exercise_type: str):
        """Generate exercise"""
        try:
            result = self.tutor_service.generate_exercise(self.current_language, difficulty)
            
            if result['success']:
                self.exercise_display.delete("1.0", tk.END)
                
                content = f"📚 {exercise_type.title()} Exercise\n"
                content += f"🌐 Language: {self.current_language}\n"
                content += f"📊 Difficulty: {difficulty}\n\n"
                content += result['exercise']
                
                self.exercise_display.insert("1.0", content)
                
                # Store in memory
                self.memory_service.add_exercise_completion(
                    self.current_language, difficulty, exercise_type
                )
            else:
                messagebox.showerror("Error", f"Exercise generation failed: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Exercise generation error: {str(e)}")
    
    def update_progress(self):
        """Update progress display"""
        if not self.memory_service:
            return
        
        try:
            progress_result = self.memory_service.get_learning_progress(self.current_language)
            
            progress_text = f"📊 Learning Progress for {self.current_language}\n\n"
            
            if progress_result['success']:
                stats = progress_result['statistics']
                progress_text += f"📈 Statistics:\n"
                progress_text += f"• Total Exercises: {stats['total_exercises']}\n"
                progress_text += f"• Total Translations: {stats['total_translations']}\n"
                progress_text += f"• Average Performance: {stats['average_performance']:.1%}\n"
                progress_text += f"• Last Activity: {stats['last_activity'] or 'No activity yet'}\n"
            else:
                progress_text += "Start learning to track your progress!\n"
            
            self.progress_display.delete("1.0", tk.END)
            self.progress_display.insert("1.0", progress_text)
            
        except Exception as e:
            self.progress_display.delete("1.0", tk.END)
            self.progress_display.insert("1.0", f"Error loading progress: {str(e)}")
    
    def logout(self):
        """Logout user"""
        if self.current_session_id:
            self.user_manager.end_learning_session(self.current_session_id)
        
        self.current_user = None
        self.tutor_service = None
        self.memory_service = None
        self.current_language = None
        
        self.show_login_screen()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
    
    app = ModernLanguageTutorApp(langsmith_api_key=langsmith_api_key)
    app.run()
