import streamlit as st
st.set_page_config(layout="wide", page_title="BDF | Portfolio Tracker", page_icon=":infinity:")

from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import yfinance as yf

from market_data_utils.basics import StaticNasdaq
from portfolio import Portfolio_CSV

@st.cache_data()
def pull_static_data():
    return StaticNasdaq()

st.title(':infinity: Big Data Fund Portfolio Tracker')
st.caption("Portfolio & Performance Tracker for the Big Data Fund :registered: | Last Updated 09.2023")

nasdaq = pull_static_data()
capital = st.number_input("Starting AUM", min_value=0)

st.info("Should have the following columns: trade_type (buy/sell), ticker, size, share_price, date")
portfolio_file = st.file_uploader("Portfolio", type="csv")

if portfolio_file:
    portfolio = Portfolio_CSV(portfolio_file)
    st.dataframe(portfolio.get_df())
