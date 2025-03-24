# chatbot_desktop/config/config.py

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Fallback (for development/testing only; remove or keep private)
if not OPENAI_API_KEY:
    # Replace with your actual key or keep it out of version control.
    OPENAI_API_KEY = "your-fallback-key-here"
