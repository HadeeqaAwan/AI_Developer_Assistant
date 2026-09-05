from langchain_core.tools import tool


@tool
def tech_info(topic: str) -> str:
    """Provide basic information about common AI and software technologies."""

    information = {
        "langgraph": (
            "LangGraph is a framework for building stateful, multi-step "
            "and multi-agent applications using graph-based workflows."
        ),

        "langchain": (
            "LangChain is a framework for developing applications powered "
            "by language models, including agents, tools, prompts and chains."
        ),

        "rag": (
            "RAG stands for Retrieval-Augmented Generation. "
            "It retrieves relevant information from a knowledge source "
            "and provides it to an LLM to generate a better answer."
        ),

        "llm": (
            "LLM stands for Large Language Model. "
            "It is an AI model trained to understand and generate natural language."
        ),

        "mcp": (
            "MCP stands for Model Context Protocol. "
            "It provides a standardized way for AI applications to connect "
            "with external tools and data sources."
        )
    }

    topic_lower = topic.lower()

    for key, description in information.items():
        if key in topic_lower:
            return description

    return (
        f"I don't have predefined information about '{topic}'. "
        "Try asking about LangGraph, LangChain, RAG, LLM, or MCP."
    )


if __name__ == "__main__":

    result = tech_info.invoke("What is LangGraph?")

    print(result)