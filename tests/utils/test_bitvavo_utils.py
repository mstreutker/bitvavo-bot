import pytest
from src.utils.bitvavo_utils import BitvavoClient
from src.utils.config_utils import get_absolute_filepath
import json
from unittest.mock import  patch

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