from __future__ import annotations

import configparser
import pandas as pd

# def get_configparser(config_file_path):
#     # Initialize the configparser
#     config = configparser.ConfigParser()

#     # Read the configuration from the INI file
#     config.read_file(config_file_path)

#     return config

def read_config_to_dataframe(config_file_path)-> pd.DataFrame:
    """
    Reads configuration from an INI file and converts it into a pandas DataFrame.
    
    :param config_file_path: Path to the configuration INI file.
    :return: DataFrame containing the configuration data.
    """
    # Initialize the configparser
    config = configparser.ConfigParser()

    # Read the configuration from the INI file
    config.read_file(config_file_path)

    # Transform the INI structure into a list of dictionaries
    data = []
    for ticker in config.sections():
        settings = dict(config.items(ticker))
        settings['ticker'] = ticker
        # Convert appropriate fields to their correct types
        settings['buy_margin'] = int(settings['buy_margin'])
        settings['sell_margin'] = int(settings['sell_margin'])
        settings['trade'] = config.getboolean(ticker, 'trade')
        data.append(settings)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)
    return df