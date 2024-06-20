from __future__ import annotations

from python_bitvavo_api.bitvavo import Bitvavo
from src.utils.config_utils import read_bitvavo_config, TickerConfig
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
        # Retrieve historical trades for ticker
        trades_json = self.bitvavo.trades(ticker, {})
        trades_df = pd.DataFrame(trades_json)
      
        return trades_json, trades_df
        

    def calc_trades(self, trades_df: pd.DataFrame):
        # Sort trades ascending (oldest first)
        trades_df = trades_df.sort_values(by='timestamp')
        trades_df = trades_df.reset_index(drop=True)

        # Apply basic formatting to support calculations
        trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].astype(float)
        trades_df["operator"] = trades_df.apply(lambda x: (1 if x['side'] == 'buy' else -1), axis=1)
        trades_df['amount'] = trades_df['amount'] * trades_df["operator"]
        trades_df["_timestamp"] = pd.to_datetime(trades_df['timestamp'], unit='ms')
        trades_df["total"] = (trades_df["amount"] * trades_df["price"]) + trades_df["fee"]

        # Initialize calculated attributes
        price_per_piece = 0
        camount = 0
        ctotal = 0
        cfee = 0

        # Iterate over the rows using vectorized operations
        for i in range(len(trades_df)):
            row = trades_df.iloc[i]
            if i == 0:
                # First trade initializes the cumulative measures
                camount = row["amount"]
                ctotal = row["total"] 
                cfee = row["fee"]
                price_per_piece = (ctotal) / camount
            else:
                if row['side'] == 'buy':
                    # If trade is buy, increase the cumulative measures and recalc price_per_piece
                    camount += row["amount"]
                    ctotal += row["total"]
                    cfee += row["fee"]
                    price_per_piece = (ctotal) / camount
                else:
                    # If trade is sell, keep using the previous price_per_piece + fee
                    # to avoid lowering the price_per_piece for sold pieces.
                    # Otherwise, a high sell will cannibalize the price_per_piece.
                    camount += row["amount"]
                    cfee += row["fee"]
                    price_per_piece += (row["fee"] / camount)
                    ctotal = camount * price_per_piece

            # Add the calculated measures to the dataframe
            trades_df.at[i, 'price_per_piece'] = price_per_piece
            trades_df.at[i, 'camount'] = camount
            trades_df.at[i, 'cfee'] = cfee
            trades_df.at[i, 'ctotal'] = ctotal

        # select the latest, most recent trade
        latest_trade_df = trades_df.tail(1).reset_index(drop=True)

        return trades_df, latest_trade_df
    
    def calc_action (price_per_piece: float, ticker_price: float, ticker_config: TickerConfig):
        margin = ((ticker_price / price_per_piece)-1)*100
        return margin