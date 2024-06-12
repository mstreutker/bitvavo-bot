from __future__ import annotations

import configparser
import pandas as pd

class TickerConfig:
    def __init__(self, ticker, buy_margin, sell_margin, currency, trade):
        self.ticker = ticker
        self.buy_margin = buy_margin
        self.sell_margin = sell_margin
        self.currency = currency
        self.trade = trade

    def __repr__(self):
        return (f"TickerConfig(ticker='{self.ticker}', buy_margin={self.buy_margin}, "
                f"sell_margin={self.sell_margin}, currency='{self.currency}', trade={self.trade})")
    
    def __eq__(self, other):
        if isinstance(other, TickerConfig):
            return (self.ticker == other.ticker and
                    self.buy_margin == other.buy_margin and
                    self.sell_margin == other.sell_margin and
                    self.currency == other.currency and
                    self.trade == other.trade)
        return False

    def __hash__(self):
        return hash((self.ticker, self.buy_margin, self.sell_margin, self.currency, self.trade))    


class BitvavoConfig:
    def __init__(self, apikey, apisecret, resturl, wsurl, accesswindow, debugging):
        self.apikey = apikey
        self.apisecret = apisecret
        self.resturl = resturl
        self.wsurl = wsurl
        self.accesswindow = accesswindow
        self.debugging = debugging

    def __eq__(self, other):
        if isinstance(other, BitvavoConfig):          
            return (self.apikey == other.apikey and
                    self.apisecret == other.apisecret and
                    self.resturl == other.resturl and
                    self.wsurl == other.wsurl and
                    self.accesswindow == other.accesswindow and
                    self.debugging == other.debugging)
        return False

    def __hash__(self):
        return hash((self.apikey, self.apisecret, self.resturl, self.wsurl, self.accesswindow, self.debugging))  



def read_ticker_config(config_file_path)->list[TickerConfig]:
    """
    Reads configuration from an INI file and converts it into a list of TickerConfig instances.
    
    :param config_file_path: Path to the configuration INI file.
    :return: List of TickerConfig instances.
    """
    # Initialize the configparser
    config = configparser.ConfigParser()

    # Read the configuration from the INI file
    config.read_file(config_file_path)

    # Transform the INI structure into a list of TickerConfig instances
    configs = []
    for ticker in config.sections():
        settings = config[ticker]
        ticker_config = TickerConfig(
            ticker=ticker,
            buy_margin=int(settings['buy_margin']),
            sell_margin=int(settings['sell_margin']),
            currency=settings['currency'],
            trade=config.getboolean(ticker, 'trade')
        )
        configs.append(ticker_config)
    
    return configs

def read_bitvavo_config(config_file_path)->BitvavoConfig:
    """
    Reads configuration from an INI file and converts it into a list of BitvavoConfig instance.
    
    :param config_file_path: Path to the configuration INI file.
    :return: List of BitvavoConfig instance.
    """
    # Initialize the configparser
    config = configparser.ConfigParser()

    # Read the configuration from the INI file
    config.read_file(config_file_path)

    # Read the BitvavoSettings section
    settings = config["BitvavoSettings"]

    bitvavo_config = BitvavoConfig(
        apikey=settings['apikey'],
        apisecret = settings['apisecret'],
        resturl = settings['resturl'],
        wsurl = settings['wsurl'],
        accesswindow = settings['accesswindow'],
        debugging = config.getboolean('BitvavoSettings','debugging'),
    )
  
    return bitvavo_config