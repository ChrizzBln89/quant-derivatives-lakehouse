import os
import yaml
from pathlib import Path


def load_config() -> dict:
    """Loads configuration based on the ENVIRONMENT environment variable.

    Defaults to 'local' if ENVIRONMENT is not set.
    """
    env = os.getenv("ENVIRONMENT", "local")
    config_path = Path(f"conf/{env}.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f) or {}

    config["environment"] = env
    return config
