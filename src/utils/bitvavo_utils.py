from __future__ import annotations

from python_bitvavo_api.bitvavo import Bitvavo
from src.utils.config_utils import read_bitvavo_config
from src.utils.references import BITVAVO_CONFIG
import pandas as pd

class BitvavoClient:
    def __init__ (self):
        config = read_bitvavo_config(BITVAVO_CONFIG)

        apikey = config.apikey
        apisecret = config.apisecret
        resturl = config.resturl
        wsurl = config.wsurl
        accesswindow = config.accesswindow
        debugging = config.debugging

        self.bitvavo = Bitvavo({
            'APIKEY': apikey,
            'APISECRET': apisecret,
            'RESTURL': resturl,
            'WSURL': wsurl,
            'ACCESSWINDOW': accesswindow,
            'DEBUGGING': debugging
        })
    
    def get_balance (self, ticker):
        """Return the balance for the ticker."""
        response = self.bitvavo.balance({})

        available = None
        for item in response:
            if item['symbol'] == ticker:
                available = item['available']
                break

        return available
    
    def get_ticker_price (self, ticker):
        """Return the current price for ticker."""
        ticker_price = self.bitvavo.tickerPrice({'market':ticker})
        return float(ticker_price['price'])
    
    def get_market(self, ticker):
        response = self.bitvavo.markets({'market':ticker})

        # Get the market specific settings
        market_df = pd.DataFrame(response)
        market_df = market_df[market_df["orderTypes"]=="market"]
        
        # Get the minimal order quantity.
        minimal_order_qty = market_df["minOrderInBaseAsset"].item()
        
        # Minimal order quantity needs to be float or int (matching market settings), 
        # otherwise API calls for order or sell will fail with 309 error
        if minimal_order_qty.isdigit():
            minimal_order_qty = int(minimal_order_qty)
        else:
            minimal_order_qty = float(minimal_order_qty)

        return market_df, minimal_order_qty

    def get_trades(self, ticker):
        trades_json = self.bitvavo.trades(ticker, {})
        trades_df = pd.DataFrame(trades_json)

        return trades_json, trades_df