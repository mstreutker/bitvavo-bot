import bitvavo as bv
import logging
import confighelper
import emailhelper
import sys
import matplotlib.pyplot as plt
import pandas as pd
import io
import datetime


def df_to_plot_table (df):
  fig, ax = plt.subplots()

  # hide axes
  fig.patch.set_visible(False)
  ax.axis('off')
  ax.axis('tight')
  ax.table(cellText=df.values, colLabels=df.columns,  loc='center')
  fig.tight_layout()
  return fig


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

# run through ticker list
for ticker in config.ticker_list:
  
  # get market details
  market = client.get_market(ticker)
  moq = client.get_minimal_order_quantity(market)

  # get trade history for ticker
  trades_df = client.get_trades (ticker)

  if config.verbose:
    # if running in verbose mode, show the last 5 transactions
    print(trades_df[['market','amount','price','side','side_factor','fee', 'value','cum_amount','price_per_piece']].tail(5))

  # get actual price for ticker
  ticker_price = client.get_ticker_price(ticker)

  # get actual balance for the configured currency
  balance_EUR = client.get_balance(config.currency)

  logger.info (f"Balance {config.currency}: {balance_EUR}")
  logger.info (f"{ticker} Minimal Order Quantity : {moq}")

  # select the latest, most recent trade
  latest_trade = trades_df.iloc[-1]
 
  # determine ration between current market price and the current paid price per piece
  market_vs_ppp = ((ticker_price/latest_trade['price_per_piece']) -1) * 100

  # set number of pieces in order to the minimal order quantity
  order_pcs = moq
 
  # calculate total order price based on current ticker price * number of pieces (ignoring any fees)
  order_EUR = ticker_price * order_pcs
  
  # get number of available pieces for current ticker
  balance_pcs = latest_trade['cum_amount']

  logger.info (f"{latest_trade['market']} Market Price : {ticker_price} PPP : {round(latest_trade['price_per_piece'],4)} ({round(market_vs_ppp, 2)}%)")

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

  overview_dict["market"][ticker] = round(ticker_price,2)
  overview_dict["ppp"][ticker] = round(latest_trade['price_per_piece'],2)
  overview_dict["margin"][ticker] = f"{round(market_vs_ppp, 2)}%"
  overview_dict["order_pcs"][ticker] = order_pcs
  overview_dict["balance_pcs"][ticker] = round(balance_pcs, 6)

overview_df = pd.DataFrame(overview_dict).reset_index()
print (overview_df)

# convert the dataframe to a table plot
fig = df_to_plot_table(overview_df)

# convert the image to bytes
buf = io.BytesIO()
plt.savefig(buf, format='jpg')
buf.seek(0)
data = buf.read()

# prepare email
now = datetime.datetime.now()
email = emailhelper.email_client()
sendTo = email.recipient
emailSubject = f"Bitvavo overview {now.strftime('%Y-%m-%d %H:%M:%S')}"
emailContent = f"Balance {config.currency}: {balance_EUR}"

# send email
email.sendmail(sendTo, emailSubject, emailContent, data)
