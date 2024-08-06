import pytest
from src.utils.bitvavo_utils import BitvavoClient
from src.utils.config_utils import get_absolute_filepath, TickerConfig
import json
from unittest.mock import  patch
import pandas as pd
import numpy as np
from decimal import Decimal, getcontext
from pandas.testing import assert_frame_equal
from datetime import date

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
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_trades_test.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    mock_bitvavo.trades.return_value = data

    ticker = 'BTC-EUR'
    trades_json, trades_df = bitvavo_client.get_trades(ticker)
    trades_calc_df, latest_trade_df = bitvavo_client.calc_trades(trades_df)
    
    result_df = latest_trade_df[['_timestamp','amount','camount', 'price', 'fee', 'cfee','operator','total','ctotal','price_per_piece','number_of_buys','buy_cooldown']]

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
         'number_of_buys' : '2',
         'buy_cooldown': 0,
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
        "price_per_piece": "float64",
        "number_of_buys": "int64",
        "buy_cooldown": "int64"
    }

    expected_data = pd.DataFrame(expected_json).astype(schema)

    assert_frame_equal (result_df, expected_data)



def test_calc_trades_cooldown(mock_bitvavo, bitvavo_client):
    file_path = get_absolute_filepath(r'tests\utils\resources\test_bitvavo_trades.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    mock_bitvavo.trades.return_value = data

    ticker = 'BTC-EUR'
    trades_json, trades_df = bitvavo_client.get_trades(ticker)
    trades_calc_df, latest_trade_df = bitvavo_client.calc_trades(trades_df)
    
    result_df = latest_trade_df[['_timestamp','operator','number_of_buys','buy_cooldown']]

    expected_json = [
        {'_timestamp': '2024-06-16 09:09:25.590000', 
         'operator': '1',
         'number_of_buys' : '5',
         'buy_cooldown': 1,
         }
    ]

    schema = {
        "_timestamp": "datetime64[ns]",
        "operator": "int64",
        "number_of_buys": "int64",
        "buy_cooldown": "int64"
    }

    expected_data = pd.DataFrame(expected_json).astype(schema)

    assert_frame_equal (result_df, expected_data)

def test_calc_margin():
    bitvavo_client = BitvavoClient()
    
    # Test for positive margin
    price_per_piece = Decimal('10.00')
    ticker_price = Decimal('12.00')
    expected_margin = Decimal('20')
    margin = bitvavo_client.calc_margin(price_per_piece, ticker_price)

    assert margin == expected_margin

    # Test for negative margin
    price_per_piece = Decimal('10.4321')
    ticker_price = Decimal('9.1111')
    expected_margin = Decimal('-12.663')
    margin = bitvavo_client.calc_margin(price_per_piece, ticker_price)

    assert margin == expected_margin

    # Test for zero margin
    price_per_piece = Decimal('10.4321')
    ticker_price = Decimal('10.4321')
    expected_margin = Decimal('0')
    margin = bitvavo_client.calc_margin(price_per_piece, ticker_price)

    assert margin == expected_margin

def test_calc_proposed_action_buy():
    bitvavo_client = BitvavoClient()
    ticker_config = TickerConfig("test",10,20,"EUR",True)

    # Margin > buy_margin : buy
    margin = Decimal('-15')
    expected_action = 'buy'
    action = bitvavo_client.calc_proposed_action(margin, ticker_config)

    assert action == expected_action
    # Margin = buy_margin : buy
    margin = Decimal('-10')
    expected_action = 'buy'
    action = bitvavo_client.calc_proposed_action(margin, ticker_config)

    assert action == expected_action

    # Margin < buy_margin : hold
    margin = Decimal('5')
    expected_action = 'hold'
    action = bitvavo_client.calc_proposed_action(margin, ticker_config)

    assert action == expected_action

def test_calc_proposed_action_sell():
    bitvavo_client = BitvavoClient()
    ticker_config = TickerConfig("test",10,20,"EUR",True)

    # Margin > sell_margin : sell
    margin = Decimal('25')
    expected_action = 'sell'
    action = bitvavo_client.calc_proposed_action(margin, ticker_config)

    assert action == expected_action
    # Margin = sell_margin : sell
    margin = Decimal('20')
    expected_action = 'sell'
    action = bitvavo_client.calc_proposed_action(margin, ticker_config)

    assert action == expected_action

    # Margin < sell_margin : hold
    margin = Decimal('5')
    expected_action = 'hold'
    action = bitvavo_client.calc_proposed_action(margin, ticker_config)

    assert action == expected_action   

def test_calc_trades_cooldown():
    bitvavo_client = BitvavoClient()

    # Current_date > cooldown: no wait
    cooldown = 2
    last_trade_date = date(2024, 1, 1)
    current_date = date(2024, 1, 4)
    expected_wait = False

    wait = bitvavo_client.wait_for_cooldown(cooldown, last_trade_date, current_date)
                                            
    assert wait == expected_wait

    # Current_date = cooldown : no wait
    cooldown = 2
    last_trade_date = date(2024, 1, 1)
    current_date = date(2024, 1, 3)
    expected_wait = False

    wait = bitvavo_client.wait_for_cooldown(cooldown, last_trade_date, current_date)
                                            
    assert wait == expected_wait

    # Current_date < cooldown : wait
    cooldown = 2
    last_trade_date = date(2024, 1, 1)
    current_date = date(2024, 1, 2)
    expected_wait = True

    wait = bitvavo_client.wait_for_cooldown(cooldown, last_trade_date, current_date)
                                            
    assert wait == expected_wait