# Databricks Asset Bundle (DAB) File Overview & Architecture Manifest

This document provides a comprehensive overview of all the files necessary for the **Databricks Asset Bundle (DAB)** in the `quant-derivatives-lakehouse` repository. It outlines the structural layout, configuration definitions, entrypoints, and core library components required for deployment and execution across development and production environments.

---

## 📂 Repository File Tree for DAB

```text
quant-derivatives-lakehouse/
├── databricks.yml                 # Main Databricks Asset Bundle configuration
├── resources/
│   ├── compute.yml                # Compute & cluster specifications (quant_engine_cluster)
│   └── derivatives_pipeline.yml   # Databricks Job workflow & task DAG (derivatives_pricing_pipeline)
├── src/
│   ├── entrypoints/               # Job entrypoint scripts executed by tasks
│   │   ├── run_bronze.py          # Task 1: Ingestion & Raw Landing
│   │   ├── run_silver.py          # Task 2: Cleaning & Volatility Calibration
│   │   └── run_gold.py            # Task 3: Vectorized Arrow UDF Black-Scholes Valuation
│   └── quant_lakehouse/           # Core Python package code
│       ├── __init__.py
│       ├── domain/                # Financial & mathematical models
│       │   ├── black_scholes.py   # Black-Scholes pricing & analytics
│       │   └── statistics.py      # Statistical utility functions
│       ├── ingestion/             # Data extraction modules
│       │   └── market_data.py     # Market data connectors (e.g. yfinance)
│       ├── transformations/       # Medallion architecture transformations
│       │   ├── bronze.py          # Bronze layer logic
│       │   ├── silver.py          # Silver layer logic
│       │   └── gold.py            # Gold layer logic
│       └── utils/                 # Shared utilities
│           └── spark.py           # Spark session initialization & configs
├── conf/
│   ├── base.yaml                  # Base pipeline configuration parameters
│   ├── dev.yaml                   # Development environment overrides
│   └── prod.yaml                  # Production environment overrides
└── pyproject.toml                 # Package definition, build system & dependencies
```

---

## 📋 Detailed File Declarations & Purpose

### 1. Bundle & Resource Configuration Files

- **`databricks.yml`**
  - **Purpose**: Root DAB manifest file. Defines the bundle name (`quant-derivatives-lakehouse`), file inclusion patterns (`resources/*.yml`), synchronization rules (`sync.exclude`), global variables (`environment`, `config_path`), and target environments (`dev` and `prod`).
  - **Key Declarations**: Targets configuration, workspace paths, and sync filters.

- **`resources/compute.yml`**
  - **Purpose**: Defines cluster infrastructure and dependencies for the pipeline jobs.
  - **Key Declarations**:
    - Cluster key: `quant_engine_cluster`
    - Spark runtime: `15.4.x-scala2.12` with single-node profile (`spark.databricks.cluster.profile: singleNode`) and Apache Arrow optimizations (`spark.sql.execution.arrow.pyspark.enabled: true`).
    - Python libraries: PyPI packages (`yfinance>=0.2.40`, `scipy>=1.12.0`, `pyarrow>=15.0.0`, `pyyaml>=6.0.1`).

- **`resources/derivatives_pipeline.yml`**
  - **Purpose**: Defines the Databricks Workflow Job (`derivatives_pricing_pipeline`) and execution DAG.
  - **Key Declarations**:
    - Job scheduling (Cron expression with environment-aware pause status: paused in dev, unpaused in prod).
    - Task DAG:
      1. `run_bronze` (`src/entrypoints/run_bronze.py`)
      2. `run_silver` (`src/entrypoints/run_silver.py`, depends on `run_bronze`)
      3. `run_gold` (`src/entrypoints/run_gold.py`, depends on `run_silver`)
    - Runtime parameters passing environment (`--env`) and config path (`--config`).
    - Email notifications on job failure.

---

### 2. Job Entrypoint Scripts

- **`src/entrypoints/run_bronze.py`**
  - **Purpose**: Entrypoint for the Bronze ingestion task. Connects to market data sources and lands raw data into the Delta lakehouse.

- **`src/entrypoints/run_silver.py`**
  - **Purpose**: Entrypoint for the Silver transformation task. Cleans raw data and performs volatility calibration.

- **`src/entrypoints/run_gold.py`**
  - **Purpose**: Entrypoint for the Gold valuation task. Applies vectorized Apache Arrow Pandas UDFs for high-performance Black-Scholes option pricing.

---

### 3. Core Package Modules (`src/quant_lakehouse/`)

- **`src/quant_lakehouse/utils/spark.py`**
  - **Purpose**: Utility functions for initializing and configuring PySpark sessions with Delta Lake support.

- **`src/quant_lakehouse/ingestion/market_data.py`**
  - **Purpose**: Data acquisition logic using external APIs (e.g., Yahoo Finance).

- **`src/quant_lakehouse/transformations/bronze.py`, `silver.py`, `gold.py`**
  - **Purpose**: Core business logic implementing the Medallion architecture transformations across bronze, silver, and gold layers.

- **`src/quant_lakehouse/domain/black_scholes.py` & `statistics.py`**
  - **Purpose**: Quantitative finance domain models, pricing formulas, and statistical calculators.

---

### 4. Configuration & Packaging Files

- **`conf/dev.yaml` & `conf/prod.yaml` (and `conf/base.yaml`)**
  - **Purpose**: Environment-specific configuration parameters (catalog names, schema names, paths, batch sizes) loaded by the entrypoint scripts.

- **`pyproject.toml`**
  - **Purpose**: Defines Python package metadata (`quant_lakehouse`), build backend (`setuptools`), and dependency constraints (`pyspark`, `delta-spark`, `pandas`, `numpy`, `scipy`, `yfinance`, `duckdb`). Enables the codebase to be installed as a Python library within Databricks compute environments.

---

## 🚀 Synchronization & Deployment Summary

When running `databricks bundle deploy` (or via CI/CD pipelines in `.github/workflows/`), Databricks Asset Bundles syncs the code to the workspace root path defined in `databricks.yml`. 

- **Excluded from Sync**: `.git/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `data/`, `conf/dev.yaml`, and `tests/` are excluded during workspace synchronization to keep deployments clean and performant.
- **Execution**: Jobs reference Python files directly via relative paths from the workspace root (e.g., `src/entrypoints/run_bronze.py`), leveraging the synced codebase and cluster-installed PyPI libraries.
