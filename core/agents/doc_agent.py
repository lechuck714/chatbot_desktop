# chatbot_desktop/core/agents/doc_agent.py

from .base_agent import BaseAgent
from services.ai_service import ask_chatgpt


class DocAgent(BaseAgent):
    def __init__(self, blackboard):
        super().__init__(blackboard)
        self.active_doc_id = None

    def set_active_doc(self, doc_id):
        self.active_doc_id = doc_id

    def handle_query(self, user_msg):
        self.logger.debug("DocAgent handling query.")

        if not self.active_doc_id or self.active_doc_id not in self.blackboard.documents:
            return "No document loaded in DocAgent."

        doc_text = self.blackboard.documents[self.active_doc_id]

        # Flatten conversation so far for context
        conv_text = ""
        for msg in self.blackboard.conversation_history:
            role = msg["role"]
            content = msg["content"]
            conv_text += f"{role.capitalize()}: {content}\n"

        prompt = (
            f"{conv_text}\n\n"
            f"Document content:\n{doc_text}\n\n"
            f"User's query: {user_msg}\n"
        )

        return ask_chatgpt(prompt)
