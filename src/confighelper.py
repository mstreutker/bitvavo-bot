import configparser

# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read('.\local.config.ini')
    return config
class config:
    def __init__(self, config_file):
        cfg = configparser.ConfigParser()
        cfg.read(config_file)

        # get the currency of the balance account
        self.currency = cfg['TradeSettings']['currency'] 

        # market price needs to be x% below
        self.buy_margin = cfg.getfloat('TradeSettings','buy_margin')

        # market price needs to be x% above
        self.sell_margin = cfg.getfloat('TradeSettings','sell_margin')

        # trade = True will trade currencies, False will only log the current state
        self.trade = cfg.getboolean('TradeSettings','trade')

        # check if the logging should be verbose
        self.verbose = cfg.getboolean('TradeSettings','verbose')

        # get the list of currencies that need to be monitored
        self.ticker_list = (cfg['TradeSettings']['tickerlist']).split(',')