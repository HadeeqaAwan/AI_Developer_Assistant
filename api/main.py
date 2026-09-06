from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from multi_agent import app as agent_app


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Developer Assistant API",
    description="FastAPI backend for the AI Developer Assistant",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):
    response: str


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Developer Assistant API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # Check empty message
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:

        # ----------------------------------------------------
        # Send request to LangGraph multi-agent system
        # ----------------------------------------------------

        result = agent_app.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=request.message
                    )
                ]
            }
        )

        # ----------------------------------------------------
        # Extract final response
        # ----------------------------------------------------

        final_response = ""

        for message in reversed(result["messages"]):

            if not hasattr(message, "content"):
                continue

            content = message.content

            # Gemini may return content as a list
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

            # Normal string response
            elif isinstance(content, str):

                final_response = content.strip()

            else:

                final_response = str(content)

            if final_response:
                break

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        if not final_response:
            final_response = (
                "I was unable to generate a response."
            )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return ChatResponse(
            response=final_response
        )

    except Exception as e:

        print("ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the request."
        )