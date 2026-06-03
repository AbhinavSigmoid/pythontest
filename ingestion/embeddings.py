from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def create_embeddings(chunks):

    texts = []

    for chunk in chunks:
        texts.append(chunk["chunk"])

    embeddings = model.encode(texts)

    return embeddings