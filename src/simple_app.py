"""Simple Language Tutor Desktop Application - Working Version"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# LangChain imports
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

class SimpleLanguageTutorApp:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("🌐 Language Tutor - Simple Version")
        self.root.geometry("1200x800")
        
        # Configure style
        self.root.configure(bg='#f0f0f0')
        
        # Initialize services
        self.llm = None
        self.current_user = None
        self.current_language = "Spanish"
        
        # Supported languages
        self.languages = {
            "Spanish": "es",
            "French": "fr", 
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Russian": "ru",
            "Chinese": "zh",
            "Japanese": "ja"
        }
        
        self.setup_ui()
        self.initialize_ollama()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🌐 Language Tutor",
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_chat_tab()
        self.create_translation_tab()
        self.create_exercises_tab()
        self.create_progress_tab()
    
    def create_chat_tab(self):
        """Create chat interface tab"""
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=15,
            font=('Arial', 11)
        )
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = tk.Frame(chat_frame, bg='#f0f0f0')
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(input_frame, text="Message:", bg='#f0f0f0').pack(side='left', padx=(0, 5))
        
        self.chat_input = tk.Entry(input_frame, font=('Arial', 12))
        self.chat_input.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_chat_message,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        send_btn.pack(side='right')
        
        # Bind Enter key
        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())
        
        # Welcome message
        self.add_chat_message("🤖 Tutor", f"Hello! I'm your AI language tutor. I can help you learn {self.current_language}. What would you like to practice today?")
    
    def create_translation_tab(self):
        """Create translation interface tab"""
        trans_frame = ttk.Frame(self.notebook)
        self.notebook.add(trans_frame, text="🔄 Translation")
        
        # Language selection
        lang_frame = tk.Frame(trans_frame, bg='#f0f0f0')
        lang_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(lang_frame, text="From:", bg='#f0f0f0').pack(side='left', padx=(0, 5))
        self.source_lang_var = tk.StringVar(value="Auto-detect")
        source_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.source_lang_var,
            values=["Auto-detect"] + list(self.languages.keys()),
            width=15
        )
        source_combo.pack(side='left', padx=(0, 20))
        
        tk.Label(lang_frame, text="To:", bg='#f0f0f0').pack(side='left', padx=(0, 5))
        self.target_lang_var = tk.StringVar(value=self.current_language)
        target_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_lang_var,
            values=list(self.languages.keys()),
            width=15
        )
        target_combo.pack(side='left')
        
        # Input text
        tk.Label(trans_frame, text="Text to translate:", bg='#f0f0f0').pack(anchor='w', padx=10, pady=(10, 5))
        
        self.translation_input = scrolledtext.ScrolledText(
            trans_frame,
            height=8,
            font=('Arial', 11)
        )
        self.translation_input.pack(fill='x', padx=10, pady=(0, 10))
        
        # Translate button
        translate_btn = tk.Button(
            trans_frame,
            text="Translate",
            command=self.translate_text,
            bg='#2196F3',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        translate_btn.pack(pady=10)
        
        # Result
        tk.Label(trans_frame, text="Translation:", bg='#f0f0f0').pack(anchor='w', padx=10, pady=(10, 5))
        
        self.translation_result = scrolledtext.ScrolledText(
            trans_frame,
            height=8,
            font=('Arial', 11)
        )
        self.translation_result.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    
    def create_exercises_tab(self):
        """Create exercises interface tab"""
        ex_frame = ttk.Frame(self.notebook)
        self.notebook.add(ex_frame, text="📚 Exercises")
        
        # Controls
        control_frame = tk.Frame(ex_frame, bg='#f0f0f0')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(control_frame, text="Difficulty:", bg='#f0f0f0').pack(side='left', padx=(0, 5))
        self.difficulty_var = tk.StringVar(value="beginner")
        diff_combo = ttk.Combobox(
            control_frame,
            textvariable=self.difficulty_var,
            values=["beginner", "intermediate", "advanced"],
            width=15
        )
        diff_combo.pack(side='left', padx=(0, 20))
        
        generate_btn = tk.Button(
            control_frame,
            text="Generate Exercise",
            command=self.generate_exercise,
            bg='#FF9800',
            fg='white',
            font=('Arial', 12, 'bold')
        )
        generate_btn.pack(side='left')
        
        # Exercise display
        self.exercise_display = scrolledtext.ScrolledText(
            ex_frame,
            font=('Arial', 11)
        )
        self.exercise_display.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_progress_tab(self):
        """Create progress interface tab"""
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="📊 Progress")
        
        # Progress display
        self.progress_display = scrolledtext.ScrolledText(
            progress_frame,
            font=('Arial', 11)
        )
        self.progress_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Load initial progress
        self.update_progress()
    
    def initialize_ollama(self):
        """Initialize Ollama LLM"""
        try:
            self.llm = Ollama(model="translategemma:4b")
            self.add_chat_message("🤖 Tutor", "✅ Successfully connected to Ollama with translategemma:4b model!")
        except Exception as e:
            self.add_chat_message("❌ Error", f"Failed to connect to Ollama: {str(e)}")
            self.add_chat_message("💡 Tip", "Make sure Ollama is running and you have pulled the translategemma:4b model")
    
    def send_chat_message(self):
        """Send chat message"""
        message = self.chat_input.get().strip()
        if not message:
            return
        
        # Add user message
        self.add_chat_message("You", message)
        self.chat_input.delete(0, tk.END)
        
        # Process in background
        threading.Thread(
            target=self.process_chat_message,
            args=(message,),
            daemon=True
        ).start()
    
    def process_chat_message(self, message: str):
        """Process chat message"""
        try:
            if not self.llm:
                self.add_chat_message("❌ Error", "Ollama not initialized")
                return
            
            # Create prompt for language tutoring
            prompt = f"""You are a helpful language tutor teaching {self.current_language}. 
            The user says: "{message}"
            
            Provide a helpful, encouraging response that helps them learn {self.current_language}.
            Keep your response concise and educational."""
            
            response = self.llm.invoke(prompt)
            self.add_chat_message("🤖 Tutor", response)
            
        except Exception as e:
            self.add_chat_message("❌ Error", f"Failed to get response: {str(e)}")
    
    def translate_text(self):
        """Translate text"""
        text = self.translation_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
        
        if not self.llm:
            messagebox.showerror("Error", "Ollama not initialized")
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
            
            prompt = f"Translate the following text from {source_lang} to {target_lang}: '{text}'"
            
            response = self.llm.invoke(prompt)
            
            self.translation_result.delete("1.0", tk.END)
            self.translation_result.insert("1.0", response)
            
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed: {str(e)}")
    
    def generate_exercise(self):
        """Generate exercise"""
        if not self.llm:
            messagebox.showerror("Error", "Ollama not initialized")
            return
        
        difficulty = self.difficulty_var.get()
        
        # Process in background
        threading.Thread(
            target=self.perform_exercise_generation,
            args=(difficulty,),
            daemon=True
        ).start()
    
    def perform_exercise_generation(self, difficulty: str):
        """Generate exercise"""
        try:
            prompt = f"""Create a {difficulty} {self.current_language} language exercise.
            Include:
            1. A short text in {self.current_language}
            2. A translation task
            3. A vocabulary question
            Format it clearly with sections."""
            
            response = self.llm.invoke(prompt)
            
            self.exercise_display.delete("1.0", tk.END)
            self.exercise_display.insert("1.0", f"📚 {difficulty.title()} Exercise - {self.current_language}\n\n{response}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Exercise generation failed: {str(e)}")
    
    def update_progress(self):
        """Update progress display"""
        progress_text = f"""📊 Learning Progress for {self.current_language}

📈 Statistics:
• Total Sessions: 0
• Exercises Completed: 0
• Translations Made: 0
• Study Time: 0 minutes

🎯 Recent Activity:
No recent activity yet. Start learning to track your progress!

💡 Tips:
• Practice daily for best results
• Use the chat tab for conversations
• Try translation exercises
• Complete generated exercises

📚 Current Language: {self.current_language}
🔧 Difficulty: {self.difficulty_var.get()}
"""
        
        self.progress_display.delete("1.0", tk.END)
        self.progress_display.insert("1.0", progress_text)
    
    def add_chat_message(self, sender: str, message: str):
        """Add message to chat display"""
        self.chat_display.insert(tk.END, f"[{datetime.now().strftime('%H:%M')}] {sender}: {message}\n\n")
        self.chat_display.see(tk.END)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleLanguageTutorApp()
    app.run()
