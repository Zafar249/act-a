import pandas as pd
import pandas_ta_classic as ta

def get_agent_response(agent, user_input):
    # Make a call to the agent and return the response
    resp = agent.invoke({"messages": user_input})

    try:
        # If both tools are called
        return resp["messages"][5].content
    
    except:
        try:
            # If only 1 tool is called
            return resp["messages"][3].content
        
        except:
            # If no tool is called
            return resp["messages"][1].content
        

def get_coin_data(market_list):

    # Convert the market list to a dataframe
    coin_data = pd.DataFrame(market_list, columns=["Time","Open","High","Low","Close"], dtype=pd.Float64Dtype)

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