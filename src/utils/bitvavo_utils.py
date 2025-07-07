from __future__ import annotations

from python_bitvavo_api.bitvavo import Bitvavo
from src.utils.config_utils import read_bitvavo_config, TickerConfig
from src.utils.references import BITVAVO_CONFIG
import pandas as pd
import numpy as np
from decimal import Decimal, getcontext
from datetime import date

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
        
    def createPostfix(self, options):
        params = []
        for key in options:
            params.append(key + '=' + str(options[key]))
        postfix = '&'.join(params)
        if(len(options) > 0):
            postfix = '?' + postfix
        return postfix

    def get_balances(self):
        response = self.bitvavo.balance({})
        return pd.DataFrame(response)

    def get_balance (self, ticker):
        """Return the balance for the ticker."""
        response = self.bitvavo.balance({})

        available = None
        for item in response:
            if item['symbol'] == ticker:
                available = item['available']
                break
        if available is not None:        
            return Decimal(available)
        else:
            return None
    
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


    def getTradeHistoryPage(self, page):
        options = {}
        body = {}
        #options['type'] = 'buy'
        options['page']=page
        options['fromDate']=0
        postfix = self.createPostfix(options)
        #hist = bitvavo.privateRequest('/orders', postfix, {}, 'GET')
        hist = self.bitvavo.privateRequest('/account/history/', postfix, body, 'GET')
        return hist

    def getTradeHistory(self):

        # ticker = ticker.removesuffix('-EUR')

        all_data = []
        current_page = 1
        total_pages = 1


        while current_page <= total_pages:
            data = self.getTradeHistoryPage(page=current_page)
            total_pages = data['totalPages']  # Update totalPages from API response
            current_page = data['currentPage']  # Update currentPage from API response
            print (f"total pages: {total_pages}")
            print (f"total pages: {current_page}")
            current_page+=1
            all_data.extend(data['items'])

        items_df = pd.json_normalize(all_data)

        items_df['amount'] = items_df.apply(
            lambda row: row['receivedAmount'] if row['type'] == 'buy' else row['sentAmount'],
            axis=1
        )

        items_df = items_df.rename(columns={
            'priceAmount': 'price',
            'feesAmount': 'fee',
            'type': 'side'
        })

        # Ensure 'executedAt' is in datetime format
        items_df['executedAt'] = pd.to_datetime(items_df['executedAt'])

        # Convert 'executedAt' to Unix timestamp in milliseconds
        items_df['timestamp'] = (items_df['executedAt'].astype('int64') // 10**6)


        # filtered_df = items_df[
        #     ((items_df['sentCurrency'] == ticker) | (items_df['receivedCurrency'] == ticker))
        #     & ((items_df['side'] == "buy") | (items_df['side'] == "sell"))
        # ]

        return items_df


    def buy_order(self, ticker, amount):
        #response = self.bitvavo.time()
        response = self.bitvavo.placeOrder(ticker, 'buy', 'market', { 'amount': amount, 'operatorId': 1 })
        return response

    def sell_order(self, ticker, amount):
        response = self.bitvavo.placeOrder(ticker, 'sell', 'market', { 'amount': amount, 'operatorId': 1 })
        return response           

    def calc_trades(self, trades_df: pd.DataFrame):
        # Sort trades ascending (oldest first)
        trades_df = trades_df.sort_values(by='timestamp')
        trades_df = trades_df.reset_index(drop=True)
        # Apply basic formatting to support calculations
        trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].astype(np.float64)
        trades_df["operator"] = trades_df.apply(lambda x: (1 if x['side'] == 'buy' else -1), axis=1) 
        trades_df['amount'] = trades_df['amount'] * trades_df["operator"]     
        trades_df["_timestamp"] = pd.to_datetime(trades_df['timestamp'], unit='ms')     
        trades_df["total"] = (trades_df["amount"] * trades_df["price"]) + trades_df["fee"]
        trades_df["number_of_buys"] = trades_df.apply(lambda x: 0, axis=1).astype(np.int64)
        trades_df["buy_cooldown"] = trades_df.apply(lambda x: 0, axis=1).astype(np.int64)


        # Initialize calculated attributes
        price_per_piece = 0
        camount = 0
        ctotal = 0
        cfee = 0
        number_of_buys = 1

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
                    number_of_buys += 1
                else:
                    # If trade is sell, keep using the previous price_per_piece + fee
                    # to avoid lowering the price_per_piece for sold pieces.
                    # Otherwise, a high sell will cannibalize the price_per_piece.
                    camount += row["amount"]
                    cfee += row["fee"]
                    price_per_piece += (row["fee"] / camount)
                    ctotal = camount * price_per_piece
                    number_of_buys = 0
            
            # Add the calculated measures to the dataframe
            trades_df.at[i, 'price_per_piece'] = price_per_piece
            trades_df.at[i, 'camount'] = camount
            trades_df.at[i, 'cfee'] = cfee
            trades_df.at[i, 'ctotal'] = ctotal
            trades_df.at[i, 'number_of_buys'] = int(number_of_buys)
            trades_df.at[i, 'buy_cooldown'] = int(number_of_buys) // 3

        # select the latest, most recent trade
        latest_trade_df = trades_df.tail(1).reset_index(drop=True)

        return trades_df, latest_trade_df
    
    def calc_margin(self, price_per_piece: Decimal, ticker_price: Decimal)->Decimal:
        margin = ((ticker_price / price_per_piece)-Decimal(1)) * 100
        return round(margin,3)


    def calc_proposed_action (self, margin: Decimal, ticker_config: TickerConfig):
        action = "hold"

        if margin < 0:
            # Ticker price is lower than current price per piece, potential buy
            if abs(margin) >= ticker_config.buy_margin:
                action = "buy"
        elif margin > 0:
            if abs(margin) >= ticker_config.sell_margin:
            # market price is higher than current price per piece, potential sell
            # if balance_pcs > order_pcs:
                action = "sell" 

        return action
    
    def get_remaining_cooldown(self, cooldown: np.int64, last_trade_date: date, current_date: date)->int:

        delta = current_date - last_trade_date
        remaining_cooldown = cooldown - delta.days
        if remaining_cooldown < 0:
            remaining_cooldown = 0
        # One buy per day is permitted. 
        # By default, a buy is permitted on a new day, unless there is a cooldown > 0.
        return remaining_cooldown