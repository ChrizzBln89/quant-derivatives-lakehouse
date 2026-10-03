# Quant Derivatives Lakehouse

quant-derivatives-lakehouse/
├── .github/workflows/         # CI/CD-Pipelines für GitHub Actions
│   ├── ci.yml                 # Automatisiertes Linting, Typecheck & Pytest
│   └── deploy.yml             # Databricks Asset Bundle (DAB) Deployment
│
├── conf/                      # Konfigurationsdateien (YAML)
│   ├── base.yaml              # Ticker-Listen, Volatilitäts-Lookbacks, Strikes
│   ├── dev.yaml               # Lokale Pfade (z. B. ./data/lakehouse)
│   └── prod.yaml              # Cloud-Pfade (Unity Catalog: catalog.schema.table)
│
├── databricks.yml             # Hauptkonfiguration für Databricks Asset Bundles
├── resources/                 # Deklarative Cloud-Ressourcen (YAML)
│   ├── compute.yml            # Cluster-Spezifikationen & Serverless-Policies
│   └── derivatives_pipeline.yml # Definition der Multi-Task-Pipeline
│
├── src/quant_lakehouse/       # Der eigentliche Programmcode (Python-Paket)
│   ├── domain/                # Reine Finanzmathematik (reines NumPy/SciPy, kein PySpark)
│   ├── ingestion/             # API-Abruf und Extraktion (yfinance, Requests)
│   ├── transformations/       # PySpark-Logik für Bronze, Silver und Gold
│   └── utils/                 # Hilfsfunktionen (SparkSession-Builder, Config-Loader)
│
├── src/entrypoints/           # Ausführbare Startskripte für Jobs & CLI-Aufrufe
│   ├── run_bronze.py          # Startet Extraktion -> Bronze-Tabelle
│   ├── run_silver.py          # Startet Bronze -> Silver-Bereinigung
│   └── run_gold.py            # Startet Silver -> Gold-Derivatebewertung
│
├── tests/                     # Automatisierte Tests (Pytest)
│   ├── conftest.py            # Lokale SparkSession-Fixtures für Tests
│   ├── unit/                  # Mathe-Tests ohne Spark-Overhead (schnell)
│   └── integration/           # PySpark- und Delta-Lake-Pipeline-Tests
│
├── data/lakehouse/            # Lokales Datenverzeichnis (in .gitignore!)
│   ├── bronze/                # Rohe Delta-Tabellen mit _delta_log
│   ├── silver/                # Bereinigte Zeitreihen
│   └── gold/                  # Berechnete Derivate und Greeks
│
├── .gitignore                 # Ignoriert .venv, data/, .pytest_cache etc.
├── Makefile                   # Terminal-Shortcuts für Lint, Test, Run
├── pyproject.toml             # Paket- und Tool-Konfiguration (Ruff, Mypy)
├── requirements.txt           # Python-Abhängigkeiten
└── README.md                  # Architekturbeschreibung & Setup-Doku
