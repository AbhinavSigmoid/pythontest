import chromadb
import uuid


def store_chunks(chunks, embeddings):

    client = chromadb.PersistentClient(
        path="data/chroma_db"
    )

    collection = client.get_or_create_collection(
        name="de_documents"
    )

    try:

        existing = collection.get()

        if existing["ids"]:

            collection.delete(
                ids=existing["ids"]
            )

            print(
                "Old documents cleared"
            )

    except Exception:
        pass

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:

        ids.append(
            str(uuid.uuid4())
        )

        documents.append(
            chunk["chunk"]
        )

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

    print(
        "Chunks stored successfully"
    )