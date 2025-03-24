# chatbot_desktop/services/ai_service.py

import openai
from config.config import OPENAI_API_KEY

# Initialize the OpenAI client
openai.api_key = OPENAI_API_KEY


def ask_chatgpt(message, system_prompt=None):
    """
    Using the python openai library to call chat completions.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo", "gpt-4.5" etc.
            messages=messages,
            temperature=0.8
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"[ERROR] {str(e)}"
