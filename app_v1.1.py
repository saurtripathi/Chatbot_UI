from  backend_updated import get_db_url,invoke_and_save_chat, build_graph, get_threads
import streamlit as st
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.postgres import PostgresSaver
import uuid

def generate_thread_id():
    return uuid.uuid4()


def reset_chat():
    thread_id = generate_thread_id()
    add_thread(thread_id)
    st.session_state['thread_id'] = thread_id
    st.session_state['message_history'] = []

def add_thread(th_id):
    thread_id = th_id
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
        with PostgresSaver.from_conn_string(get_db_url()) as checkpointer:
            chatbot = build_graph().compile(checkpointer=checkpointer)
            return chatbot.get_state(config={"configurable":{"thread_id":thread_id}}).values['messages']

# *************************** Side bar UI ********
st.sidebar.title('Chatbot')
if st.sidebar.button("New Chat"):
     reset_chat()
st.sidebar.header("Conversation history")
# **************************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = get_threads()

add_thread(st.session_state['thread_id'])

for thread_id in  st.session_state['chat_threads']:
        if st.sidebar.button(str(thread_id)):
             st.session_state['thread_id'] = thread_id
             if len(st.session_state['chat_threads'])==1:
                  break
             if st.session_state['thread_id'] not in get_threads():
                  break
             messages = load_conversation(thread_id) 
             temp_messages = []
             for message in messages:
                  if isinstance(message, HumanMessage):
                       role = 'user'
                  else:
                       role='assistant'  
                  temp_messages.append({'role':role,'content':message.content})  
             st.session_state['message_history'] = temp_messages

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])



user_input =  st.chat_input("Type here")

if user_input:
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    # CONFIG = {"configurable":{"thread_id":st.session_state['thread_id']}}
    # CONFIG updated to store the threads in langsmith project metadata
    CONFIG = {
         "configurable":{
              "thread_id":st.session_state['thread_id']
              },
        "metadata":{
             "thread_id":st.session_state['thread_id']
        },
        "run_name":"chatbot_execution"
         }
    
    with PostgresSaver.from_conn_string(get_db_url()) as checkpointer:
        checkpointer.setup()
        chatbot = build_graph().compile(checkpointer=checkpointer)
        with st.chat_message('assistant'):
                ai_message = st.write_stream(
                    message_chunk.content for message_chunk, metadata in chatbot.stream(
                        {"messages":[HumanMessage(content=user_input)]},
                        config=CONFIG,stream_mode='messages')
                )
        st.session_state['message_history'].append({'role':'assistant','content':ai_message})


    
