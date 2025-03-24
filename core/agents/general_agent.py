# chatbot_desktop/core/agents/general_agent.py

from .base_agent import BaseAgent
from services.ai_service import ask_chatgpt


class GeneralAgent(BaseAgent):
    def handle_query(self, user_msg):
        self.logger.debug("GeneralAgent fallback.")

        conv_text = ""
        for msg in self.blackboard.conversation_history:
            role = msg["role"]
            content = msg["content"]
            conv_text += f"{role.capitalize()}: {content}\n"

        prompt = f"{conv_text}\nUser: {user_msg}\nAssistant:"
        return ask_chatgpt(prompt)
