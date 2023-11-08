import numpy as np
import pandas as pd
import yfinance as yf

from market_data_utils.polygon import Polygon

class StaticNasdaq(): # static nasdaq data from 2023
    def __init__(self):
        self._static_df : pd.DataFrame = pd.read_csv("data/nasdaq_screener.csv")
        self._static_df.drop(["Last Sale", "Net Change", "% Change", "Market Cap"], axis=1, inplace=True)
    
    @property
    def data(self) -> pd.DataFrame:
        return self._static_df
    
    @property
    def tickers(self) -> pd.Series:
        return self._static_df["Symbol"]
    
    @property
    def sectors(self) -> np.ndarray:
        return self._static_df["Sector"].unique()
    
    @property
    def industries(self) -> np.ndarray:
        return self._static_df["Industry"].unique()
    
    def get_company_name(self, ticker: str):
        return self._static_df.loc[self._static_df["Symbol"] == ticker].head(1)["Name"]

def market_status():
    poly = Polygon()
    return poly.exchange_status("nasdaq")

def calculate_risk_free_rate(): # calculate risk free rate from t-bills
    def deannualize(annual_rate, periods=(365//4)):
        return (1 + annual_rate) ** (1/periods) - 1

    def get_risk_free_rate():
        annualized = yf.download("^IRX")["Adj Close"]
        daily = annualized.apply(deannualize)

        return pd.DataFrame({"annualized": annualized, "trimonthly": daily})    

    rates = get_risk_free_rate()
    return float(rates["trimonthly"].iloc[-1])