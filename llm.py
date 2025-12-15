from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv
from prompt import system_prompt
from helper_functions import *
import os

# Load the environment variables
load_dotenv()

def get_coin_indicators(query : str):
    """
    Analyzes a cryptocurrency's current price and technical indicators (RSI, MACD, EMA).
    
    Args:
        query (str): The full name (e.g., 'bitcoin') or ticker symbol (e.g., 'BTC').
    
    Returns:
        str: A summary of the price and technical analysis.
    """

    # Initialize the api
    # demo_api_key=os.getenv("COINGECKO_API_KEY")
    cg = CoinGeckoAPI()
    query = query.lower().strip()

    try:
        # Get the price of the coin if query is a valid symbol
        price = cg.get_price(ids=query, vs_currencies="usd")

    except:
        try:
            # Get the symbol of the coin if query is the name
            query = cg.get_coins_markets(
                symbols=query,
                vs_currency="usd"
            )[0]["id"]

            # Get the price of the coin if query is a valid symbol
            price = cg.get_price(ids=query, vs_currencies="usd")

        except:
            pass

    # Get market data about the coin over the past n days
    market_list = cg.get_coin_ohlc_by_id(id=query, vs_currency="usd", days=30)

    latest = get_coin_data(market_list)

    # Determine Trend based on EMA
    trend = "Bullish" if latest["Close"] > latest["EMA_50"] else "Bearish"
    
    # Determine Momentum based on MACD Histogram
    momentum = "Positive" if latest["MACDh_12_26_9"] > 0 else "Negative"

    summary = (
        f"Analysis for {query.capitalize()}:\n"
        f"- Current Price: ${latest['Close']:.2f}\n"
        f"- Trend (vs EMA 50): {trend}\n"
        f"- RSI (6): {latest['RSI_6']:.2f} (Over 70=Overbought, Under 30=Oversold)\n"
        f"- MACD Momentum: {momentum} (Histogram: {latest['MACDh_12_26_9']:.2f})"
    )
    return summary


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
    print(get_agent_response(agent, "Get me the current price of ethereum and the news about it."))


