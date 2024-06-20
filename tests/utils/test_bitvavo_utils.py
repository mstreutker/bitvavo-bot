import pytest
from src.utils.bitvavo_utils import BitvavoClient
from src.utils.config_utils import get_absolute_filepath
import json
from unittest.mock import  patch
import pandas as pd
from pandas.testing import assert_frame_equal

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

def test_calc_trades(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_trades.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    mock_bitvavo.trades.return_value = data

    ticker = 'BTC-EUR'
    trades_json, trades_df = bitvavo_client.get_trades(ticker)
    trades_calc_df, latest_trade_df = bitvavo_client.calc_trades(trades_df)
    
    result_df = latest_trade_df[['_timestamp','amount','camount', 'price', 'fee', 'cfee','operator','total','ctotal','price_per_piece']]

    # # Set pandas option to display all columns
    # pd.set_option('display.max_columns', None)
    # # Set pandas option to increase the display width
    # pd.set_option('display.width', 1000)

    # print(result_df)
    expected_json = [
        {'_timestamp': '2024-06-16 09:09:25.590000', 
         'amount': '5.0', 
         'camount': '17.0',
         'price': '0.6',
         'fee': '0.005',
         'cfee': '0.025',
         'operator': '1',
         'total': '3.005',
         'ctotal': '11.0152',
         'price_per_piece': '0.647953',
         }
    ]

    schema = {
        "_timestamp": "datetime64[ns]",
        "amount": "float64",
        "camount": "float64",
        "price": "float64",
        "fee": "float64",
        "cfee": "float64",
        "operator": "int64",
        "total": "float64",
        "ctotal": "float64",
        "price_per_piece": "float64" 
    }

    expected_data = pd.DataFrame(expected_json).astype(schema)

    assert_frame_equal (result_df, expected_data)
    