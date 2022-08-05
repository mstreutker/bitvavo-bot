import bitvavo as bv
import logging
import confighelper
import sys

#
# logging settings
#

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('bitvavo.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

#
# configuration settings
#

#config = confighelper.read_config()
config = confighelper.config('.\local.config.ini')


# get the currency of the balance account
#currency = config['TradeSettings']['currency'] 

# market price needs to be x% below
#buy_margin = config.getfloat('TradeSettings','buy_margin')

# market price needs to be x% above
#sell_margin = config.getfloat('TradeSettings','sell_margin')

# trade = True will trade currencies, False will only log the current state
#trade = config.getboolean('TradeSettings','trade')

# check if the logging should be verbose
#verbose = config.getboolean('TradeSettings','verbose')

# get the list of currencies that need to be monitored
#ticker_list = (config['TradeSettings']['tickerlist']).split(',')

# instantiate a new bitvavo connection
client = bv.bitvavo_client()

overview_dict = {"market":{},"ppp":{}}

for ticker in config.ticker_list:
  print (f"Current ticker : {ticker}")

  # get market details
  market = client.get_market(ticker)
  #print(market.head())
  #moq_ = market[market["orderTypes"]=="market"]["minOrderInBaseAsset"].iloc[0]

  # Minimal Order Quantity needs to be float or int (matching market settings), 
  # otherwise API call fails with 309 error
  #if moq_.isdigit():
  #    moq = int(moq_)
  #else:
  #    moq = float(moq_)
  moq = client.get_minimal_order_quantity(market)
      
  print (f"Minimal Order Quantity : {moq}")

  # get trade history for ticker
  trades_df = client.get_trades (ticker)

  # get actual price for ticker
  ticker_price = client.get_ticker_price(ticker)

  # get actual balance for all currencies
  #balance_df = client.get_balance()
  #print(balance_df)
  #balance_EUR = balance_df[balance_df["symbol"]==currency]['available'].iloc[0]
  balance_EUR = client.get_balance(config.currency)
  print(f"Current Balance in {config.currency}: {balance_EUR}")

  # select the latest, most recent trade
  latest_trade = trades_df.iloc[-1]
 
  if config.verbose:
    print(trades_df[['market','amount','price','side','side_factor','fee', 'value','cum_amount','price_per_piece']].tail(5))
  # determine ration between current market price and the current paid price per piece
  market_vs_ppp = ((ticker_price/latest_trade['price_per_piece']) -1) * 100
  # determine the buying amount in EUR
  #buy_value_EUR = ticker_price * moq #(balance_EUR/100) * buy_amount
  # determine the buying amount in pieces
  #buy_value_pcs = moq#buy_value_EUR / ticker_price
  order_pcs = moq
  # print(f"moq {moq}")
  order_EUR = ticker_price * moq
  # determine the selling amount in pieces
  #sell_value_pcs = (latest_trade['cum_amount']/100) * sell_amount
  balance_pcs = latest_trade['cum_amount']#float(latest_trade['cum_amount'])

  logger.info (f"{latest_trade['market']} Market Price : {ticker_price} PPP : {round(latest_trade['price_per_piece'],4)} ({round(market_vs_ppp, 2)}%)")

  overview_dict["market"][ticker] = ticker_price
  overview_dict["ppp"][ticker] = latest_trade['price_per_piece']

  if market_vs_ppp < 0:
    # market price is lower than current price per piece, potential buy
    if abs(market_vs_ppp) >= config.buy_margin:
      if balance_EUR > order_EUR:
        logger.info (f"{ticker} Buy {order_EUR} EUR ({order_pcs} pieces)")
        if config.trade:
          response = client.buy_order(ticker, order_pcs)
          logger.info(response)
      else:
        logger.info(f"Buy balance too low ({balance_EUR} EUR vs {order_EUR} EUR)")
    else:
      logger.info (f"{ticker} Buy margin too low ({round(market_vs_ppp,2)}% vs {config.buy_margin}%)")
  elif market_vs_ppp > 0:
    if abs(market_vs_ppp) >= config.sell_margin:
    # market price is higher than current price per piece, potential sell
      if balance_pcs > order_pcs:
        logger.info (f"{ticker} Sell {moq} pieces ({round(order_EUR,2)} EUR)")
        if config.trade:
          response = client.sell_order(ticker, order_pcs)
          logger.info(response)      
      else:
        logger.info (f"Sell balance too low ({balance_pcs} pcs vs {order_pcs} pcs)")
    else:
      logger.info (f"{ticker} Sell margin too low ({round(market_vs_ppp,2)}% vs {config.sell_margin}%)")

print(overview_dict)
  #response = client.buy_order(ticker, 20.0)
  #print (response)
