from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools.calculator import calculator
from tools.code_analyzer import code_analyzer


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
# 3. Define Coding Agent tools
# --------------------------------

coding_tools = [
    calculator,
    code_analyzer
]


# --------------------------------
# 4. Bind tools to Gemini
# --------------------------------

coding_llm = llm.bind_tools(coding_tools)


# --------------------------------
# 5. Coding Agent
# --------------------------------

def coding_agent(state: State):

    print("Coding Agent is running...")

    response = coding_llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# --------------------------------
# 6. Tool Node
# --------------------------------

tool_node = ToolNode(coding_tools)


# --------------------------------
# 7. Create Graph
# --------------------------------

graph = StateGraph(State)

graph.add_node("coding_agent", coding_agent)
graph.add_node("tools", tool_node)


# --------------------------------
# 8. Define Flow
# --------------------------------

graph.add_edge(START, "coding_agent")

graph.add_conditional_edges(
    "coding_agent",
    tools_condition
)

graph.add_edge("tools", "coding_agent")


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
                content="Calculate 25 * 48"
            )
        ]
    })

    print("\n========== CODING AGENT RESULT ==========")

    for message in result["messages"]:

        if message.content:
            print(message.content)