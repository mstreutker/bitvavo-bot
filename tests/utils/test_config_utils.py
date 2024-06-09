import pytest
import pandas as pd
from io import StringIO
import configparser
from src.utils.config_utils import read_ticker_config, TickerConfig

@pytest.fixture
def config_data():
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

    [ETH-EUR]
    buy_margin = 7
    sell_margin = 10
    currency = EUR
    trade = True
    """

def test_read_config_to_dataframe(config_data):
    # Write the configuration data to a temporary file-like object
    config_file_path = StringIO(config_data)
    
    configs = read_ticker_config(config_file_path)
    
    # Expected list of TickerConfig instances
    expected_configs = [
        TickerConfig(ticker='ADA-EUR', buy_margin=6, sell_margin=15, currency='EUR', trade=False),
        TickerConfig(ticker='BTC-EUR', buy_margin=5, sell_margin=20, currency='EUR', trade=True),
        TickerConfig(ticker='ETH-EUR', buy_margin=7, sell_margin=10, currency='EUR', trade=True)
    ]
    
    # Assert that the resulting list of TickerConfig instances matches the expected list
    assert configs == expected_configs
