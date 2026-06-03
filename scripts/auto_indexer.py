import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import create_chunks
from ingestion.embeddings import create_embeddings

from rag.vector_store import store_chunks


def process_pdf(file_path):

    print("\nProcessing PDF...\n")

    text = load_pdf(file_path)

    document = {
        "file_name": file_path,
        "content": text
    }

    documents = [document]

    chunks = create_chunks(documents)

    print(
        f"Created {len(chunks)} chunks"
    )

    embeddings = create_embeddings(
        chunks
    )

    print(
        f"Created {len(embeddings)} embeddings"
    )

    store_chunks(
        chunks,
        embeddings
    )

    print(
        "\nStored in ChromaDB\n"
    )