from ingestion.txt_loader import load_documents
from ingestion.chunker import create_chunks
from ingestion.embeddings import create_embeddings


documents = load_documents("docs")

chunks = create_chunks(documents)

embeddings = create_embeddings(chunks)

print("\nNumber of Chunks:")

print(len(chunks))

print("\nEmbedding Shape:")

print(embeddings.shape)

print("\nFirst 10 Values of First Embedding:")

print(embeddings[0][:10])
