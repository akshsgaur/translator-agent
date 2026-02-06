"""Web-based Language Tutor Application"""

import streamlit as st
import threading
from datetime import datetime
from typing import Dict, Any, Optional

# LangChain imports
from langchain_community.llms import Ollama

class WebLanguageTutorApp:
    def __init__(self):
        self.llm = None
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
        
        self.initialize_ollama()
    
    def initialize_ollama(self):
        """Initialize Ollama LLM"""
        try:
            self.llm = Ollama(model="translategemma:4b")
            st.success("✅ Successfully connected to Ollama with translategemma:4b model!")
        except Exception as e:
            st.error(f"❌ Failed to connect to Ollama: {str(e)}")
            st.info("💡 Make sure Ollama is running and you have pulled the translategemma:4b model")
    
    def run(self):
        """Run the Streamlit web app"""
        st.set_page_config(
            page_title="🌐 Language Tutor",
            page_icon="🌐",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main title
        st.title("🌐 Language Tutor - Web Version")
        st.markdown("---")
        
        # Sidebar for language selection
        with st.sidebar:
            st.header("⚙️ Settings")
            
            self.current_language = st.selectbox(
                "Select Language:",
                list(self.languages.keys()),
                index=0
            )
            
            st.markdown("---")
            st.markdown("### 📚 Features")
            st.markdown("- 💬 AI Chat Tutor")
            st.markdown("- 🔄 Text Translation")
            st.markdown("- 📝 Exercise Generation")
            st.markdown("- 📊 Progress Tracking")
        
        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🔄 Translation", "📚 Exercises", "📊 Progress"])
        
        with tab1:
            self.chat_interface()
        
        with tab2:
            self.translation_interface()
        
        with tab3:
            self.exercises_interface()
        
        with tab4:
            self.progress_interface()
    
    def chat_interface(self):
        """Chat interface"""
        st.header("💬 AI Language Tutor")
        
        # Initialize chat history
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": f"Hello! I'm your AI language tutor. I can help you learn {self.current_language}. What would you like to practice today?"}
            ]
        
        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your message here..."):
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            if self.llm:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response_prompt = f"""You are a helpful language tutor teaching {self.current_language}. 
                            The user says: "{prompt}"
                            
                            Provide a helpful, encouraging response that helps them learn {self.current_language}.
                            Keep your response concise and educational."""
                            
                            response = self.llm.invoke(response_prompt)
                            st.markdown(response)
                            
                            # Add to session state
                            st.session_state.chat_messages.append({"role": "assistant", "content": response})
                            
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.error("❌ Ollama not initialized")
    
    def translation_interface(self):
        """Translation interface"""
        st.header("🔄 Text Translation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            source_lang = st.selectbox(
                "From:",
                ["Auto-detect"] + list(self.languages.keys()),
                key="source_lang"
            )
        
        with col2:
            target_lang = st.selectbox(
                "To:",
                list(self.languages.keys()),
                index=list(self.languages.keys()).index(self.current_language),
                key="target_lang"
            )
        
        # Text input
        text_to_translate = st.text_area(
            "Text to translate:",
            height=150,
            key="translate_input"
        )
        
        # Translate button
        if st.button("🔄 Translate", type="primary"):
            if text_to_translate.strip() and self.llm:
                with st.spinner("Translating..."):
                    try:
                        source = "auto" if source_lang == "Auto-detect" else source_lang
                        prompt = f"Translate the following text from {source} to {target_lang}: '{text_to_translate}'"
                        
                        translation = self.llm.invoke(prompt)
                        
                        st.success("✅ Translation Complete!")
                        st.text_area("Translation:", value=translation, height=150, key="translation_result")
                        
                    except Exception as e:
                        st.error(f"Translation failed: {str(e)}")
            else:
                st.warning("Please enter text to translate and ensure Ollama is connected")
    
    def exercises_interface(self):
        """Exercises interface"""
        st.header("📚 Language Exercises")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            difficulty = st.selectbox(
                "Difficulty Level:",
                ["beginner", "intermediate", "advanced"],
                key="exercise_difficulty"
            )
        
        with col2:
            exercise_type = st.selectbox(
                "Exercise Type:",
                ["comprehensive", "translation", "vocabulary", "grammar"],
                key="exercise_type"
            )
        
        # Generate button
        if st.button("📝 Generate Exercise", type="primary"):
            if self.llm:
                with st.spinner("Generating exercise..."):
                    try:
                        prompt = f"""Create a {difficulty} {self.current_language} language exercise of type {exercise_type}.
                        Include:
                        1. A short text in {self.current_language}
                        2. A translation task
                        3. A vocabulary question
                        Format it clearly with sections."""
                        
                        exercise = self.llm.invoke(prompt)
                        
                        st.success(f"✅ {difficulty.title()} Exercise Generated!")
                        st.markdown(f"### 📚 {exercise_type.title()} Exercise - {self.current_language}")
                        st.markdown(exercise)
                        
                    except Exception as e:
                        st.error(f"Exercise generation failed: {str(e)}")
            else:
                st.error("❌ Ollama not initialized")
    
    def progress_interface(self):
        """Progress interface"""
        st.header("📊 Learning Progress")
        
        # Progress metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", "0")
        
        with col2:
            st.metric("Exercises Completed", "0")
        
        with col3:
            st.metric("Translations Made", "0")
        
        with col4:
            st.metric("Study Time", "0 min")
        
        st.markdown("---")
        
        # Progress details
        st.subheader("📈 Current Progress")
        
        progress_info = f"""
        **🎯 Current Language:** {self.current_language}
        **📊 Difficulty Level:** {st.session_state.get('exercise_difficulty', 'beginner')}
        
        **📚 Recent Activity:**
        - No recent activity yet. Start learning to track your progress!
        
        **💡 Tips:**
        - Practice daily for best results
        - Use the chat tab for conversations
        - Try translation exercises
        - Complete generated exercises
        
        **🔧 Settings:**
        - Model: translategemma:4b
        - Provider: Ollama (Local)
        - Status: {'✅ Connected' if self.llm else '❌ Disconnected'}
        """
        
        st.markdown(progress_info)
        
        # Refresh button
        if st.button("🔄 Refresh Progress"):
            st.rerun()

if __name__ == "__main__":
    app = WebLanguageTutorApp()
    app.run()
