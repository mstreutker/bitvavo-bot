import pytest
from src.utils.bitvavo_utils import BitvavoClient
from src.utils.config_utils import get_absolute_filepath
import json
from unittest.mock import  patch
import pandas as pd

@pytest.fixture
def mock_bitvavo():
    with patch('src.utils.bitvavo_utils.Bitvavo') as MockBitvavo:
        instance = MockBitvavo.return_value
        yield instance

@pytest.fixture
def bitvavo_client(mock_bitvavo):
    return BitvavoClient()

def test_get_balance(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_balance.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    mock_bitvavo.balance.return_value = data

    # Test for EUR balance
    ticker = 'EUR'
    expected_balance = '502.27'
    balance = bitvavo_client.get_balance(ticker)
    assert balance == expected_balance

    # Test for BTC balance
    ticker = 'BTC'
    expected_balance = '0.00123456'
    balance = bitvavo_client.get_balance(ticker)
    assert balance == expected_balance

    # Test for a ticker that doesn't exist
    ticker = 'ETH'
    expected_balance = None
    balance = bitvavo_client.get_balance(ticker)
    assert balance == expected_balance    
 
def test_get_ticker_price(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_tickerprice.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    mock_bitvavo.tickerPrice.return_value = data

    # Test for BTC-EUR price
    ticker = 'BTC-EUR'
    expected_price = 62524.0
    price = bitvavo_client.get_ticker_price(ticker)
    assert price == expected_price

def test_get_market_moq_float(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_market.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Find the dictionary where 'market' is 'BTC-EUR'
    btc_eur_market = None
    for item in data:
        if item['market'] == 'BTC-EUR':
            btc_eur_market = item
            break

    mock_bitvavo.markets.return_value = btc_eur_market

    # Test for BTC-EUR
    ticker = 'BTC-EUR'
    expected_moq = 0.0001
    market_df, moq = bitvavo_client.get_market(ticker)
    assert moq == expected_moq

def test_get_market_moq_int(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_market.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Find the dictionary where 'market' is 'XYO-EUR'
    xyo_eur_market = None
    for item in data:
        if item['market'] == 'XYO-EUR':
            xyo_eur_market = item
            break

    mock_bitvavo.markets.return_value = xyo_eur_market

    # Test for XYO-EUR
    ticker = 'XYO-EUR'
    expected_moq = 600
    market_df, moq = bitvavo_client.get_market(ticker)
    assert moq == expected_moq

def test_get_trades(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_trades_test.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    mock_bitvavo.trades.return_value = data

    ticker = 'BTC-EUR'
    trades_json, trades_df = bitvavo_client.get_trades(ticker)
    
    #trades_df["ticker"]="ticker"
    trades_df = trades_df.sort_values(by='timestamp')
    trades_df = trades_df.reset_index(drop=True)

    trades_df[['amount', 'price', 'fee']] = trades_df[['amount', 'price', 'fee']].astype(float)
    trades_df["operator"] = trades_df.apply(lambda x: (1 if x['side'] == 'buy' else -1), axis=1)
    trades_df['amount'] = trades_df['amount'] * trades_df["operator"]

    trades_df["_timestamp"] = pd.to_datetime(trades_df['timestamp'], unit='ms')
    trades_df["total"] = (trades_df["amount"] * trades_df["price"]) + trades_df["fee"]

    price_per_piece = 0
    camount = 0
    ctotal = 0
    cfee = 0

    # iterate over the rows using vectorized operations
    for i in range(len(trades_df)):
        row = trades_df.iloc[i]
        if i == 0:
            camount = row["amount"]
            ctotal = row["total"] 
            cfee = row["fee"]
            price_per_piece = (ctotal) / camount
        else:
            if row['side'] == 'buy':
                #price_per_piece = ((row['value'] + row['fee']) + (previous_price_per_piece * previous_cum_amount)) / cum_amount.iloc[i]
                camount += row["amount"]
                ctotal += row["total"]
                cfee += row["fee"]
                price_per_piece = (ctotal) / camount
            else:
                #price_per_piece = previous_price_per_piece + (row['fee'] / cum_amount.iloc[i])
                camount += row["amount"]
                cfee += row["fee"]
                price_per_piece += (row["fee"] / camount)
                ctotal = camount * price_per_piece

        trades_df.at[i, 'price_per_piece'] = price_per_piece
        trades_df.at[i, 'camount'] = camount
        trades_df.at[i, 'cfee'] = cfee
        trades_df.at[i, 'ctotal'] = ctotal
        # previous_cum_amount = cum_amount.iloc[i]
        # previous_price_per_piece = price_per_piece




    # trades_agg = trades_df.groupby(['ticker','side'])[["total","amount", "fee"]].sum()
    # trades_agg["ppp"] = trades_agg["total"] / trades_agg["amount"] 

    # trades_total = trades_agg.groupby(['ticker'])[["total","amount"]].sum()
    # trades_total["ppp"] = trades_total["total"] / trades_total["amount"] 
#df_all = df_all.sort_values(by='timestamp')

    # Set pandas option to display all columns
    pd.set_option('display.max_columns', None)
    # Set pandas option to increase the display width
    pd.set_option('display.width', 1000)

    print(trades_df[['_timestamp','amount','camount', 'price', 'fee', 'cfee','operator','total','ctotal','price_per_piece']])
    # print (trades_agg)
    # print (trades_total)

    assert False