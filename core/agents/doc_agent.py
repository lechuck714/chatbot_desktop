# chatbot_desktop/core/agents/doc_agent.py

from .base_agent import BaseAgent
from services.vector_service import VectorService
from utils.chunker import chunk_text


class DocAgent(BaseAgent):
    def __init__(self, blackboard):
        super().__init__(blackboard)
        self.vector_service = VectorService()

    def ingest_document(self, document_id, text, metadata=None):
        """
        Chunks the doc text and stores it in Chroma
        """
        chunks = chunk_text(text)
        self.vector_service.add_document(document_id, chunks, metadata)

    def query_document(self, query_text):
        """
        Queries Chroma for relevant context
        """
        results = self.vector_service.search(query_text, top_k=3)
        context = "\n---\n".join(chunk for chunk, _ in results)
        return context

    def handle_query(self, user_msg):
        """
        Called if doc_agent is active. Could do direct usage of `query_document`.
        """
        self.logger.debug("DocAgent handling query.")

        # Example usage: "search: how does AI work?"
        if user_msg.lower().startswith("search:"):
            query_text = user_msg.split("search:")[-1]
            context = self.query_document(query_text)
            return f"Here is the relevant context:\n{context}"

        # Otherwise, you might do some fallback logic ...
        return "DocAgent: Try 'search: <your question>'."
