import pandas as pd
import pandas_ta_classic as ta
from pycoingecko import CoinGeckoAPI
import requests
import json
from pydantic import BaseModel, Field
from langchain_core.tools import tool
import os

# Initialize the api
demo_api_key=os.getenv("COINGECKO_API_KEY")
cg = CoinGeckoAPI(demo_api_key=demo_api_key)

def get_agent_response(agent, user_input):
    # Make a call to the agent and return the response
    resp = agent.invoke({"messages": user_input})

    # Return the response based on the number of tools used
    return resp["messages"][-1].content

def get_coin_name(query : str):
    """
    Normalizes a user's coin query into a valid CoinGecko API ID.
    
    This function handles the ambiguity between ticker symbols (e.g., 'ETH') 
    and full coin names (e.g., 'ethereum'). It first attempts to use the input 
    directly as an ID. If that fails (returns no price), it searches the market 
    list to resolve the symbol to its primary ID.

    Args:
        query (str): The raw user input (e.g., 'BTC', 'bitcoin', 'eth').

    Returns:
        str: The valid API ID string (e.g., 'bitcoin', 'ethereum').
    """
    global cg
    query = query.lower().strip()

    # Get the price of the coin if query is a valid name
    price = cg.get_price(ids=query, vs_currencies="usd")

    # If price is empty
    if not price:
        # Get the name of the coin if query is a symbol
        query = cg.get_coins_markets(
            symbols=query,
            vs_currency="usd"
        )[0]["id"]

    coin = cg.get_coin_by_id(query)
    symbol = coin["symbol"].upper()
    return query, symbol


class GetCoinIndicators(BaseModel):
    query : str = Field(description="query (str): The valid API ID of the coin (e.g., 'bitcoin').")

@tool(args_schema=GetCoinIndicators)
def get_coin_indicators(query : str):
    """
    Orchestrates the retrieval and analysis of technical market data.
    
    This function acts as a pipeline that:
    1. Fetches 30 days of OHLC (Open, High, Low, Close) data.
    2. Calculates key technical indicators (EMA, RSI, MACD).
    3. Generates a natural language summary of the asset's health.

    Args:
        query (str): The valid API ID of the coin (e.g., 'bitcoin').

    Returns:
        str: A formatted text summary comprising current price, trend direction, 
             momentum signals, and RSI status.
    """
    global cg

    # Get the name of the coin
    query, symbol = get_coin_name(query)

    # # Get market data about the coin over the past n days
    # market_list = get_coin_ohlc(symbol)

    # Get market data about the coin over the past n days
    market_list = cg.get_coin_ohlc_by_id(id=query, vs_currency="usd", days=30)

    # Get the summary of the coin
    summary = get_coin_summary(market_list, query)

    return summary


def get_coin_ohlc(symbol : str):
    # Returns the ohlc history of a coin based on the coin name

    # Define the request url
    key = "https://api.binance.us/api/v3/klines?symbol="+symbol+"USDT&interval=1h&limit=225"

    # Requesting data from the url
    data = requests.get(key)
    data = data.json()

    market_data = []
    for candle in data:
        # Add the useful columns of candle data to market data
        market_data.append(candle[:5])

    return market_data

def get_coin_data(market_list):

    # Convert the market list to a dataframe
    coin_data = pd.DataFrame(market_list, columns=["Time","Open","High","Low","Close"])

    # Calculate EMA of the coin
    coin_data["EMA_50"] = coin_data.ta.ema(close="Close", length=50)
    coin_data["EMA_100"] = coin_data.ta.ema(close="Close", length=100)
    coin_data["EMA_150"] = coin_data.ta.ema(close="Close", length=150)

    # Calculate RSI of the coin
    coin_data["RSI_6"] = coin_data.ta.rsi(close="Close", length=6)

    # Calculate MACD of the coin
    macd_data = coin_data.ta.macd(close="Close", fast=12, slow=26, signal=9)
    coin_data = pd.concat([coin_data, macd_data], axis=1)


    return coin_data.iloc[-1]


def get_coin_summary(market_list, query):
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


