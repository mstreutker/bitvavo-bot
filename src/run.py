import bitvavo as bv
import logging
import sys

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

ticker = 'ADA-EUR' 
currency = 'EUR'
buy_margin = 6      # market price needs to be x% below
sell_margin = 15     # market price needs to be x% above
#buy_amount = 1      # % of available credit for buy
#sell_amount = 1     # % of available amount to sell
debug = True
# instantiate a new bitvavo connection
client = bv.bitvavo_client()

ticker_list = ['ADA-EUR', 'BTC-EUR', 'ETH-EUR']

for ticker in ticker_list:
  print (ticker)

  # get trade history for ticker
  trades_df = client.get_trades (ticker)

  # get actual price for ticker
  ticker_price = client.get_ticker_price(ticker)

  # get actual balance for all currencies
  balance_df = client.get_balance()
  balance_EUR = balance_df[balance_df["symbol"]==currency]['available'].iloc[0]

  # select the latest, most recent trade
  latest_trade = trades_df.iloc[-1]

  # get market details
  market = client.get_market(ticker)
  moq_ = market[market["orderTypes"]=="market"]["minOrderInBaseAsset"].iloc[0]
  # print(type(moq_))
  # print(f"_moq {moq_}")
  # if isinstance(moq_, int):
  #   print ("int")
  #   moq = int(moq_)
  # else:
  #   print("float")
  #   moq = float(moq_)

  # Minimal Order Quantity needs to be float or int (matching market settings), 
  # otherwise API call fails with 309 error
  if moq_.isdigit():
      moq = int(moq_)
  else:
      moq = float(moq_)
  #print(f"moq {moq}")
  #print(market)
  #print(f"MOQ: {moq} Price: {ticker_price * moq}")

  if debug:
    print(trades_df.loc[:,['market','amount','price','side','side_factor','fee', 'value','cum_amount','price_per_piece']])

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
  balance_pcs = float(latest_trade['cum_amount'])

  logger.info (f"{latest_trade['market']} Market Price : {ticker_price} PPP : {round(latest_trade['price_per_piece'],4)} ({round(market_vs_ppp, 2)}%)")

  if market_vs_ppp < 0:
    # market price is lower than current price per piece, potential buy
    if abs(market_vs_ppp) >= buy_margin:
      if balance_EUR > order_EUR:
        logger.info (f"{ticker} Buy {order_EUR} EUR ({order_pcs} pieces)")
        if not debug:
          response = client.buy_order(ticker, order_pcs)
          logger.info(response)
      else:
        logger.info(f"Buy balance too low ({balance_EUR} EUR vs {order_EUR} EUR)")
    else:
      logger.info (f"{ticker} Buy margin too low ({round(market_vs_ppp,2)}% vs {buy_margin}%)")
  elif market_vs_ppp > 0:
    if abs(market_vs_ppp) >= sell_margin:
    # market price is higher than current price per piece, potential sell
      if balance_pcs > order_pcs:
        logger.info (f"{ticker} Sell {moq} pieces ({round(order_EUR,2)} EUR)")
        if not debug:
          response = client.sell_order(ticker, order_pcs)
          logger.info(response)      
      else:
        logger.info (f"Sell balance too low ({balance_pcs} pcs vs {order_pcs} pcs)")
    else:
      logger.info (f"{ticker} Sell margin too low ({round(market_vs_ppp,2)}% vs {sell_margin}%)")


  #response = client.buy_order(ticker, 20.0)
  #print (response)
