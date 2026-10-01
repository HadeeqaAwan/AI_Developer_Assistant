from rag.vector_store import create_vector_store


pdf_path = "E:\AI_Developer_Assistant\documents\Career Guide Reference.pdf"

chunks = create_vector_store(pdf_path)

print(f"RAG setup successful.")
print(f"Number of document chunks: {chunks}")