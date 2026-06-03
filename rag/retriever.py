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


def search_documents(query):

    client = chromadb.PersistentClient(
        path=DB_PATH
    )

    collection = client.get_collection(
        name="de_documents"
    )

    query_embedding = model.encode(
        query
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    formatted_results = []

    for doc, meta in zip(
        documents,
        metadatas
    ):

        formatted_results.append(
            {
                "content": doc,
                "source": meta["source"]
            }
        )

    return formatted_results