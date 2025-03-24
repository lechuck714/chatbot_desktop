# agents/doc_agent.py
from chatbot import ask_chatgpt

class DocAgent:
    def __init__(self, blackboard):
        self.blackboard = blackboard
        self.active_doc_id = None

    def set_active_doc(self, doc_id):
        self.active_doc_id = doc_id

    def handle_query(self, user_msg):
        print("DEBUG: DocAgent handling query.")
        self.blackboard.conversation_history.append(
            {"role":"system", "content":"(DocAgent analyzing doc...)"}
        )

        if not self.active_doc_id or self.active_doc_id not in self.blackboard.documents:
            return "No document loaded in DocAgent."

        doc_text = self.blackboard.documents[self.active_doc_id]

        # flatten
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
