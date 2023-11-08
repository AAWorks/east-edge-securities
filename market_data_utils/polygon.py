import requests, time, random
from yahoo_fin import options

class Polygon:
    _headers: dict
    _base_url: str

    def __init__(self, key=None, yf_backup=False, debugging=False):
        if key is None:
            with open('keys/polygon.txt', 'r') as keyfile:
                key = keyfile.readline().strip()

        self._headers = {
            'Authorization': f'Bearer {key}'
        }

        self._base_url = 'https://api.polygon.io/'
        self._yf_backup = yf_backup
        self._debugging = debugging

    def _get_req_url(self, extension: str = ""):
        return self._base_url + extension

    def _query(self, query: str):
        full_query = self._get_req_url(query)
        return requests.request("GET", url=full_query, headers=self._headers)
    
    def _get_close_price_from_poly(self, ticker):
        query = f"v2/aggs/ticker/{ticker}/prev?adjusted=true"
        previous_day_details = self._query(query).json()
        price_results = previous_day_details["results"][0]
        
        if "vw" in price_results:
            return price_results["vw"] #volume weighted avg
        else:
            return price_results["c"] # close

    def last_ticker_prices(self):
        price_dict, tickers = {}, self.nasdaq_tickers
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker).history()
                current_price = stock['Close'].iloc[-1]
            except:
                if self._debugging:
                    with open("data/error_log.txt", "a") as f:
                        f.write(f"<error> Ticker: {ticker}")

                current_price = float(self._get_close_price_from_poly(ticker))
            
            price_dict[ticker] = current_price
                
        return price_dict

    @property
    def base_url(self):
        return self._base_url
    
    def _options_query(self, query: str):
        time.sleep(12)
        return self._query(f"v3/reference/options/contracts?{query}")

    def _polygon_options(self, ticker, position="", expired=""):
        if position:
            position = f"&contract_type={position}"
        
        if expired != "":
            expired = f"&expired={str(expired).lower()}"
        
        query = f"underlying_ticker={ticker}{position}{expired}&limit=1000"
        return self._options_query(query)
    
    def _poly_ticker_contracts(self, ticker, expiration):
        json_data = self._polygon_options(ticker).json()
        ticker_data = pd.DataFrame(json_data["results"])
        prices = self._get_eod_stock_prices(self.nasdaq_tickers)
        ticker_data["mark"] = prices[ticker]
        ticker_data["price"] = prices[ticker]
    
    def _yf_ticker_contracts(self, ticker, expiration):
        random.seed(31337)
        np.random.seed(31337)

        expiration = expiration.strftime("%m/%d/%Y")
        try:
            chain = options.get_options_chain(ticker, expiration)
        except ValueError:
            return None

        calls = pd.DataFrame(chain["calls"])
        puts = pd.DataFrame(chain["puts"])
        calls["Type"] = "C"
        puts["Type"] = "P"

        ticker_data = pd.concat([calls, puts]).sort_index(kind='merge')
        ticker_data.reset_index(inplace=True, drop=True)
        
        ticker_data["Contract ID"] = np.random.randint(low=100, high=999, size=len(ticker_data))
        ticker_data["Bid"] = ticker_data["Bid"].apply(pd.to_numeric, errors='coerce')
        ticker_data["Mark"] = ticker_data[["Bid", "Ask"]].mean(axis=1)
        
        #ticker_data["Dividend Yield"] = ticker_data["x"] - ticker_data["Mark"]

        return ticker_data

    def _get_eod_options_data(self, tickers):
        all_ticker_options_data = []
        for ticker in tickers:
            json_data = self._polygon_options(ticker).json()
            ticker_data = pd.DataFrame(json_data["results"])
            all_ticker_options_data.append(ticker_data)
        
        return pd.concat(all_ticker_options_data).sort_index(kind='merge')
    
    def _get_eod_stock_prices(self, tickers):
        ticker_prices = {}
        for ticker in tickers:
            query = f"v2/aggs/ticker/{ticker}/prev?adjusted=true"
            previous_day_details = self._query(query).json()
            price_results = previous_day_details["results"][0]
            
            if "vw" in price_results:
                ticker_prices[ticker] = price_results["vw"] #volume weighted avg
            else:
                ticker_prices[ticker] = price_results["c"] # close
        
        return ticker_prices

    def exchange_status(self, exchange): # i.e. nasdaq -> open, closed, after-hours
        query = "v1/marketstatus/now?"
        market_details = self._query(query).json()
        return market_details["exchanges"][exchange] 

    def expiration_dates(self, ticker):
        return options.get_expiration_dates(ticker.lower())[1:]