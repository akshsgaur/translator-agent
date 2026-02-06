#!/usr/bin/env python3
"""
Modern Language Tutor Desktop Application
Enhanced UI with modern design patterns and improved user experience
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for the modern application"""
    try:
        # Get LangSmith API key from environment
        langsmith_api_key = os.getenv('LANGSMITH_API_KEY')
        
        # Import and run the modern app
        from modern_main_app import ModernLanguageTutorApp
        
        app = ModernLanguageTutorApp(langsmith_api_key=langsmith_api_key)
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
