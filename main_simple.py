#!/usr/bin/env python3
"""
Simple Language Tutor Desktop Application
Working version with minimal dependencies
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the simple application"""
    try:
        # Test tkinter first
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the test window
            root.destroy()
            print("✅ tkinter is working")
        except Exception as e:
            print(f"❌ tkinter error: {e}")
            print("Note: tkinter comes built-in with Python")
            return
        
        # Test basic imports
        try:
            from langchain_community.llms import Ollama
            print("✅ LangChain Ollama import working")
        except Exception as e:
            print(f"❌ LangChain import error: {e}")
            return
        
        # Import and run the simple app
        from simple_app import SimpleLanguageTutorApp
        
        app = SimpleLanguageTutorApp()
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
