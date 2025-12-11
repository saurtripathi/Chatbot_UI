from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
from operator import add
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
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

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def get_chat_response(state:ChatState):

        messages = state["messages"]
        response = model.invoke(messages)
        return {"messages":[response]}

def build_graph():
    graph = StateGraph(ChatState)
    graph.add_node("chat_node",get_chat_response)
    graph.add_edge(START, "chat_node")
    graph.add_edge("chat_node",END)
    return graph




# checkpointer = get_checkpointer()
# config = {"configurable": {"thread_id": "user-123" }, "checkpointer":checkpointer}
def invoke_and_save_chat(thread_id):
     
    with PostgresSaver.from_conn_string(DB_URL) as checkpointer:
        checkpointer.setup()
        chatBot = build_graph().compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id }}
        return chatBot

        # result = chatBot.invoke(
        #     {"messages":[HumanMessage(content="what is capital of japan")]},
        #     config=config
        # )

    checkpoints = checkpointer.list(config=config)
# Iterate through the checkpoints and extract messages
    for checkpoint_data in checkpoints:

    # Access the checkpoint content, which contains the channel values
        checkpoint_state = checkpoint_data.checkpoint
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
def get_threads():
    arr = []
    with PostgresSaver.from_conn_string(get_db_url()) as checkpointer:
            # checkpointer.setup()
            checkpoints = checkpointer.list(None)
            for checkpoint in checkpoints:
                arr.append(checkpoint[0]['configurable']['thread_id'])

            arr = list(set(arr))
    return arr

print(get_threads())