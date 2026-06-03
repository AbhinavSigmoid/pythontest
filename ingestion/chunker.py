def create_chunks(documents, chunk_size=300, overlap=50):

    chunks = []

    for doc in documents:

        text = doc["content"]

        file_name = doc["file_name"]

        start = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append(
                {
                    "file_name": file_name,
                    "chunk": chunk_text
                }
            )

            start += chunk_size - overlap

    return chunks