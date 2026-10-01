from rag.vector_store import load_vector_store


def search_documents(
    query: str,
    user_id: int,
    k: int = 3
):
    vector_store = load_vector_store(user_id)

    if vector_store is None:
        return []

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


def get_document_context(
    query: str,
    user_id: int,
    k: int = 3
):
    results = search_documents(
        query,
        user_id,
        k
    )

    if not results:
        return ""

    context = "\n\n".join(
        result.page_content
        for result in results
    )

    return context