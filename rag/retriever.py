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

    # Use get_or_create_collection to prevent NotFoundError
    collection = client.get_or_create_collection(
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

    print("\nWHERE FILTER:")
    print(where_filter)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where=where_filter
        )
        print("\n" + "=" * 60)
        print("CHROMA RESULTS")
        print(results)
        print("=" * 60)
    except Exception as e:
        print("\nCHROMADB QUERY ERROR:")
        print(e)
        return []

    documents = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])

    if not documents:
        return []

    documents = documents[0]
    if metadatas:
        metadatas = metadatas[0]
    else:
        metadatas = []

    print("\nMETADATA FOUND:")
    print(metadatas)

    formatted_results = []
    for index, doc in enumerate(documents):
        meta = None
        if index < len(metadatas):
            meta = metadatas[index]

        source = ""
        if isinstance(meta, dict):
            source = meta.get("source", "")

        formatted_results.append(
            {
                "content": doc,
                "source": source
            }
        )

    print("\nFORMATTED RESULTS:")
    print(formatted_results)

    return formatted_results