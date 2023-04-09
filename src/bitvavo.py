from ast import Raise
from python_bitvavo_api.bitvavo import Bitvavo
import pandas as pd
import confighelper

class bitvavo_client:
    def __init__ (self):
        config = confighelper.read_config()

        apikey = config['BitvavoSettings']['apikey']
        apisecret = config['BitvavoSettings']['apisecret']
        resturl = config['BitvavoSettings']['resturl']
        wsurl = config['BitvavoSettings']['wsurl']
        accesswindow = config['BitvavoSettings']['accesswindow']
        debugging = config.getboolean('BitvavoSettings','debugging')

        self.bitvavo = Bitvavo({
            'APIKEY': apikey,
            'APISECRET': apisecret,
            'RESTURL': resturl,
            'WSURL': wsurl,
            'ACCESSWINDOW': accesswindow,
            'DEBUGGING': debugging
        })
        self.label = "hello"

    def calc_value (self, amount, price):
        value = amount * price
        return value

    def calc_side_factor (self, side):
        if side == "buy":
            return 1
        else:
            return -1        

    def get_trades(self, ticker):
        response = self.bitvavo.trades(ticker, {})
        # load the trades, reverse the order for easier cumulative rollup
        trades_df = pd.DataFrame(response).iloc[::-1]
        # put the appropriate columns to numeric
        trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].apply(pd.to_numeric)

        trades_df['value'] = trades_df.apply (
        lambda row: self.calc_value(row["amount"],row["price"]),
        axis=1
        )
        trades_df['side_factor'] = trades_df.apply (
        lambda row: self.calc_side_factor(row["side"]),
        axis=1
        )


        #print(response)
        #trades["paid"] = trades["amount"] * trades["price"]
        #trades["value"]=0
        #idx_value = trades.columns.get_loc("value")
        trades_iterrows = []
        price_per_piece_iterrows = []
        cum_amount = 0
        previous_price_per_piece = 0
        previous_cum_amount = 0
        for index, row in trades_df.iterrows():
            cum_amount += row["amount"] * row["side_factor"]
            
            # Alternative logic for the first row
            if index == len(trades_df.index) -1:
                price_per_piece = (row['value'] + row['fee']) / cum_amount 
            else:
                if row['side'] == 'buy':
                    price_per_piece = ( (row['value'] + row['fee'])+ (previous_price_per_piece * previous_cum_amount)) / cum_amount
                else: #price_per_piece = float(previous_row['amount'])
                    price_per_piece = previous_price_per_piece + (row['fee'] / cum_amount)

            previous_cum_amount = cum_amount
            previous_price_per_piece = price_per_piece
            trades_iterrows.append(float(cum_amount))
            price_per_piece_iterrows.append(price_per_piece)
            #trades.iloc[index]['value'] = 10#float(row["amount"]) * float(row["price"])
            #trades.iloc[index, idx_value]=float(row["amount"]) * float(row["price"])


        #  print(index)
        #trades.iloc[0]["value"] =10
        trades_df['cum_amount'] = trades_iterrows
        trades_df['price_per_piece'] = price_per_piece_iterrows

        return trades_df, response

    def get_ticker_price (self, ticker):
        """Return the current price for ticker."""
        ticker_price = self.bitvavo.tickerPrice({'market':ticker})
        return float(ticker_price['price'])
    
    def get_balance (self, ticker):
        """Return the balance for the ticker."""
        response = self.bitvavo.balance({})
        balance_df = pd.DataFrame(response)
        balance_df[['available']] = balance_df[['available']].apply(pd.to_numeric)
        balance_ticker = balance_df[balance_df["symbol"]==ticker]['available'].iloc[0]
        return balance_ticker

    def buy_order(self, ticker, amount):
        #response = self.bitvavo.time()
        response = self.bitvavo.placeOrder(ticker, 'buy', 'market', { 'amount': amount})
        return response

    def sell_order(self, ticker, amount):
        response = self.bitvavo.placeOrder(ticker, 'sell', 'market', { 'amount': amount})
        return response        
    
    def get_market(self, ticker):
        market_df = pd.DataFrame()
#        try:
        response = self.bitvavo.markets({'market':ticker})
        if response.get('error') != None:
            raise ValueError (response)
        market_df = pd.DataFrame(response)
 #       except ValueError:
  #          print (response)
   #         raise
        return market_df
    
    def get_minimal_order_quantity(self, market_df):
        """Return the minimal order quantity for the market."""
        moq_ = market_df[market_df["orderTypes"]=="market"]["minOrderInBaseAsset"].iloc[0]

        # Minimal Order Quantity needs to be float or int (matching market settings), 
        # otherwise API call fails with 309 error
        if moq_.isdigit():
            moq = int(moq_)
        else:
            moq = float(moq_)
        
        return moq
   