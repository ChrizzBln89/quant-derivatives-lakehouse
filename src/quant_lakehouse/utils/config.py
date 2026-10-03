import os
import sys
import yaml
from pathlib import Path


def load_config() -> dict:
    """Loads base configuration and merges environment-specific overrides.

    Resolution order:
    1. Command line argument: --env <env> or --config <path>
    2. Environment variable: DATABRICKS_ENV or ENVIRONMENT
    3. Default: 'dev'
    """
    env = "dev"
    config_path = None

    # Simple check for command-line arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--env" and i + 1 < len(sys.argv):
            env = sys.argv[i + 1]
        elif arg == "--config" and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]

    # Fallback to environment variables if not specified via CLI
    if not config_path:
        env = os.getenv("DATABRICKS_ENV", os.getenv("ENVIRONMENT", env))
        config_path = f"conf/{env}.yaml"

    # Load base config
    base_path = Path("conf/base.yaml")
    config = {}
    if base_path.exists():
        with open(base_path, "r") as f:
            config.update(yaml.safe_load(f) or {})

    # Load env-specific config overrides
    env_path = Path(config_path)
    if env_path.exists():
        with open(env_path, "r") as f:
            config.update(yaml.safe_load(f) or {})

    config["environment"] = env
    return config
