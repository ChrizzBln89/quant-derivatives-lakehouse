import sys
import yaml
from pathlib import Path


def load_config() -> dict:
    """Loads the environment configuration file.

    Defaults to 'conf/local.yaml' unless --env or --config is passed.
    """
    config_path = "conf/local.yaml"

    for i, arg in enumerate(sys.argv):
        if arg == "--env" and i + 1 < len(sys.argv):
            env = sys.argv[i + 1]
            config_path = f"conf/{env}.yaml"
        elif arg == "--config" and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f) or {}

    config["environment"] = path.stem
    return config
