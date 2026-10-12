from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()


def fetch_stock_data(tickers: list[str] | None = None, period: str = "1y") -> str:
    """Downloads historical stock data for given tickers using yfinance and dumps to landing zone with timestamp."""
    if tickers is None:
        tickers = ["AAPL", "MSFT", "SPY"]

    all_data = []
    for ticker_symbol in tickers:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period).reset_index()
        hist["ticker"] = ticker_symbol
        all_data.append(hist)

    if not all_data:
        raise ValueError("No data fetched from yfinance.")

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df["timestamp"] = datetime.now(UTC)
    combined_df.columns = [c.lower().replace(" ", "_") for c in combined_df.columns]

    project_root = Path(__file__).resolve().parent.parent.parent.parent
    landing_zone_dir = project_root / "data" / "landing_zone"
    landing_zone_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    landing_file_path = landing_zone_dir / f"market_data_{timestamp_str}.csv"

    combined_df.to_csv(landing_file_path, index=False)
    print(f"Dumped raw data to landing zone: {landing_file_path}")

    return str(landing_file_path)


if __name__ == "__main__":
    fetch_stock_data()
