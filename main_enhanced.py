#!/usr/bin/env python3
"""
Language Tutor Desktop Application
Ollama-style AI language learning app with LangSmith observability
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the application"""
    try:
        # Check if Ollama is available before starting
        from ollama_check import check_ollama_availability
        if not check_ollama_availability():
            print("Ollama is required but not available. Exiting.")
            sys.exit(1)

        # Get LangSmith API key from environment
        langsmith_api_key = os.getenv('LANGSMITH_API_KEY')

        # Import and run the new Ollama-style tutor app
        from tutor_app import TutorApp

        app = TutorApp(langsmith_api_key=langsmith_api_key)
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
