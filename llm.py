from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from prompt import system_prompt
from helper_functions import *
import os

# Load the environment variables
load_dotenv()

def create_agent():

    # Create an LLM model using Groq and Gpt open source
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b")

    # Create a tool object using Tavily Search
    search_tool = TavilySearch(
        max_results = 3,
        topic = "general"
    )

    coin_tool = Tool(
        name="get_coin_indicators",
        func=get_coin_indicators,
        description = "Useful for getting the current price, RSI, MACD, and trend analysis of a cryptocurrency. Accepts names (Bitcoin) or symbols (BTC)."
    )
    
    # Create an AI agent by merging the llm with the tool
    agent = create_react_agent(llm, [search_tool, coin_tool], prompt=system_prompt)

    return agent


if __name__ == "__main__":
    agent = create_agent()
    print(get_agent_response(agent, "Should I buy ethereum?"))





