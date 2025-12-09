from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv
import os

# Load the environment variables
load_dotenv()

def get_coin_price(query : str):
    """
    Retrieves the current price of a cryptocurrency in USD. 
    This tool can handle both full coin names (e.g., 'bitcoin') and ticker symbols (e.g., 'BTC', 'ETH').
    
    Args:
        query (str): The name or symbol of the coin to look up.
    """

    # Initialize the api
    # demo_api_key=os.getenv("COINGECKO_API_KEY")
    cg = CoinGeckoAPI()
    query = query.lower().strip()

    try:
        # Get the price of the coin if query is a valid symbol
        price = cg.get_price(ids=query, vs_currencies="usd")

        return price[query]["usd"]
    except:
        pass

    try:
        # Get the symbol of the coin if query is the name
        query = cg.get_coins_markets(
            symbols=query,
            vs_currency="usd"
        )[0]["id"]

        # Get the price of the coin if query is a valid symbol
        price = cg.get_price(ids=query, vs_currencies="usd")

        return price[query]["usd"]
        
    except:
        print("An error occured")


def create_agent():

    # Create an LLM model using Groq and Gpt open source
    llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-20b")

    # Create a tool object using Tavily Search
    search_tool = TavilySearch(
        max_results = 3,
        topic = "general"
    )

    coin_tool = Tool(
        name="get_coin_price",
        func=get_coin_price,
        description = "Useful for finding the current price of any crypto. Accepts both full names (Bitcoin) and symbols (BTC)."
    )
    # Create an AI agent by merging the llm with the tool
    agent = create_react_agent(llm, [search_tool, coin_tool])

    return agent


def get_agent_response(agent, user_input):
    # Make a call to the agent and return the response
    resp = agent.invoke({"messages": user_input})

    try:
        return resp["messages"][3].content
    except:
        return resp["messages"][1].content

if __name__ == "__main__":
    agent = create_agent()
    print(get_agent_response(agent, "What is the current price of DOGE?"))

