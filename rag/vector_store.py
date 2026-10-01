import os

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()


VECTOR_STORE_BASE_PATH = "rag/vector_stores"


def get_embeddings():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key not found. Check your .env file."
        )

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )


def get_user_vector_store_path(user_id: int):
    return os.path.join(
        VECTOR_STORE_BASE_PATH,
        f"user_{user_id}"
    )


def create_vector_store(
    pdf_path: str,
    user_id: int,
    document_id: int
):
    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Split document into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    # Add document information to every chunk
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id
        chunk.metadata["user_id"] = user_id

    # Create embeddings
    embeddings = get_embeddings()

    # Get user's vector store path
    vector_store_path = get_user_vector_store_path(user_id)

    os.makedirs(
        vector_store_path,
        exist_ok=True
    )

    # If user already has a vector store,
    # add the new document to it.
    if os.path.exists(
        os.path.join(vector_store_path, "index.faiss")
    ):
        vector_store = FAISS.load_local(
            vector_store_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        new_vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )

        vector_store.merge_from(new_vector_store)

    else:
        # Create a new vector store for this user
        vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )

    # Save user's vector store
    vector_store.save_local(
        vector_store_path
    )

    return len(chunks)


def load_vector_store(user_id: int):
    # Create embeddings
    embeddings = get_embeddings()

    # Get user's vector store path
    vector_store_path = get_user_vector_store_path(user_id)

    index_path = os.path.join(
        vector_store_path,
        "index.faiss"
    )

    if not os.path.exists(index_path):
        return None

    vector_store = FAISS.load_local(
        vector_store_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_store
def delete_document_from_vector_store(
    user_id: int,
    document_id: int
):
    vector_store = load_vector_store(user_id)

    if vector_store is None:
        return False

    ids_to_delete = []

    for index, docstore_id in vector_store.index_to_docstore_id.items():
        document = vector_store.docstore.search(docstore_id)

        if document is None:
            continue

        if document.metadata.get("document_id") == document_id:
            ids_to_delete.append(docstore_id)

    if not ids_to_delete:
        return False

    vector_store.delete(ids_to_delete)

    vector_store_path = get_user_vector_store_path(user_id)

    vector_store.save_local(vector_store_path)

    return True