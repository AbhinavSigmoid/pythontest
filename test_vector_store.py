from ingestion.txt_loader import load_documents
from ingestion.chunker import create_chunks
from ingestion.embeddings import create_embeddings

from rag.vector_store import store_chunks


documents = load_documents("docs")

chunks = create_chunks(documents)

embeddings = create_embeddings(chunks)

store_chunks(chunks, embeddings)