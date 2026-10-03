import yaml
from pathlib import Path


def load_config() -> dict:
    """Loads the single configuration file."""
    path = Path("conf/config.yaml")
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, "r") as f:
        return yaml.safe_load(f) or {}
