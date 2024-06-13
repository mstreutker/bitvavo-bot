from __future__ import annotations

from python_bitvavo_api.bitvavo import Bitvavo
from src.utils.config_utils import read_bitvavo_config
from src.utils.references import BITVAVO_CONFIG

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
        print (ticker_price)
        return float(ticker_price['price'])