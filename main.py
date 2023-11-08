import streamlit as st
st.set_page_config(layout="wide", page_title="Portfolio Tracker", page_icon=":gear:")

from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import yfinance as yf

from market_data_utils.basics import StaticNasdaq

@st.cache_data()
def pull_static_data():
    return StaticNasdaq()

st.title('Portfolio Tracker :gear:')
st.caption("Big Data Fund | 2023")

st.info("Basic Data-In Model Portfolio Tracker")

nasdaq = pull_static_data()

capital = st.number_input("Total AUM", min_value=0)

inputs, from_csv, coming_soon = st.tabs(["From Inputs", "From CSV/Excel", "Coming Soon"])

with inputs:
    tickers = st.multiselect("Ticker", nasdaq.tickers, "AAPL")
    if capital and tickers:
        submit_a = st.button("Submit", use_container_width=True, key="submit_a")
    else:
        submit_a = st.button("Submit", use_container_width=True, disabled=True, key="submit_a")

    if submit_a:
        portfolio = pd.DataFrame(columns=["Ticker", "Company", "Principal", "Allocation Date", "Current Value", "Percentage of Portfolio"])
        values = []
        for ticker in tickers:
            vals = {"sym": ticker}
            vals["amt"] = st.number_input(f"{ticker} Allocation Amount", min_value=0, key=f"{ticker}_allocation")
            vals["date"] = st.date_input(f"{ticker} Allocation Date", key=f"{ticker}_date")
            values.append(vals)

        submit_b = st.button("Submit", use_container_width=True, key="submit_b")

        if submit_b:
            for vals in values:
                row = {
                    "Ticker": vals["sym"], 
                    "Company": nasdaq.get_company_name(vals["sym"]),
                    "Principal": vals["amt"],
                    "Allocation Date": vals["date"],
                    "Current Value": 0,
                    "Percentage of Portfolio": 0
                }
                portfolio.append(row, ignore_index=True)
            
            st.success("Portfolio Generated")
            st.dataframe(portfolio)
