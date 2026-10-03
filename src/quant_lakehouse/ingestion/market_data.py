from datetime import datetime
from deltalake import write_deltalake
import pandas as pd
import yfinance as yf


def fetch_stock_data(
    tickers: list[str] = ["AAPL", "MSFT", "SPY"], period: str = "1y"
) -> pd.DataFrame:
    """Downloads historical stock data for given tickers using yfinance."""
    all_data = []
    for ticker_symbol in tickers:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period).reset_index()
        hist["ticker"] = ticker_symbol
        all_data.append(hist)

    if not all_data:
        return pd.DataFrame()

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.columns = [c.lower().replace(" ", "_") for c in combined_df.columns]
    return combined_df


def ingest_to_bronze(
    output_path: str = "./data/lakehouse/bronze",
    tickers: list[str] = ["AAPL", "MSFT", "SPY"],
) -> None:
    """Fetches stock data and writes it to Delta Lake Bronze layer using deltalake."""
    pdf = fetch_stock_data(tickers=tickers)
    if pdf.empty:
        raise ValueError("No data fetched from yfinance.")

    pdf["ingested_at"] = datetime.utcnow()

    write_deltalake(output_path, pdf, mode="overwrite")
    print(f"Successfully ingested {len(pdf)} rows to bronze path: {output_path}")


if __name__ == "__main__":
    ingest_to_bronze()
