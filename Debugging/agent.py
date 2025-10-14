from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import START, END
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage

import os
from dotenv import load_dotenv
load_dotenv()

os.environ['GROQ_API_KEY']=os.getenv('GROQ_API_KEY')
os.environ['LANGCHAIN_API_KEY']=os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGSMITH_TRACING']='true'
os.environ['LANGSMITH_PROJECT']='TestProject'

from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model

llm = ChatGroq(model='llama-3.3-70b-versatile')

class State(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
def call_llm_model(state:State):
    return {"messages":[llm_with_tools.invoke(state['messages'])]}
    
@tool
def add(a:int, b:int)->int:
    """
    Add two numbers a, b
    """
    return a+b
tools=[add]
tool_node = ToolNode([add])

llm_with_tools = llm.bind_functions([add])

graph = StateGraph(State)

graph.add_node("tool_calling_llm", call_llm_model)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "tool_calling_llm")
graph.add_conditional_edges("tool_calling_llm",tools_condition)
graph.add_edge("tools", "tool_calling_llm")
tool_agent=graph.compile()