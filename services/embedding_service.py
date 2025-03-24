# embedding_service.py

from config.config import client


def get_embedding(text, model="text-embedding-ada-002"):
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding
