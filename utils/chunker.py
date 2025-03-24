import tiktoken


def chunk_text(text, max_tokens=500, overlap=50):
    tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")
    tokens = tokenizer.encode(text)
    chunks = []

    for start_idx in range(0, len(tokens), max_tokens - overlap):
        chunk = tokens[start_idx: start_idx + max_tokens]
        chunks.append(tokenizer.decode(chunk))

    return chunks
