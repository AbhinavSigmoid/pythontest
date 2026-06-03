from ingestion.txt_loader import load_documents
from ingestion.chunker import create_chunks


documents = load_documents("docs")

chunks = create_chunks(documents)

print("\nChunks Created:\n")

for index, chunk in enumerate(chunks[:10]):

    print("=" * 50)

    print("Chunk Number:", index + 1)

    print("Source File:", chunk["file_name"])

    print()

    print(chunk["chunk"])

    print()