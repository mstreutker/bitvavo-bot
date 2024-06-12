import pytest
import pandas as pd
from io import StringIO
import configparser
from src.utils.config_utils import read_ticker_config, TickerConfig, BitvavoConfig, read_bitvavo_config

@pytest.fixture
def ticker_config_data():
    # INI configuration data
    return """
    [ADA-EUR]
    buy_margin = 6
    sell_margin = 15
    currency = EUR
    trade = False

    [BTC-EUR]
    buy_margin = 5
    sell_margin = 20
    currency = EUR
    trade = True
    """

@pytest.fixture
def bitvavo_config_data():
    # INI configuration data
    return """
    [BitvavoSettings]
    apikey = 123ABC
    apisecret = 456DEV
    resturl = https://api.bitvavo.com/v2
    wsurl = wss://ws.bitvavo.com/v2/
    accesswindow = 10000
    debugging = False
    """

def test_read_ticker_config(ticker_config_data):
    # Write the configuration data to a temporary file-like object
    config_file_path = StringIO(ticker_config_data)
    
    configs = read_ticker_config(config_file_path)
    
    # Expected list of TickerConfig instances
    expected_configs = [
        TickerConfig(ticker='ADA-EUR', buy_margin=6, sell_margin=15, currency='EUR', trade=False),
        TickerConfig(ticker='BTC-EUR', buy_margin=5, sell_margin=20, currency='EUR', trade=True)
    ]
    
    # Assert that the resulting list of TickerConfig instances matches the expected list
    assert configs == expected_configs

def test_read_bitvavo_config(bitvavo_config_data):
    # Write the configuration data to a temporary file-like object
    config_file_path = StringIO(bitvavo_config_data)
    
    config = read_bitvavo_config(config_file_path)
    
    # Expected a BitvavoConfig instance
    expected_config = BitvavoConfig(apikey='123ABC', apisecret='456DEV', resturl='https://api.bitvavo.com/v2', wsurl='wss://ws.bitvavo.com/v2/', accesswindow='10000', debugging=False)  
    
    # Assert that the BitvavoConfig instances matches the expected data
    assert config == expected_config
