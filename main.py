from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from tools.error_analyzer import error_analyzer

from tools.calculator import calculator
from tools.code_analyzer import code_analyzer


# Load environment variables
load_dotenv()


# Create Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)


# Give Gemini access to BOTH tools
tools = [
    calculator,
    code_analyzer,
    error_analyzer
]

llm_with_tools = llm.bind_tools(tools)


# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Developer Agent
def developer_agent(state: State):

    print("Developer Agent is running...")

    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }


# Create graph
graph = StateGraph(State)


# Add Developer Agent
graph.add_node("developer_agent", developer_agent)


# Add Tool Node
graph.add_node(
    "tools",
    ToolNode(tools)
)


# Start → Developer Agent
graph.add_edge(START, "developer_agent")


# Developer Agent → Tool OR END
graph.add_conditional_edges(
    "developer_agent",
    tools_condition
)


# Tool → Developer Agent
graph.add_edge("tools", "developer_agent")


# Compile
app = graph.compile()


# Test the assistant
result = app.invoke({
    "messages": [
        HumanMessage(
            content="Analyze this Python error: NameError: name 'username' is not defined"
        )
    ]
})


print("\nAI Developer Assistant:")

for message in result["messages"]:
    if message.content:
        print(message.content)