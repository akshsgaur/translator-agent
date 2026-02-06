#!/usr/bin/env python3
"""
Web-based Language Tutor Application
Runs in browser when tkinter is not available
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the web application"""
    try:
        # Test basic imports
        try:
            from langchain_community.llms import Ollama
            print("✅ LangChain Ollama import working")
        except Exception as e:
            print(f"❌ LangChain import error: {e}")
            return
        
        # Import and run the web app
        from web_tutor import WebLanguageTutorApp
        
        app = WebLanguageTutorApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
