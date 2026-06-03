from rag.retriever import search_documents


query = "What is the SLA of Orders Pipeline?"

results = search_documents(query)

print("\nRetrieved Results:\n")

for doc in results["documents"][0]:

    print("=" * 50)

    print(doc)

    print()