from ast import Raise
from python_bitvavo_api.bitvavo import Bitvavo
import pandas as pd
import confighelper
import datetime
import json
import os
from datetime import datetime
import numpy as np

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
        # # load the trades, reverse the order for easier cumulative rollup
        # trades_df = pd.DataFrame(response).iloc[::-1]
        # # put the appropriate columns to numeric
        # trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].apply(pd.to_numeric)

        # trades_df['value'] = trades_df.apply (
        # lambda row: self.calc_value(row["amount"],row["price"]),
        # axis=1
        # )
        # trades_df['side_factor'] = trades_df.apply (
        # lambda row: self.calc_side_factor(row["side"]),
        # axis=1
        # )


        # #print(response)
        # #trades["paid"] = trades["amount"] * trades["price"]
        # #trades["value"]=0
        # #idx_value = trades.columns.get_loc("value")
        # trades_iterrows = []
        # price_per_piece_iterrows = []
        # cum_amount = 0
        # previous_price_per_piece = 0
        # previous_cum_amount = 0
        # for index, row in trades_df.iterrows():
        #     cum_amount += row["amount"] * row["side_factor"]
            
        #     # Alternative logic for the first row
        #     if index == len(trades_df.index) -1:
        #         price_per_piece = (row['value'] + row['fee']) / cum_amount 
        #     else:
        #         if row['side'] == 'buy':
        #             price_per_piece = ( (row['value'] + row['fee'])+ (previous_price_per_piece * previous_cum_amount)) / cum_amount
        #         else: #price_per_piece = float(previous_row['amount'])
        #             price_per_piece = previous_price_per_piece + (row['fee'] / cum_amount)

        #     previous_cum_amount = cum_amount
        #     previous_price_per_piece = price_per_piece
        #     trades_iterrows.append(float(cum_amount))
        #     price_per_piece_iterrows.append(price_per_piece)
        #     #trades.iloc[index]['value'] = 10#float(row["amount"]) * float(row["price"])
        #     #trades.iloc[index, idx_value]=float(row["amount"]) * float(row["price"])


        # #  print(index)
        # #trades.iloc[0]["value"] =10
        # trades_df['cum_amount'] = trades_iterrows
        # trades_df['price_per_piece'] = price_per_piece_iterrows

        return response
    
    # def calc_trades(self, data):
  
    #     # load the trades, reverse the order for easier cumulative rollup
    #     #trades_df = pd.DataFrame(data).iloc[::-1]
    #     trades_df = data
    #     # put the appropriate columns to numeric
    #     trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].apply(pd.to_numeric)

    #     trades_df['value'] = trades_df.apply (
    #     lambda row: self.calc_value(row["amount"],row["price"]),
    #     axis=1
    #     )
    #     trades_df['side_factor'] = trades_df.apply (
    #     lambda row: self.calc_side_factor(row["side"]),
    #     axis=1
    #     )

    #     trades_iterrows = []
    #     price_per_piece_iterrows = []
    #     cum_amount = 0
    #     previous_price_per_piece = 0
    #     previous_cum_amount = 0
    #     for index, row in trades_df.iterrows():
    #         cum_amount += row["amount"] * row["side_factor"]
            
    #         # Alternative logic for the first row
    #         if index == len(trades_df.index) -1:
    #             price_per_piece = (row['value'] + row['fee']) / cum_amount 
    #         else:
    #             if row['side'] == 'buy':
    #                 price_per_piece = ( (row['value'] + row['fee'])+ (previous_price_per_piece * previous_cum_amount)) / cum_amount
    #             else: #price_per_piece = float(previous_row['amount'])
    #                 price_per_piece = previous_price_per_piece + (row['fee'] / cum_amount)

    #         previous_cum_amount = cum_amount
    #         previous_price_per_piece = price_per_piece
    #         trades_iterrows.append(float(cum_amount))
    #         price_per_piece_iterrows.append(price_per_piece)
 
    #     trades_df['cum_amount'] = trades_iterrows
    #     trades_df['price_per_piece'] = price_per_piece_iterrows

    #     return trades_df   

    def calc_trades(self, data):
        trades_df = data
        trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].astype(float)

        trades_df['value'] = self.calc_value(trades_df['amount'], trades_df['price'])
        trades_df['side_factor'] = trades_df.apply(lambda x: (1 if x['side'] == 'buy' else -1), axis=1)

        cum_amount = trades_df['amount'] * trades_df['side_factor']
        cum_amount = cum_amount.cumsum()

        previous_price_per_piece = 0
        previous_cum_amount = 0
        trades_df['cum_amount'] = cum_amount
        trades_df['price_per_piece'] = np.nan

        # iterate over the rows using vectorized operations
        for i in range(len(trades_df)):
            row = trades_df.iloc[i]
            if i == 0:
                price_per_piece = (row['value'] + row['fee']) / cum_amount.iloc[i]
            else:
                if row['side'] == 'buy':
                    price_per_piece = ((row['value'] + row['fee']) + (previous_price_per_piece * previous_cum_amount)) / cum_amount.iloc[i]
                else:
                    price_per_piece = previous_price_per_piece + (row['fee'] / cum_amount.iloc[i])

            trades_df.at[i, 'price_per_piece'] = price_per_piece
            previous_cum_amount = cum_amount.iloc[i]
            previous_price_per_piece = price_per_piece

        return trades_df

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
    
    def save_trades_json(self, data, output_dir):
        # Group the data by month
        groups = {}
        for item in data:    
            timestamp = datetime.fromtimestamp(item['timestamp']/1000)
            month = timestamp.strftime('%Y-%m')
            if month not in groups:
                groups[month] = []
            groups[month].append(item)

        # Create the output directory if it doesn't already exist
        if not os.path.exists(f'{output_dir}'):
            os.makedirs(f'{output_dir}')

        # Check if the file for the most recent month already exists
        existing_files = os.listdir(output_dir)
        existing_files_sorted = sorted(existing_files, key=lambda x: x.split('.')[0], reverse=True)
        if existing_files_sorted:
            latest_filename = existing_files_sorted[0]
            latest_month = latest_filename.replace('.json', '')
        
        # Write each group to a separate file
        for month, items in groups.items():
            if not existing_files or month >= latest_month:
                print(f'Writing {output_dir}/{month}')
                filename = f'{output_dir}/{month}.json'
                with open(filename, 'w') as f:
                    json.dump(items, f)
            else:
                print(f'Skipping {output_dir}/{month} (file is up-to-date)')

    def get_df_from_trades_json(self, output_dir):
        # Get a list of all the filenames in the output directory
        filenames = os.listdir(output_dir)

        # Initialize an empty list to store the DataFrames
        dfs = []

        # Loop over the filenames and read each file into a DataFrame
        for filename in filenames:
            filepath = os.path.join(output_dir, filename)
            df = pd.read_json(filepath, precise_float=True)
            dfs.append(df)

        # Concatenate all of the DataFrames into a single one
        df_all = pd.concat(dfs, ignore_index=True)

        # Sort the resulting DataFrame on the timestamp in ascending order
        df_all = df_all.sort_values(by='timestamp')
        df_all = df_all.reset_index(drop=True)

        return df_all
    
    # def perform_trades (self, trades_df, currency):
    #     trades_buy = trades_df[trades_df['action']=="buy"]
    #     trades_sell = trades_df[trades_df['action']=="sell"]

    #     for index, row in trades_buy.iterrows():
    #         # get actual balance for the configured currency
    #         balance_EUR = self.get_balance(currency)
    #         response = self.buy_order(row["ticker"], row["order_pcs"])