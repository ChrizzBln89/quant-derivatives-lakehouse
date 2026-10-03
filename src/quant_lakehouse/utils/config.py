import yaml
from pathlib import Path


def load_config(env: str = "local") -> dict:
    """Loads configuration for the specified environment manually ('local', 'dev', 'prod')."""
    config_path = Path(f"conf/{env}.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f) or {}

    config["environment"] = env
    return config
