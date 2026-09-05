
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from agents.coding_agent import coding_agent
from agents.debug_agent import debug_agent
from agents.research_agent import research_agent

from tools.calculator import calculator
from tools.code_analyzer import code_analyzer
from tools.error_analyzer import error_analyzer
from tools.tech_info import tech_info


# --------------------------------
# 1. Define State
# --------------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str


# --------------------------------
# 2. Create Agent Nodes
# --------------------------------

def coding_node(state: State):
    print("\n>>> Coding Agent")
    return coding_agent(state)


def debug_node(state: State):
    print("\n>>> Debug Agent")
    return debug_agent(state)


def research_node(state: State):
    print("\n>>> Research Agent")
    return research_agent(state)


# --------------------------------
# 3. Create Tool Nodes
# --------------------------------

coding_tools_node = ToolNode([
    calculator,
    code_analyzer
])

debug_tools_node = ToolNode([
    error_analyzer
])

research_tools_node = ToolNode([
    tech_info
])


# --------------------------------
# 4. AI Supervisor
# --------------------------------

supervisor_llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)


def supervisor(state: State):

    message = state["messages"][-1].content

    # Gemini may return content as a list
    if isinstance(message, list):
        text_parts = []

        for item in message:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif "text" in item:
                    text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)

        message = "\n".join(text_parts)

    print("\n>>> Supervisor")

    prompt = f"""
You are the supervisor of a multi-agent AI Developer Assistant.

Choose exactly ONE starting agent for the user's request.

Available agents:

coding:
Handles Python code, programming, calculations, and code analysis.

debug:
Handles errors, exceptions, bugs, and debugging.

research:
Handles technology explanations and technical information.

User request:
{message}

Return ONLY one word:
coding
debug
research
"""

    response = supervisor_llm.invoke(prompt)

    # --------------------------------
    # Handle Gemini response content
    # --------------------------------

    content = response.content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif "text" in item:
                    text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)

        content = "\n".join(text_parts)

    # Make sure content is a string
    if not isinstance(content, str):
        content = str(content)

    next_agent = content.strip().lower()

    # --------------------------------
    # Validate supervisor decision
    # --------------------------------

    if next_agent not in ["coding", "debug", "research"]:
        next_agent = "research"

    print(f"Supervisor selected: {next_agent}")

    return {
        "next_agent": next_agent
    }


# --------------------------------
# 5. Routing Function
# --------------------------------

def route_agent(state: State):
    return state["next_agent"]


# --------------------------------
# 6. Create Graph
# --------------------------------

graph = StateGraph(State)


# Agent nodes
graph.add_node("supervisor", supervisor)
graph.add_node("coding", coding_node)
graph.add_node("debug", debug_node)
graph.add_node("research", research_node)


# Tool nodes
graph.add_node("coding_tools", coding_tools_node)
graph.add_node("debug_tools", debug_tools_node)
graph.add_node("research_tools", research_tools_node)


# --------------------------------
# 7. Supervisor → Starting Agent
# --------------------------------

graph.add_edge(START, "supervisor")

graph.add_conditional_edges(
    "supervisor",
    route_agent,
    {
        "coding": "coding",
        "debug": "debug",
        "research": "research"
    }
)


# --------------------------------
# 8. Coding Agent → Tools / END
# --------------------------------

graph.add_conditional_edges(
    "coding",
    tools_condition,
    {
        "tools": "coding_tools",
        END: END
    }
)

graph.add_edge("coding_tools", "coding")


# --------------------------------
# 9. Debug Agent → Tools / END
# --------------------------------

graph.add_conditional_edges(
    "debug",
    tools_condition,
    {
        "tools": "debug_tools",
        END: END
    }
)

graph.add_edge("debug_tools", "debug")


# --------------------------------
# 10. Research Agent → Tools / END
# --------------------------------

graph.add_conditional_edges(
    "research",
    tools_condition,
    {
        "tools": "research_tools",
        END: END
    }
)

graph.add_edge("research_tools", "research")


# --------------------------------
# 11. Compile Graph
# --------------------------------

app = graph.compile()


# --------------------------------
# 12. Clean Final Response
# --------------------------------

def get_final_response(result):

    for message in reversed(result["messages"]):

        if not message.content:
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
                            item.get("text", "")
                        )

                elif isinstance(item, str):
                    text_parts.append(item)

            content = "\n".join(text_parts)

        if isinstance(content, str) and content.strip():
            return content.strip()

    return "No response generated."


# --------------------------------
# 13. Interactive Test
# --------------------------------

if __name__ == "__main__":

    print("\n===================================")
    print("AI Developer Assistant")
    print("Type 'exit' to quit.")
    print("===================================")

    conversation = []

    while True:

        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        conversation.append(
            HumanMessage(content=user_input)
        )

        result = app.invoke({
            "messages": conversation,
            "next_agent": ""
        })

        conversation = result["messages"]

        print("\nAI Developer Assistant:")
        print(get_final_response(result))

