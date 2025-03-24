# services/ai_service.py

from openai import OpenAI
from config.config import client

client = client


def ask_chatgpt(message, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # or 'gpt-3.5-turbo'
            messages=messages,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR] {str(e)}"
