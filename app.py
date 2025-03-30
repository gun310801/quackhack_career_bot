import streamlit as st
import pandas as pd
import numpy as np
from langchain_core.messages import HumanMessage, AIMessage
from langchain.tools import tool

st.title("Career Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "current_job": "",
        "current_salary": 0,
        "location": "",
        "years_experience": 0,
        "skills": []
    }
    
st.write("Welcome to the Career Bot! Ask me anything about your career.")

def main():
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.write(f"You: {msg.content}")
        elif isinstance(msg, AIMessage):
            st.write(f"Career Bot: {msg.content}")
    
    if prompt := st.chat_input("Enter a message"):
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.chat_message("user").markdown(prompt)

        # Process user input
        if "salary" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing salary data..."))
            st.write("Career Bot: Analyzing salary data...")
            
        if "career" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing career data..."))
            st.write("Career Bot: Analyzing career data...")
            
        if "job" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing job data..."))
            st.write("Career Bot: Analyzing job data...")

        if "transition" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing transition data..."))
            st.write("Career Bot: Analyzing transition data...")
            
        if "salary" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing salary data..."))
            st.write("Career Bot: Analyzing salary data...")
            
        if "career" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing career data..."))
            st.write("Career Bot: Analyzing career data...")

        if "job" in prompt.lower():
            st.session_state.messages.append(AIMessage(content="Analyzing job data..."))
            st.write("Career Bot: Analyzing job data...")
            
            
if __name__ == "__main__":
    main()  