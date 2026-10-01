from rag.search import search_documents


query = "What career guidance is provided in the document?"

results = search_documents(query, k=3)

print("\nRetrieved Documents:\n")

for i, result in enumerate(results, start=1):

    print(f"--- Result {i} ---")
    print(result.page_content)
    print()