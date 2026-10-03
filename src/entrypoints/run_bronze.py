import argparse
from quant_lakehouse.ingestion.market_data import ingest_to_bronze
import yaml


def main():
    parser = argparse.ArgumentParser(description="Run Bronze Ingestion Pipeline")
    parser.add_argument("--env", default="dev", help="Environment name")
    parser.add_argument("--config", default="conf/dev.yaml", help="Path to config file")
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    storage_root = config.get("storage_root", "./data/lakehouse")
    bronze_path = f"{storage_root}/bronze"

    print(f"Running bronze ingestion for environment: {args.env}")
    ingest_to_bronze(output_path=bronze_path)


if __name__ == "__main__":
    main()
