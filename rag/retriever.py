import os

import chromadb

from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "chroma_db"
)


def search_documents(query, source_file=None):
    print("\nSOURCE FILE RECEIVED:", source_file)

    client = chromadb.PersistentClient(
        path=DB_PATH
    )

    collection = client.get_collection(
        name="de_documents"
    )

    query_embedding = model.encode(
        query
    ).tolist()

    where_filter = None
    if source_file:
        basename = os.path.basename(source_file)
        abs_path = os.path.join(BASE_DIR, "uploads", basename)
        where_filter = {
            "$or": [
                {"source": abs_path},
                {"source": os.path.join("uploads", basename)},
                {"source": basename}
            ]
        }
    print("WHERE FILTER:")
    print(where_filter)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=where_filter
        )
    except Exception as e:
        print("CHROMADB QUERY ERROR:", e)
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    print("\nMETADATA FOUND:")
    print(metadatas)

    formatted_results = []
    for doc, meta in zip(
        documents,
        metadatas
    ):
        formatted_results.append(
            {
                "content": doc,
                "source": meta.get("source", "")
            }
        )

    return formatted_results