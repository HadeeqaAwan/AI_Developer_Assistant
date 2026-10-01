
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from langchain_core.messages import HumanMessage, AIMessage

from auth.routes import router as auth_router
from auth.dependencies import get_current_user

from database.database import get_db
from database.models import User
from database.chat_models import Conversation, Message

from api.conversation_routes import router as conversation_router
from api.document_routes import router as document_router

from multi_agent import app as agent_app

from rag.search import get_document_context


app = FastAPI(
    title="AI Developer Assistant API",
    description="FastAPI backend for the AI Developer Assistant",
    version="1.0.0"
)


# Include routers
app.include_router(auth_router)
app.include_router(conversation_router)

app.include_router(document_router)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Chat request model
class ChatRequest(BaseModel):
    message: str
    conversation_id: int


# Chat response model
class ChatResponse(BaseModel):
    response: str
    conversation_id: int


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "AI Developer Assistant API is running"
    }


# Health endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Check for empty message
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    # Find the logged-in user
    user = db.query(User).filter(
        User.email == current_user
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check that the conversation belongs to this user
    conversation = db.query(Conversation).filter(
        Conversation.id == request.conversation_id,
        Conversation.user_id == user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Save user's new message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    db.add(user_message)
    db.commit()

    try:

        # Get all previous messages from this conversation
        previous_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.id).all()

        # Build message history for LangGraph
        chat_messages = []

        for message in previous_messages:

            if message.role == "user":
                chat_messages.append(
                    HumanMessage(
                        content=message.content
                    )
                )

            elif message.role == "assistant":
                chat_messages.append(
                    AIMessage(
                        content=message.content
                    )
                )

        # Get relevant information from the document
        document_context = get_document_context(
    request.message,
    user.id,
    k=3
)

        # Add document context to the user's question
        rag_message = HumanMessage(
            content=(
                "Use the following document context when it is "
                "relevant to the user's question.\n\n"
                "DOCUMENT CONTEXT:\n"
                f"{document_context}\n\n"
                "USER QUESTION:\n"
                f"{request.message}"
            )
        )

        # Send conversation history + document context to LangGraph
        result = agent_app.invoke(
            {
                "messages": chat_messages + [rag_message]
            }
        )

        # Extract final AI response
        final_response = ""

        for message in reversed(result["messages"]):

            if not hasattr(message, "content"):
                continue

            content = message.content

            # Handle list-based content
            if isinstance(content, list):

                text_parts = []

                for item in content:

                    if isinstance(item, dict):

                        if item.get("type") == "text":
                            text_parts.append(
                                item.get("text", "")
                            )

                        elif "text" in item:
                            text_parts.append(
                                item["text"]
                            )

                    elif isinstance(item, str):
                        text_parts.append(item)

                final_response = "\n".join(
                    text_parts
                ).strip()

            # Handle normal string content
            elif isinstance(content, str):

                final_response = content.strip()

            # Handle other content types
            else:

                final_response = str(content)

            if final_response:
                break

        # Fallback response
        if not final_response:
            final_response = (
                "I was unable to generate a response."
            )

        # Save AI response to database
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=final_response
        )

        db.add(assistant_message)
        db.commit()

        # Return response
        return ChatResponse(
            response=final_response,
            conversation_id=conversation.id
        )

    except Exception as e:

        # Rollback database changes if something fails
        db.rollback()

        print("ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the request."
        )
