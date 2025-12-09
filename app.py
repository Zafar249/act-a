import streamlit as st
from llm import create_agent, get_agent_response

# Set the configurations of the page
st.set_page_config(page_title="Act-A")

# Create a title for the page
st.title("AI Crypto Trading Agent")


user_input = st.text_input("Enter your query: ")

if user_input:
    # Create the react agent
    agent = create_agent()

    # Get the response of the agent and write it to the page.
    response = get_agent_response(agent, user_input)
    st.write(response)