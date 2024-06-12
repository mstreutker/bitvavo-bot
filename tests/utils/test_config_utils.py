import pytest
from io import StringIO
from src.utils.config_utils import read_ticker_config, TickerConfig, read_bitvavo_config, BitvavoConfig, read_email_config, EmailConfig

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

@pytest.fixture
def email_config_data():
    # INI configuration data
    return """
    [EmailSettings]
    smtp_server = smtp.gmail.com
    smtp_port = 587 
    username = test@test.com
    password = 123ABC 
    recipient = target@test.com
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

def test_read_email_config(email_config_data):
    # Write the configuration data to a temporary file-like object
    config_file_path = StringIO(email_config_data)
    
    config = read_email_config(config_file_path)
    
    # Expected a EmailConfig instance
    expected_config = EmailConfig(smtp_server='smtp.gmail.com', smtp_port='587', username='test@test.com', password='123ABC', recipient='target@test.com')  
    
    # Assert that the EmailConfig instances matches the expected data
    assert config == expected_config