from ingestion.txt_loader import load_documents


documents = load_documents("docs")

print("\nDocuments Loaded:\n")

for doc in documents:

    print("=" * 50)

    print("File:", doc["file_name"])

    print()

    print(doc["content"][:200])

    print()