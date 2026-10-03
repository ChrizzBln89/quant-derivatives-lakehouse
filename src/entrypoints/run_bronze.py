from quant_lakehouse.ingestion.market_data import ingest_to_bronze
from quant_lakehouse.utils import load_config


def main():
    config = load_config()

    storage_root = config.get("storage_root", "./data/lakehouse")
    bronze_path = f"{storage_root}/bronze"
    tickers = config.get("symbols", ["AAPL", "MSFT", "SPY"])

    print(f"Running bronze ingestion for environment: {config.get('environment')}")
    ingest_to_bronze(output_path=bronze_path, tickers=tickers)


if __name__ == "__main__":
    main()
