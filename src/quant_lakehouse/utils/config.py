import os

from dotenv import load_dotenv


def load_config() -> dict:
    """Loads configuration purely from environment variables (.env locally, Databricks in cloud)."""
    load_dotenv()

    symbols_env = os.getenv("SYMBOLS", "AAPL,MSFT,SPY")
    symbols = [s.strip() for s in symbols_env.split(",") if s.strip()]

    return {
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "storage_root": os.getenv("STORAGE_ROOT", "default.bronze_derivatives"),
        "symbols": symbols,
        "risk_free_rate": float(os.getenv("RISK_FREE_RATE", "0.035")),
        "volatility_lookback_days": int(os.getenv("VOLATILITY_LOOKBACK_DAYS", "252")),
    }
