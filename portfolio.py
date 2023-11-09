import pandas as pd
import numpy as np
import streamlit as st

from notanorm import SqliteDb

DATA_PATH = "data/"

# All monetary values in cents, action_type is trade, withdrawal, deposit
def _create_portfolio_table(db: SqliteDb) -> None:
    db.query("""CREATE TABLE IF NOT EXISTS big_data_fund (
             action_id INTEGER PRIMARY KEY AUTOINCREMENT,
             action_type TEXT,
             ticker TEXT,
             company TEXT,
             share_price INTEGER,
             total_price INTEGER,
             size INTEGER,
             date TEXT DEFAULT CURRENT_TIMESTAMP,
             deposit_amount INTEGER DEFAULT 0,
             withdrawal_amount INTEGER DEFAULT 0);""")

@st.cache_resource()
def _connect_to_db(name: str) -> SqliteDb:
    db = SqliteDb(DATA_PATH + name)
    _create_portfolio_table(db)
    return db


class Portfolio:
    def __init__(self, name: str, db_file: str = "portfolio.db"):
        self._db: SqliteDb = _connect_to_db(db_file)
        self._name = name

    def _get_dataframe(self, data) -> pd.DataFrame:
        headers_info = self._db.query(f"PRAGMA table_info({self._name});")
        headers = [header.name for header in headers_info]
        return pd.DataFrame.from_records(data = data, columns = headers)

    @property
    def name(self):
        return self._name
    
    def get_portfolio(self) -> pd.DataFrame:
        data = self._db.select(self._name)
        return self._get_dataframe(data)
    
    def get_buys(self) -> pd.DataFrame:
        buys = self._db.select(self._name, action_type="buy")
        return self._get_dataframe(buys)

    def get_sells(self) -> pd.DataFrame:
        sells = self._db.select(self._name, action_type="sell")
        return self._get_dataframe(sells)
    
    def get_trades(self) -> pd.DataFrame:
        buys = self._db.select(self._name, action_type="buy")
        sells = self._db.select(self._name, action_type="sell")
        return self._get_dataframe(buys + sells)
    
    def get_positions(self) -> pd.DataFrame:
        return None

if __name__ == "__main__":
    p = Portfolio("big_data_fund")
    print(p.get_dataframe())
