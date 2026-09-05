from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools.error_analyzer import error_analyzer


# --------------------------------
# 1. Define State
# --------------------------------

class State(TypedDict):
    messages: Annotated[list, add_messages]


# --------------------------------
# 2. Create Gemini model
# --------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)


# --------------------------------
# 3. Define Debug Agent tools
# --------------------------------

debug_tools = [
    error_analyzer
]


# --------------------------------
# 4. Bind tools to Gemini
# --------------------------------

debug_llm = llm.bind_tools(debug_tools)


# --------------------------------
# 5. Debug Agent
# --------------------------------

def debug_agent(state: State):

    print("Debug Agent is running...")

    response = debug_llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# --------------------------------
# 6. Tool Node
# --------------------------------

tool_node = ToolNode(debug_tools)


# --------------------------------
# 7. Create Graph
# --------------------------------

graph = StateGraph(State)

graph.add_node("debug_agent", debug_agent)
graph.add_node("tools", tool_node)


# --------------------------------
# 8. Define Flow
# --------------------------------

graph.add_edge(START, "debug_agent")

graph.add_conditional_edges(
    "debug_agent",
    tools_condition
)

graph.add_edge("tools", "debug_agent")


# --------------------------------
# 9. Compile
# --------------------------------

app = graph.compile()


# --------------------------------
# 10. Test
# --------------------------------

if __name__ == "__main__":

    result = app.invoke({
        "messages": [
            HumanMessage(
                content="Analyze this error: NameError: name 'username' is not defined"
            )
        ]
    })

    print("\n========== DEBUG AGENT RESULT ==========")

    for message in result["messages"]:

        if message.content:
            print(message.content)