from src.utils.bitvavo_utils import BitvavoClient
from src.utils.config_utils import TickerConfig, get_absolute_filepath, read_ticker_config
from src.utils.email_utils import email_helper, email_client
from decimal import Decimal
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt

client = BitvavoClient()
email_helper = email_helper()

current_date = datetime.now().date()

def process_ticker(ticker_config):
    ticker = ticker_config.ticker
    balance_EUR = client.get_balance('EUR')
    print(balance_EUR)
    trades_json, trades_df = client.get_trades(ticker)

    market_df, minimal_order_qty = client.get_market(ticker)
    print (minimal_order_qty)

    ticker_price = Decimal(client.get_ticker_price(ticker))
    print(f"ticker price: {ticker_price}")

    order_EUR = Decimal(minimal_order_qty) * ticker_price
    print(f"order_EUR: {order_EUR}")

    trades_df, latest_trade_df = client.calc_trades(trades_df)
    latest_trade_df = latest_trade_df.iloc[-1]
    price_per_piece = Decimal(latest_trade_df['price_per_piece'])

    margin = client.calc_margin(price_per_piece, ticker_price)
    print(margin)

    action = client.calc_proposed_action(margin, ticker_config)
    print(action)

    buy_cooldown = latest_trade_df["buy_cooldown"]
    last_trade_date = latest_trade_df["_timestamp"].date()
    balance_amount = latest_trade_df["camount"]
    print (f"buy_cooldown: {buy_cooldown}")
    print (f"last_trade_date: {last_trade_date}")
    print (f"current_date: {current_date}")
    print (f"balance_amount: {balance_amount}")

    wait = client.wait_for_cooldown(buy_cooldown, last_trade_date, current_date)
    print(f"wait: {wait}")

    execute = False
    reason = ""

    if action == "buy":
        if (balance_EUR > order_EUR):
            if (wait==False):
                reason = f"{ticker} Buy {order_EUR} EUR ({minimal_order_qty} pieces)"
                execute = True
            else:
                reason = f"{ticker} Cooldown active: {buy_cooldown}"
        else:
            reason = f"{ticker} Buy balance too low ({balance_EUR} EUR vs {order_EUR} EUR)"
            execute = False

    if action == "sell":
        if (balance_amount > minimal_order_qty):
            reason = f"{ticker} Sell {minimal_order_qty} pieces ({round(order_EUR,2)} EUR)"
            execute = True
        else:
            reason = f"Sell balance too low ({balance_amount} pcs vs {minimal_order_qty} pcs)"
            execute = False
    
    print(f"execute: {execute}")
    print(f"reason: {reason}")

    data = {
        "ticker": ticker,
        "market": round(float(ticker_price), 2),
        "ppp": round(float(price_per_piece), 2),
        "margin%": f"{round(float(margin), 2)}%",
        "margin": round(float(margin), 4),
        "order_pcs": minimal_order_qty,
        "balance_pcs": round(balance_amount, 6),
        "order_EUR": round(order_EUR, 6),
        "action": action,
        "execute": execute
    }

    return data

def email_results(overview_df):

    balance_EUR = client.get_balance('EUR')
    data = []
    
    data.append(email_helper.df_to_plot_table(overview_df))
    data.append(email_helper.df_to_plot_bar(overview_df))

    #plt.show()

    # prepare email
    now = datetime.now()
    email = email_client()
    sendTo = email.recipient
    emailSubject = f"Bitvavo overview {now.strftime('%Y-%m-%d %H:%M:%S')}"
    emailContent = f"Balance EUR: {balance_EUR}"

    # send email
    #email.sendmail(sendTo, emailSubject, emailContent, data)