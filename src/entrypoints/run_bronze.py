from quant_lakehouse.ingestion.market_data import ingest_to_bronze
from quant_lakehouse.utils import load_config


def main():
    config = load_config()

    storage_root = config.get("storage_root", "default.bronze_derivatives")
    tickers = config.get("symbols", ["AAPL", "MSFT", "SPY"])

    print(f"Running bronze ingestion for environment: {config.get('environment')}")
    ingest_to_bronze(output_path=storage_root, tickers=tickers)


if __name__ == "__main__":
    main()
