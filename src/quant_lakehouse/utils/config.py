import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict:
    """Loads configuration based on the ENVIRONMENT environment variable.

    Loads .env if present locally (ignored in Databricks where ENVIRONMENT is set via OS).
    Defaults to 'dev' if ENVIRONMENT is not set.
    """
    load_dotenv()
    env = os.getenv("ENVIRONMENT", "dev")

    cwd = Path.cwd()
    possible_roots = [
        cwd,
        cwd.parent,
        cwd.parent.parent,
        cwd.parent.parent.parent,
    ]

    mod_file = globals().get("__file__")
    if mod_file:
        mod_path = Path(mod_file).resolve()
        possible_roots.extend([
            mod_path.parent,
            mod_path.parent.parent,
            mod_path.parent.parent.parent,
            mod_path.parent.parent.parent.parent,
        ])

    config_path = None
    for root in possible_roots:
        candidate = root / "conf" / f"{env}.yaml"
        if candidate.exists():
            config_path = candidate
            break

    if not config_path:
        for root in possible_roots:
            candidate = root / "conf" / "dev.yaml"
            if candidate.exists():
                config_path = candidate
                break

    if not config_path or not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found for env '{env}' in checked roots: {possible_roots}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f) or {}

    config["environment"] = env
    return config
