from quant_lakehouse.utils import load_config


def main():
    config = load_config()
    print(f"Running silver transformation task for environment: {config.get('environment')}")


if __name__ == "__main__":
    main()
