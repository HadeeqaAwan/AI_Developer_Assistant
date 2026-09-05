from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


@tool
def route_to_coding_agent(request: str) -> str:
    """Route a programming or coding request to the Coding Agent."""
    return "CODING_AGENT"


@tool
def route_to_debug_agent(request: str) -> str:
    """Route a Python error or debugging request to the Debug Agent."""
    return "DEBUG_AGENT"


@tool
def route_to_research_agent(request: str) -> str:
    """Route a technology or conceptual question to the Research Agent."""
    return "RESEARCH_AGENT"


supervisor_tools = [
    route_to_coding_agent,
    route_to_debug_agent,
    route_to_research_agent
]


supervisor_llm = llm.bind_tools(supervisor_tools)


def supervisor(state):

    print("Supervisor is running...")

    response = supervisor_llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


if __name__ == "__main__":

    from langchain_core.messages import HumanMessage

    state = {
        "messages": [
            HumanMessage(
                content="Explain what LangGraph is"
            )
        ]
    }

    result = supervisor(state)

    print("\nSupervisor Response:")
    print(result["messages"][0])