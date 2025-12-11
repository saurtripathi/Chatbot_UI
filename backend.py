from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_deepseek import ChatDeepSeek
import psycopg2
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from checkpoint import get_checkpointer, DB_URL
import os, sys
import asyncio
from psycopg.rows import dict_row

load_dotenv()



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






# checkpointer = get_checkpointer()
# config = {"configurable": {"thread_id": "user-123" }, "checkpointer":checkpointer}

with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
    checkpointer.setup()
    # graph = StateGraph(ChatState)
    # graph.add_node("get_chat_response",get_chat_response)
    # graph.add_edge(START, "get_chat_response")
    # graph.add_edge("get_chat_response",END)
    # chatBot = graph.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "user-123" }}
    # # mermaid_code = chatBot.get_graph().draw_mermaid_png()
    # # with open("chatbot_o1.png",'wb') as f:
    # #         f.write(mermaid_code)
    # result = chatBot.invoke(
    #       {"messages":[HumanMessage(content="what is capital of india")]},
    #       config=config
    # )

# print(result)
    thread_set = set()
    checkpoints = checkpointer.list(config=config)
    # print(checkpoints)

# Iterate through the checkpoints and extract messages
    for checkpoint_data in checkpoints:

    # Access the checkpoint content, which contains the channel values
        checkpoint_state = checkpoint_data.checkpoint
        thread_set.add(checkpoint_data[0]['configurable']['thread_id'])
    # Get the messages channel if it exists
        # print(checkpoint_state)
        messages_channel = checkpoint_state.get("channel_values", {}).get("messages", [])

    # Iterate through the messages in the channel
        for msg in messages_channel:
            if isinstance(msg, HumanMessage):
                print(f"Human: {msg.content}")
            # elif isinstance(msg, AIMessage):
            #     print(f"AI: {msg.content}")
            # else:
            #     print(f"Other message type: {msg}")
            else:
                 print(f"AI: {msg.content}")

    print("-" * 20) # Separator for different checkpoints
    print(list(thread_set))

