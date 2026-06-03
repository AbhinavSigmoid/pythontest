import chromadb


def store_chunks(chunks, embeddings):

    client = chromadb.PersistentClient(
        path="data/chroma_db"
    )

    collection = client.get_or_create_collection(
        name="de_documents"
    )

    ids = []

    documents = []

    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(f"chunk_{i}")

        documents.append(chunk["chunk"])

        metadatas.append(
            {
                "source": chunk["file_name"]
            }
        )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("Chunks stored successfully")