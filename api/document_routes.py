import os

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.database import get_db
from database.models import User, Document
from rag.vector_store import (
    create_vector_store,
    delete_document_from_vector_store
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find current user
    user = db.query(User).filter(
        User.email == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Save uploaded file
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Create document record first
    document = Document(
        user_id=user.id,
        filename=file.filename,
        file_path=file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Create vector store using document ID
    chunks = create_vector_store(
        file_path,
        user.id,
        document.id
    )

    return {
        "message": "Document uploaded and indexed successfully.",
        "document_id": document.id,
        "filename": document.filename,
        "chunks": chunks
    }


@router.get("/")
def get_documents(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find current user
    user = db.query(User).filter(
        User.email == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get only this user's documents
    documents = db.query(Document).filter(
        Document.user_id == user.id
    ).all()

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "created_at": document.created_at
        }
        for document in documents
    ]


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find current user
    user = db.query(User).filter(
        User.email == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Find document belonging to this user
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete physical PDF file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete document's vectors from FAISS
    delete_document_from_vector_store(
        user.id,
        document.id
    )

    # Delete document record from database
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully."
    }