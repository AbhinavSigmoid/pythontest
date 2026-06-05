import chromadb
import uuid


def store_chunks(chunks, embeddings):

    client = chromadb.PersistentClient(
        path="data/chroma_db"
    )

    collection = client.get_or_create_collection(
        name="de_documents"
    )

    if chunks:
        import os
        file_name = chunks[0]["file_name"]
        basename = os.path.basename(file_name)
        try:
            # Delete any existing chunks for this file to avoid duplicates
            collection.delete(where={"source": file_name})
            collection.delete(where={"source": basename})
            collection.delete(where={"source": os.path.join("uploads", basename)})
            collection.delete(where={"source": os.path.abspath(file_name)})
            print(f"Old chunks for '{basename}' cleared")
        except Exception as e:
            print(f"Error clearing old chunks for '{basename}': {e}")

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