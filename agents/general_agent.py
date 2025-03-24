# agents/general_agent.py
from chatbot import ask_chatgpt

class GeneralAgent:
    def __init__(self, blackboard):
        self.blackboard = blackboard

    def handle_query(self, user_msg):
        print("DEBUG: GeneralAgent fallback.")
        conv_text = ""
        for msg in self.blackboard.conversation_history:
            role = msg["role"]
            content = msg["content"]
            conv_text += f"{role.capitalize()}: {content}\n"

        prompt = f"{conv_text}\nUser: {user_msg}\nAssistant:"
        return ask_chatgpt(prompt)
