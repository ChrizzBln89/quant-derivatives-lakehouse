import os
from datetime import UTC, datetime

import pandas as pd
import yfinance as yf

from quant_lakehouse.utils import get_spark_session


def fetch_stock_data(
    tickers: list[str] | None = None, period: str = "1y"
) -> pd.DataFrame:
    """Downloads historical stock data for given tickers using yfinance."""
    if tickers is None:
        tickers = ["AAPL", "MSFT", "SPY"]

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
    output_path: str = "default.bronze_derivatives",
    tickers: list[str] | None = None,
) -> None:
    """Fetches stock data, dumps raw CSV to landing zone, and writes to Delta Lake Bronze layer."""
    if tickers is None:
        tickers = ["AAPL", "MSFT", "SPY"]

    spark = get_spark_session()
    pdf = fetch_stock_data(tickers=tickers)
    if pdf.empty:
        raise ValueError("No data fetched from yfinance.")

    landing_zone_dir = "data/landing_zone"
    os.makedirs(landing_zone_dir, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    landing_file_path = os.path.join(landing_zone_dir, f"market_data_{timestamp}.csv")
    pdf.to_csv(landing_file_path, index=False)
    print(f"Dumped raw data to landing zone: {landing_file_path}")

    df_raw = pd.read_csv(landing_file_path)
    df_raw["ingested_at"] = datetime.now(UTC)

    df = spark.createDataFrame(df_raw)

    if "/" in output_path or output_path.startswith(("dbfs:", "file:")):
        abs_path = (
            output_path
            if "://" in output_path
            else f"file://{os.path.abspath(output_path)}"
        )
        df.write.format("delta").mode("overwrite").save(abs_path)
    else:
        spark.sql("CREATE DATABASE IF NOT EXISTS default")
        df.write.format("delta").mode("overwrite").saveAsTable(output_path)

    print(
        f"Successfully ingested {len(pdf)} rows from landing zone to bronze destination: {output_path}"
    )


if __name__ == "__main__":
    ingest_to_bronze()
