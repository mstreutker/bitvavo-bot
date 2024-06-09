import pytest
import pandas as pd
from io import StringIO
import configparser
from src.utils.config_utils import read_config_to_dataframe

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
    
    # Mock the file read operation
    df = read_config_to_dataframe(config_file_path)
    
    # Expected DataFrame
    expected_data = {
        'buy_margin': [6, 5, 7],
        'sell_margin': [15, 20, 10],
        'currency': ['EUR', 'EUR', 'EUR'],
        'trade': [False, True, True],
        'ticker': ['ADA-EUR', 'BTC-EUR', 'ETH-EUR']
    }
    expected_df = pd.DataFrame(expected_data)

    # Assert that the resulting DataFrame matches the expected DataFrame
    pd.testing.assert_frame_equal(df, expected_df)
