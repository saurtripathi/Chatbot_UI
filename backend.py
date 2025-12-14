from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode, tools_condition
from tools import get_weather_data, search_tool, wikipedia_tool, math_tool

import os


load_dotenv()

def get_db_url():
     return f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'

model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=1000,
    timeout=None,
    max_retries=2,
)
tools = [get_weather_data,search_tool, wikipedia_tool, math_tool]
tools_enabled_llm = model.bind_tools(tools)
tool_node = ToolNode(tools)
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:ChatState):
    messages = state["messages"]
    response = tools_enabled_llm.invoke(messages)
    return {"messages":[response]}

def build_graph():

    graph = StateGraph(ChatState)

    graph.add_node("chat_node",chat_node)
    graph.add_node("tools",tool_node)

    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge("tools","chat_node")

    return graph


def get_threads():
    arr = []
    with PostgresSaver.from_conn_string(get_db_url()) as checkpointer:
            checkpointer.setup()
            checkpoints = checkpointer.list(None)
            for checkpoint in checkpoints:
                arr.append(checkpoint[0]['configurable']['thread_id'])

            arr = list(set(arr))
    return arr
