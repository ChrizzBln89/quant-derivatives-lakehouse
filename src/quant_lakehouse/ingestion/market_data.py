from datetime import datetime
import pandas as pd
import yfinance as yf
from pyspark.sql import SparkSession


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
    output_path: str = "default.bronze_derivatives",
    tickers: list[str] = ["AAPL", "MSFT", "SPY"],
) -> None:
    """Fetches stock data and writes it to Delta Lake Bronze table or path using Spark Delta writer."""
    spark = SparkSession.builder.getOrCreate()
    pdf = fetch_stock_data(tickers=tickers)
    if pdf.empty:
        raise ValueError("No data fetched from yfinance.")

    pdf["ingested_at"] = datetime.utcnow()

    df = spark.createDataFrame(pdf)
    
    if "/" in output_path or output_path.startswith("dbfs:") or output_path.startswith("file:"):
        abs_path = output_path if "://" in output_path else f"file://{output_path}"
        df.write.format("delta").mode("overwrite").save(abs_path)
    else:
        spark.sql("CREATE DATABASE IF NOT EXISTS default")
        df.write.format("delta").mode("overwrite").saveAsTable(output_path)

    print(f"Successfully ingested {len(pdf)} rows to bronze destination: {output_path}")


if __name__ == "__main__":
    ingest_to_bronze()
