"""Enhanced Language Tutor Desktop Application with LangChain Integration"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import customtkinter as ctk
from typing import Dict, Any, Optional
import threading
import json
import os
from datetime import datetime

# Import our enhanced services
from langchain_service import LangChainTutorService
from simple_memory_service import SimpleMemoryService
from user_manager import UserManager

class EnhancedLanguageTutorApp:
    def __init__(self, langsmith_api_key: Optional[str] = None):
        # Set up CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🌐 Enhanced Language Tutor - LangChain Powered")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
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
        
        self.setup_ui()
        self.show_login_screen()
    
    def setup_ui(self):
        """Set up the main UI structure"""
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    def clear_main_container(self):
        """Clear all widgets from main container"""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Show login/create user screen"""
        self.clear_main_container()
        
        # Login frame
        login_frame = ctk.CTkFrame(self.main_container)
        login_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            login_frame, 
            text="🌐 Enhanced Language Tutor", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(20, 40))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            login_frame,
            text="Powered by LangChain + Ollama + LangSmith",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Username input
        username_label = ctk.CTkLabel(login_frame, text="Username:")
        username_label.pack(pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(login_frame, width=300, height=40)
        self.username_entry.pack(pady=(0, 20))
        
        # Email input (optional)
        email_label = ctk.CTkLabel(login_frame, text="Email (optional):")
        email_label.pack(pady=(10, 5))
        
        self.email_entry = ctk.CTkEntry(login_frame, width=300, height=40)
        self.email_entry.pack(pady=(0, 30))
        
        # LangSmith API key input
        langsmith_label = ctk.CTkLabel(login_frame, text="LangSmith API Key (optional):")
        langsmith_label.pack(pady=(10, 5))
        
        self.langsmith_entry = ctk.CTkEntry(login_frame, width=300, height=40, show="*")
        self.langsmith_entry.pack(pady=(0, 30))
        
        # Buttons
        button_frame = ctk.CTkFrame(login_frame)
        button_frame.pack(pady=20)
        
        login_btn = ctk.CTkButton(
            button_frame, 
            text="Login", 
            width=120,
            command=self.login_user
        )
        login_btn.pack(side="left", padx=10)
        
        create_btn = ctk.CTkButton(
            button_frame, 
            text="Create User", 
            width=120,
            command=self.create_user
        )
        create_btn.pack(side="left", padx=10)
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.login_user())
        self.email_entry.bind("<Return>", lambda e: self.login_user())
        self.langsmith_entry.bind("<Return>", lambda e: self.login_user())
    
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
            
            # Get LangSmith API key from entry
            langsmith_key = self.langsmith_entry.get().strip() or None
            
            # Initialize services
            self.initialize_services(langsmith_key)
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
            self.show_main_app()
        else:
            messagebox.showerror("Error", result['error'])
    
    def initialize_services(self, langsmith_key: Optional[str]):
        """Initialize LangChain and memory services"""
        try:
            # Initialize LangChain tutor service
            self.tutor_service = LangChainTutorService(
                langsmith_api_key=langsmith_key,
                langsmith_project=f"language-tutor-{self.current_user['username']}"
            )
            
            # Initialize enhanced memory service
            self.memory_service = SimpleMemoryService(
                user_id=f"user_{self.current_user['id']}"
            )
            
            messagebox.showinfo("Success", "Services initialized successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize services: {str(e)}")
            raise
    
    def show_main_app(self):
        """Show main application interface"""
        self.clear_main_container()
        
        # Create main layout
        main_layout = ctk.CTkFrame(self.main_container)
        main_layout.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(main_layout, height=60)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # User info and language selection
        user_label = ctk.CTkLabel(
            header_frame, 
            text=f"👤 {self.current_user['username']}", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        user_label.pack(side="left", padx=20, pady=15)
        
        lang_label = ctk.CTkLabel(header_frame, text="Learning:")
        lang_label.pack(side="left", padx=(20, 5), pady=15)
        
        self.language_var = tk.StringVar(value="Spanish")
        self.language_dropdown = ctk.CTkComboBox(
            header_frame, 
            values=list(self.languages.keys()),
            variable=self.language_var,
            width=150,
            command=self.on_language_change
        )
        self.language_dropdown.pack(side="left", padx=5, pady=15)
        
        # LangSmith status
        langsmith_status = "🟢 Active" if self.tutor_service.langsmith_client else "🔴 Inactive"
        langsmith_label = ctk.CTkLabel(
            header_frame,
            text=f"LangSmith: {langsmith_status}",
            font=ctk.CTkFont(size=12)
        )
        langsmith_label.pack(side="left", padx=(20, 5), pady=15)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            header_frame, 
            text="Logout", 
            width=80,
            command=self.logout
        )
        logout_btn.pack(side="right", padx=20, pady=15)
        
        # Tab view for different features
        self.tab_view = ctk.CTkTabview(main_layout)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create enhanced tabs
        self.create_enhanced_chat_tab()
        self.create_enhanced_translation_tab()
        self.create_enhanced_exercises_tab()
        self.create_enhanced_progress_tab()
        self.create_observability_tab()
        
        # Set initial language
        self.current_language = self.language_var.get()
    
    def create_enhanced_chat_tab(self):
        """Create enhanced chat interface tab"""
        chat_tab = self.tab_view.add("💬 Smart Chat")
        
        # Chat display
        chat_frame = ctk.CTkFrame(chat_tab)
        chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            state='disabled',
            font=("Arial", 11)
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = ctk.CTkFrame(chat_tab)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.chat_input = ctk.CTkEntry(
            input_frame, 
            placeholder="Ask your language tutor anything...",
            height=40
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        send_btn = ctk.CTkButton(
            input_frame, 
            text="Send", 
            width=80,
            command=self.send_enhanced_chat_message
        )
        send_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Bind Enter key
        self.chat_input.bind("<Return>", lambda e: self.send_enhanced_chat_message())
        
        # Welcome message
        self.add_chat_message("assistant", f"Hello! I'm your enhanced AI language tutor powered by LangChain. I can help you with translations, exercises, and track your progress in {self.current_language}. What would you like to learn today?")
    
    def create_enhanced_translation_tab(self):
        """Create enhanced translation interface tab"""
        trans_tab = self.tab_view.add("🔄 Smart Translation")
        
        # Translation frame
        trans_frame = ctk.CTkFrame(trans_tab)
        trans_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input section
        input_label = ctk.CTkLabel(trans_frame, text="Text to translate:")
        input_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.translation_input = ctk.CTkTextbox(trans_frame, height=100)
        self.translation_input.pack(fill="x", padx=10, pady=(0, 10))
        
        # Language selection
        lang_frame = ctk.CTkFrame(trans_tab)
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        source_label = ctk.CTkLabel(lang_frame, text="From:")
        source_label.pack(side="left", padx=(10, 5))
        
        self.source_lang_var = tk.StringVar(value="Auto-detect")
        self.source_lang_dropdown = ctk.CTkComboBox(
            lang_frame,
            values=["Auto-detect"] + list(self.languages.keys()),
            variable=self.source_lang_var,
            width=120
        )
        self.source_lang_dropdown.pack(side="left", padx=5)
        
        target_label = ctk.CTkLabel(lang_frame, text="To:")
        target_label.pack(side="left", padx=(20, 5))
        
        self.target_lang_var = tk.StringVar(value=self.current_language)
        self.target_lang_dropdown = ctk.CTkComboBox(
            lang_frame,
            values=list(self.languages.keys()),
            variable=self.target_lang_var,
            width=120
        )
        self.target_lang_dropdown.pack(side="left", padx=5)
        
        # Translate button
        translate_btn = ctk.CTkButton(
            trans_frame, 
            text="Translate", 
            command=self.translate_text_enhanced
        )
        translate_btn.pack(pady=10)
        
        # Result section
        result_label = ctk.CTkLabel(trans_frame, text="Translation:")
        result_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.translation_result = ctk.CTkTextbox(trans_frame, height=100)
        self.translation_result.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def create_enhanced_exercises_tab(self):
        """Create enhanced exercises interface tab"""
        ex_tab = self.tab_view.add("📚 Adaptive Exercises")
        
        # Exercise frame
        ex_frame = ctk.CTkFrame(ex_tab)
        ex_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Controls
        control_frame = ctk.CTkFrame(ex_tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        difficulty_label = ctk.CTkLabel(control_frame, text="Difficulty:")
        difficulty_label.pack(side="left", padx=10)
        
        self.difficulty_var = tk.StringVar(value="beginner")
        difficulty_dropdown = ctk.CTkComboBox(
            control_frame,
            values=["beginner", "intermediate", "advanced"],
            variable=self.difficulty_var,
            width=150
        )
        difficulty_dropdown.pack(side="left", padx=5)
        
        exercise_type_label = ctk.CTkLabel(control_frame, text="Type:")
        exercise_type_label.pack(side="left", padx=(20, 5))
        
        self.exercise_type_var = tk.StringVar(value="comprehensive")
        exercise_type_dropdown = ctk.CTkComboBox(
            control_frame,
            values=["comprehensive", "translation", "vocabulary", "grammar"],
            variable=self.exercise_type_var,
            width=150
        )
        exercise_type_dropdown.pack(side="left", padx=5)
        
        generate_btn = ctk.CTkButton(
            control_frame,
            text="Generate Exercise",
            command=self.generate_enhanced_exercise
        )
        generate_btn.pack(side="left", padx=20)
        
        # Exercise display
        self.exercise_display = ctk.CTkTextbox(ex_tab)
        self.exercise_display.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_enhanced_progress_tab(self):
        """Create enhanced progress tracking tab"""
        progress_tab = self.tab_view.add("📊 Progress Analytics")
        
        # Progress frame
        progress_frame = ctk.CTkFrame(progress_tab)
        progress_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Controls
        control_frame = ctk.CTkFrame(progress_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(
            control_frame,
            text="Refresh Progress",
            command=self.update_enhanced_progress
        )
        refresh_btn.pack(side="left", padx=10)
        
        export_btn = ctk.CTkButton(
            control_frame,
            text="Export Data",
            command=self.export_progress_data
        )
        export_btn.pack(side="left", padx=5)
        
        # Progress display
        self.progress_display = ctk.CTkTextbox(progress_tab)
        self.progress_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Load initial progress
        self.update_enhanced_progress()
    
    def create_observability_tab(self):
        """Create LangSmith observability tab"""
        obs_tab = self.tab_view.add("🔍 Observability")
        
        # Observability frame
        obs_frame = ctk.CTkFrame(obs_tab)
        obs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status
        status_frame = ctk.CTkFrame(obs_tab)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        if self.tutor_service.langsmith_client:
            status_text = "🟢 LangSmith tracing is ACTIVE"
            status_color = "green"
        else:
            status_text = "🔴 LangSmith tracing is INACTIVE"
            status_color = "red"
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        status_label.pack(pady=10)
        
        # Controls
        control_frame = ctk.CTkFrame(obs_tab)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        refresh_btn = ctk.CTkButton(
            control_frame,
            text="Refresh Runs",
            command=self.refresh_langsmith_runs
        )
        refresh_btn.pack(side="left", padx=10)
        
        clear_memory_btn = ctk.CTkButton(
            control_frame,
            text="Clear Chat Memory",
            command=self.clear_chat_memory
        )
        clear_memory_btn.pack(side="left", padx=5)
        
        # Runs display
        runs_label = ctk.CTkLabel(obs_tab, text="Recent LangSmith Runs:")
        runs_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.runs_display = ctk.CTkTextbox(obs_tab, height=200)
        self.runs_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load initial runs
        self.refresh_langsmith_runs()
    
    def on_language_change(self, selected_language):
        """Handle language change"""
        self.current_language = selected_language
        self.update_enhanced_progress()
    
    def send_enhanced_chat_message(self):
        """Send chat message using LangChain agent"""
        user_message = self.chat_input.get().strip()
        if not user_message:
            return
        
        # Add user message to chat
        self.add_chat_message("user", user_message)
        self.chat_input.delete(0, tk.END)
        
        # Start session if not already started
        if not self.current_session_id:
            self.current_session_id = self.user_manager.start_learning_session(
                self.current_user['id'], 
                self.current_language, 
                "enhanced_chat"
            )
        
        # Get response in separate thread
        threading.Thread(
            target=self.process_enhanced_chat_message,
            args=(user_message,),
            daemon=True
        ).start()
    
    def process_enhanced_chat_message(self, user_message):
        """Process chat message using LangChain agent"""
        try:
            # Use the LangChain tutor service
            result = self.tutor_service.chat_with_tutor(user_message)
            
            if result['success']:
                ai_response = result['response']
                
                # Store in enhanced memory
                messages = [
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": ai_response}
                ]
                
                self.memory_service.add_conversation(
                    messages, 
                    {
                        "language": self.current_language,
                        "session_type": "enhanced_chat",
                        "agent_response": True
                    }
                )
                
                # Add response to chat
                self.add_chat_message("assistant", ai_response)
                
                # Log intermediate steps if any
                if result.get('intermediate_steps'):
                    self.log_agent_steps(result['intermediate_steps'])
            else:
                self.add_chat_message("assistant", f"Sorry, I encountered an error: {result['error']}")
                
        except Exception as e:
            self.add_chat_message("assistant", f"Error: {str(e)}")
    
    def log_agent_steps(self, steps):
        """Log agent intermediate steps for debugging"""
        for i, (action, observation) in enumerate(steps):
            step_info = f"[Step {i+1}] Tool: {action.tool} | Input: {action.tool_input} | Output: {observation}"
            print(step_info)  # Could also log to file or display in UI
    
    def translate_text_enhanced(self):
        """Translate text using enhanced LangChain service"""
        text = self.translation_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
        
        source_lang = "auto" if self.source_lang_var.get() == "Auto-detect" else self.source_lang_var.get()
        target_lang = self.target_lang_var.get()
        
        # Start translation in separate thread
        threading.Thread(
            target=self.perform_enhanced_translation,
            args=(text, source_lang, target_lang),
            daemon=True
        ).start()
    
    def perform_enhanced_translation(self, text, source_lang, target_lang):
        """Perform translation using LangChain service"""
        try:
            result = self.tutor_service.translate_text(text, target_lang, source_lang)
            
            if result['success']:
                self.translation_result.delete("1.0", tk.END)
                self.translation_result.insert("1.0", result['translated_text'])
                
                # Store in enhanced memory
                self.memory_service.add_translation_memory(
                    text,
                    result['translated_text'],
                    source_lang,
                    target_lang,
                    {
                        "model": result['model'],
                        "timestamp": result['timestamp']
                    }
                )
            else:
                messagebox.showerror("Error", f"Translation failed: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Translation error: {str(e)}")
    
    def generate_enhanced_exercise(self):
        """Generate exercise using enhanced LangChain service"""
        difficulty = self.difficulty_var.get()
        exercise_type = self.exercise_type_var.get()
        
        # Start exercise generation in separate thread
        threading.Thread(
            target=self.perform_enhanced_exercise_generation,
            args=(difficulty, exercise_type),
            daemon=True
        ).start()
    
    def perform_enhanced_exercise_generation(self, difficulty, exercise_type):
        """Generate exercise using LangChain service"""
        try:
            result = self.tutor_service.generate_exercise(self.current_language, difficulty)
            
            if result['success']:
                self.exercise_display.delete("1.0", tk.END)
                
                # Add exercise type header
                exercise_content = f"📚 {exercise_type.title()} Exercise - {difficulty.title()} Level\n"
                exercise_content += f"🌐 Language: {self.current_language}\n"
                exercise_content += f"🤖 Generated by: {result['model']}\n"
                exercise_content += f"⏰ Time: {result['timestamp']}\n\n"
                exercise_content += result['exercise']
                
                self.exercise_display.insert("1.0", exercise_content)
                
                # Store in enhanced memory
                self.memory_service.add_exercise_completion(
                    self.current_language,
                    difficulty,
                    exercise_type,
                    metadata={
                        "model": result['model'],
                        "timestamp": result['timestamp']
                    }
                )
            else:
                messagebox.showerror("Error", f"Exercise generation failed: {result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Exercise generation error: {str(e)}")
    
    def update_enhanced_progress(self):
        """Update progress display using enhanced memory service"""
        if not self.current_user:
            return
        
        try:
            # Get comprehensive progress from enhanced memory
            progress_result = self.memory_service.get_learning_progress(self.current_language)
            
            # Build progress text
            progress_text = f"📊 Enhanced Learning Progress for {self.current_language}\n\n"
            
            if progress_result['success']:
                stats = progress_result['statistics']
                
                progress_text += f"📈 Statistics:\n"
                progress_text += f"• Total Exercises: {stats['total_exercises']}\n"
                progress_text += f"• Total Milestones: {stats['total_milestones']}\n"
                progress_text += f"• Total Translations: {stats['total_translations']}\n"
                progress_text += f"• Average Performance: {stats['average_performance']:.2%}\n"
                progress_text += f"• Last Activity: {stats['last_activity'] or 'No activity yet'}\n\n"
                
                # Recent activities
                progress_text += "🔄 Recent Activities:\n"
                
                # Show recent exercises
                recent_exercises = progress_result['exercises'][:3]
                for exercise in recent_exercises:
                    metadata = exercise.get('metadata', {})
                    progress_text += f"• Exercise: {metadata.get('difficulty', 'unknown')} - {metadata.get('exercise_type', 'unknown')}\n"
                
                # Show recent translations
                recent_translations = progress_result['translations'][:3]
                for translation in recent_translations:
                    metadata = translation.get('metadata', {})
                    progress_text += f"• Translation: {metadata.get('source_language', 'unknown')} → {metadata.get('target_language', 'unknown')}\n"
                
            else:
                progress_text += f"Error loading progress: {progress_result['error']}\n"
                progress_text += "Start learning to track your progress!\n"
            
            self.progress_display.delete("1.0", tk.END)
            self.progress_display.insert("1.0", progress_text)
            
        except Exception as e:
            error_text = f"Error loading progress: {str(e)}"
            self.progress_display.delete("1.0", tk.END)
            self.progress_display.insert("1.0", error_text)
    
    def refresh_langsmith_runs(self):
        """Refresh LangSmith runs display"""
        try:
            runs = self.tutor_service.get_langsmith_runs(limit=10)
            
            runs_text = "🔍 Recent LangSmith Runs:\n\n"
            
            if runs:
                for run in runs:
                    status_emoji = "✅" if run['status'] == 'success' else "❌"
                    runs_text += f"{status_emoji} {run['name']}\n"
                    runs_text += f"   ID: {run['id']}\n"
                    runs_text += f"   Time: {run['start_time']} - {run['end_time']}\n"
                    if run.get('error'):
                        runs_text += f"   Error: {run['error']}\n"
                    runs_text += "\n"
            else:
                runs_text += "No recent runs found.\n"
                if not self.tutor_service.langsmith_client:
                    runs_text += "LangSmith tracing is not active.\n"
            
            self.runs_display.delete("1.0", tk.END)
            self.runs_display.insert("1.0", runs_text)
            
        except Exception as e:
            error_text = f"Error loading LangSmith runs: {str(e)}"
            self.runs_display.delete("1.0", tk.END)
            self.runs_display.insert("1.0", error_text)
    
    def clear_chat_memory(self):
        """Clear chat memory"""
        try:
            self.tutor_service.clear_conversation_memory()
            messagebox.showinfo("Success", "Chat memory cleared successfully!")
            self.refresh_langsmith_runs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear chat memory: {str(e)}")
    
    def export_progress_data(self):
        """Export progress data"""
        try:
            # Export from enhanced memory service
            export_result = self.memory_service.export_memories(format="json")
            
            if export_result['success']:
                # Save to file
                filename = f"language_tutor_export_{self.current_user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join("data", filename)
                
                os.makedirs("data", exist_ok=True)
                with open(filepath, 'w') as f:
                    json.dump(export_result['data'], f, indent=2)
                
                messagebox.showinfo("Success", f"Progress data exported to:\n{filepath}")
            else:
                messagebox.showerror("Error", f"Export failed: {export_result['error']}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")
    
    def add_chat_message(self, role, message):
        """Add message to chat display"""
        self.chat_display.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M")
        if role == "user":
            self.chat_display.insert(tk.END, f"[{timestamp}] You: {message}\n\n", "user")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] Tutor: {message}\n\n", "assistant")
        
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
    
    def logout(self):
        """Logout current user"""
        # End current session if active
        if self.current_session_id:
            self.user_manager.end_learning_session(self.current_session_id)
            self.current_session_id = None
        
        # Clear user data
        self.current_user = None
        self.tutor_service = None
        self.memory_service = None
        self.current_language = None
        
        # Show login screen
        self.show_login_screen()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = EnhancedLanguageTutorApp()
    app.run()
