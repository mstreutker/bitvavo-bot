import bitvavo as bv
import logging
import confighelper
import emailhelper
import sys
import pandas as pd
import datetime
from datetime import datetime


# configure logging settings
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

# initialize configuration settings
config = confighelper.config('.\local.config.ini')

# instantiate bitvavo client
client = bv.bitvavo_client()

# create empty dictionary to store overview results
overview_dict = {"market":{},"ppp":{},"margin":{},"order_pcs":{},"balance_pcs":{}}
ticker_data = []

# run through ticker list
for ticker in config.ticker_list:
  output_dir = f'{ticker}'

  # get market details
  market = client.get_market(ticker)
  moq = client.get_minimal_order_quantity(market)

  # get trade history for ticker
  trades_json = client.get_trades (ticker)

  client.save_trades_json(trades_json, output_dir)
  df_all = client.get_df_from_trades_json (output_dir)
  df_all = client.calc_trades(df_all)
  df_all.to_csv(f"{ticker}_df.csv", sep=';')

  if config.verbose:
    # if running in verbose mode, show the last 5 transactions
    print(df_all[['market','amount','price','side','side_factor','fee', 'value','cum_amount','price_per_piece']].tail(5))

  # get actual price for ticker
  ticker_price = client.get_ticker_price(ticker)

  # select the latest, most recent trade
  latest_trade = df_all.iloc[-1]
 
  # determine ration between current market price and the current paid price per piece
  market_vs_ppp = ((ticker_price/latest_trade['price_per_piece']) -1) * 100

  # set number of pieces in order to the minimal order quantity
  order_pcs = moq
 
  # calculate total order price based on current ticker price * number of pieces (ignoring any fees)
  order_EUR = ticker_price * order_pcs
  
  # get number of available pieces for current ticker
  balance_pcs = latest_trade['cum_amount']

  #logger.info (f"{latest_trade['market']} Market Price : {ticker_price} PPP : {round(latest_trade['price_per_piece'],4)} ({round(market_vs_ppp, 2)}%)")

  action = "hold"

  if market_vs_ppp < 0:
    # market price is lower than current price per piece, potential buy
    if abs(market_vs_ppp) >= config.buy_margin:
      action = "buy"
  elif market_vs_ppp > 0:
    if abs(market_vs_ppp) >= config.sell_margin:
    # market price is higher than current price per piece, potential sell
      if balance_pcs > order_pcs:
        action = "sell" 

  data = {
    "ticker": ticker,
    "market": round(ticker_price, 2),
    "ppp": round(latest_trade['price_per_piece'], 2),
    "margin%": f"{round(market_vs_ppp, 2)}%",
    "margin": round(market_vs_ppp, 4),
    "order_pcs": order_pcs,
    "balance_pcs": round(balance_pcs, 6),
    "order_EUR": round(order_EUR, 6),
    "action": action
  }
  ticker_data.append(data)

overview_df = pd.DataFrame(ticker_data)
print (overview_df)

logger.info (overview_df)

trades_buy = overview_df[overview_df['action']=="buy"].sort_values(by='margin')
trades_sell = overview_df[overview_df['action']=="sell"]

for index, row in trades_sell.iterrows():
  ticker = row["ticker"]
  balance_pcs = row["balance_pcs"]
  order_pcs = row["order_pcs"]
  order_EUR = row["order_EUR"]

  if balance_pcs > order_pcs:
    logger.info (f"{ticker} Sell {order_pcs} pieces ({round(order_EUR,2)} EUR)")
    if config.trade:
      response = client.sell_order(ticker, order_pcs)
      logger.info(response)      
  else:
    logger.info (f"Sell balance too low ({balance_pcs} pcs vs {order_pcs} pcs)")

for index, row in trades_buy.iterrows():
  # get actual balance for the configured currency
  balance_EUR = client.get_balance(config.currency)
  ticker = row["ticker"]
  order_EUR = row["order_EUR"]
  order_pcs = row["order_pcs"]

  if balance_EUR > order_EUR:
    logger.info (f"{ticker} Buy {order_EUR} EUR ({order_pcs} pieces)")
    action = "buy"
    if config.trade:
      response = client.buy_order(ticker, order_pcs)
      logger.info(response)
  else:
    logger.info(f"{ticker} Buy balance too low ({balance_EUR} EUR vs {order_EUR} EUR)")

email_helper = emailhelper.email_helper()

data = []

data.append(email_helper.df_to_plot_table(overview_df))
data.append(email_helper.df_to_plot_bar(overview_df))

# prepare email
now = datetime.now()
email = emailhelper.email_client()
sendTo = email.recipient
emailSubject = f"Bitvavo overview {now.strftime('%Y-%m-%d %H:%M:%S')}"
emailContent = f"Balance {config.currency}: {balance_EUR}"

# send email
email.sendmail(sendTo, emailSubject, emailContent, data)
