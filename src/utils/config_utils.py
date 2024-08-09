from __future__ import annotations

import configparser
import os

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

class EmailConfig:
    def __init__(self, smtp_server, smtp_port, username, password, recipient):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipient = recipient

    def __eq__(self, other):
        if isinstance(other, EmailConfig):          
            return (self.smtp_server == other.smtp_server and
                    self.smtp_port == other.smtp_port and
                    self.username == other.username and
                    self.password == other.password and
                    self.recipient == other.recipient)
        return False

    def __hash__(self):
        return hash((self.smtp_server, self.smtp_port, self.username, self.password, self.recipient))  


def get_absolute_filepath(relative_path)->str:
    current_path = os.getcwd()
    absolute_path = os.path.join(current_path, relative_path)
    print(f"path: {absolute_path}")
    return absolute_path

def read_ticker_config(config_file_path)->list[TickerConfig]:
    """
    Reads configuration from an INI file and converts it into a list of TickerConfig instances.
    
    :param config_file_path: Path to the configuration INI file.
    :return: List of TickerConfig instances.
    """
    # Initialize the configparser
    config = configparser.ConfigParser()

    # Read the configuration from the INI file
    config.read(config_file_path)

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

def find_ticker_config(ticker_configs, target_ticker):
    for config in ticker_configs:
        if config.ticker == target_ticker:
            return config
    return None

def read_bitvavo_config(config_file_path)->BitvavoConfig:
    """
    Reads configuration from an INI file and converts it into a list of BitvavoConfig instance.
    
    :param config_file_path: Path to the configuration INI file.
    :return: BitvavoConfig instance.
    """
    # Initialize the configparser
    config = configparser.ConfigParser()

    # Resolve the absolute filepath
    config_file_path = get_absolute_filepath(config_file_path)    

    # Read the configuration from the INI file
    config.read(config_file_path)

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

def read_email_config(config_file_path)->EmailConfig:
    """
    Reads configuration from an INI file and converts it into a list of EmailConfig instance.
    
    :param config_file_path: Path to the configuration INI file.
    :return: EmailConfig instance.
    """
    # Initialize the configparser
    config = configparser.ConfigParser()

    # Resolve the absolute filepath
    config_file_path = get_absolute_filepath(config_file_path)

    # Read the configuration from the INI file
    config.read(config_file_path)

    # Read the BitvavoSettings section
    settings = config["EmailSettings"]

    email_config = EmailConfig(
        smtp_server=settings['smtp_server'],
        smtp_port = settings['smtp_port'],
        username = settings['username'],
        password = settings['password'],
        recipient = settings['recipient'],
    )
  
    return email_config