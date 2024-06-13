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
 

