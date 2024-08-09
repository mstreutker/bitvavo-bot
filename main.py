from src.app import process_ticker, email_results
from src.utils.config_utils import get_absolute_filepath, read_ticker_config
from src.utils.references import TICKER_CONFIG
import pandas as pd
import argparse

def main():
    """
    Main entry point for the application
    """
    try:
        # Initialize the parser
        parser = argparse.ArgumentParser(description="A script that does something.")

        # Add arguments
        parser.add_argument('--debug', action='store_true', help="Run the program in debug mode, no trades")

        # Parse the arguments
        args = parser.parse_args()

        debug = False

        if args.debug:
            print("Debug mode is on.")
            debug = True

        config_file_path = get_absolute_filepath(TICKER_CONFIG)
        ticker_configs = read_ticker_config(config_file_path)

        ticker_data = []

        for config in ticker_configs:
            print (f"start ticker {config.ticker}")
            data = process_ticker (config, debug)
            print (f"finished ticker {config.ticker}")
            ticker_data.append(data)

        overview_df = pd.DataFrame(ticker_data)
        print(overview_df)
        email_results(overview_df)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()