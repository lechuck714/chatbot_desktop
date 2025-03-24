from base_agent import BaseAgent
from services.vector_service import VectorService
from utils.chunker import chunk_text


class DocAgent(BaseAgent):
    def __init__(self, blackboard):
        super().__init__(blackboard)
        self.vector_service = VectorService()

    def ingest_document(self, document_id, text, metadata=None):
        chunks = chunk_text(text)
        self.vector_service.add_document(document_id, chunks, metadata)

    def query_document(self, query_text):
        results = self.vector_service.search(query_text, top_k=3)
        context = "\n---\n".join(chunk for chunk, _ in results)
        return context


if __name__ == "__main__":
    from storage.blackboard import Blackboard

    blackboard = Blackboard()

    agent = DocAgent(blackboard=blackboard)  # Now matches the new constructor definition

    # Ingest a sample document
    document_id = "sample1"
    document_text = (
        "Artificial intelligence makes it possible for machines to learn from experience, "
        "adjust to new inputs, and perform human-like tasks. "
        "Most AI examples today rely heavily on deep learning and natural language processing."
    )

    agent.ingest_document(document_id, document_text)

    # Perform a semantic search/query
    query = "How do machines mimic human behavior?"
    result_context = agent.query_document(query)

    print("Retrieved context from ChromaDB:")
    print(result_context)
