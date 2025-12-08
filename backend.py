from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
from operator import add
from dotenv import load_dotenv

from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
checkpointer = InMemorySaver()
model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=1000,
    timeout=None,
    max_retries=2,
)

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def get_chat_response(state:ChatState):

        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages":[response]}


graph = StateGraph(ChatState)
graph.add_node("get_chat_response",get_chat_response)
graph.add_edge(START, "get_chat_response")
graph.add_edge("get_chat_response",END)


chatBot = graph.compile(checkpointer=checkpointer)


mermaid_code = chatBot.get_graph().draw_mermaid_png()
with open("chatbot_o1.png",'wb') as f:
    f.write(mermaid_code)


