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


def read_ticker_config(config_file_path):
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