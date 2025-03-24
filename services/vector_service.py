import chromadb
from chromadb.utils import embedding_functions
from services.embedding_service import get_embedding


class VectorService:
    def __init__(self, collection_name="doc_embeddings"):
        self.client = chromadb.PersistentClient(path="./vector_db")
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_document(self, document_id, chunks, metadata=None):
        from services.embedding_service import get_embedding
        embeddings = [get_embedding(chunk) for chunk in chunks]
        self.collection.add(
            ids=[f"{document_id}-{i}" for i in range(len(chunks))],
            embeddings=embeddings,
            documents=chunks,
            metadatas=None if not metadata else [metadata] * len(chunks)
        )

    def search(self, query, top_k=3):
        query_embedding = get_embedding(query)

        # Clearly structured search operation:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        matched_chunks = results['documents'][0]
        matched_metadata = results['metadatas'][0]
        return list(zip(matched_chunks, matched_metadata))
