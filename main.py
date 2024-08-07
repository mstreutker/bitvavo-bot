from src.app import process_ticker, email_results
from src.utils.config_utils import get_absolute_filepath, read_ticker_config
from src.utils.references import TICKER_CONFIG
import pandas as pd

def main():
    """
    Main entry point for the application
    """
    try:
        # start app
        a = 1

        config_file_path = get_absolute_filepath(TICKER_CONFIG)
        ticker_configs = read_ticker_config(config_file_path)

        ticker_data = []

        for config in ticker_configs:
            data = process_ticker (config)
            ticker_data.append(data)

        overview_df = pd.DataFrame(ticker_data)
        print(overview_df)
        email_results(overview_df)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()