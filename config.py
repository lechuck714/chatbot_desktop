import os

# Load your OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional: fallback for development/testing
if not OPENAI_API_KEY:
    OPENAI_API_KEY = "sk-..."  # ← Replace with your actual key for now (just don't push it to GitHub)
