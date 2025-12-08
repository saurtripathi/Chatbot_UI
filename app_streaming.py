import backend
import streamlit as st
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


user_input =  st.chat_input("Type here")

thread_id = 1

if user_input:
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
        initial_state = {"messages":[HumanMessage(content=user_input)]}
        config = {"configurable":{"thread_id":thread_id}}
        final_state = backend.chatBot.invoke(initial_state,config=config)
        final_state = final_state['messages'][-1].content
        with st.chat_message('assistant'):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in backend.chatBot.stream(initial_state,config=config,stream_mode='messages')
            )
        st.session_state['message_history'].append({'role':'assistant','content':ai_message})


    
