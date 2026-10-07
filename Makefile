# ==============================================================================
# CONFIGURATION & ENVIRONMENT (UV)
# ==============================================================================
SHELL       := /bin/bash
TARGET      ?= dev
JOB_KEY     ?= derivatives_pricing_pipeline

.DEFAULT_GOAL := help

# ==============================================================================
# HELP & OVERVIEW
# ==============================================================================
.PHONY: help
help:
	@echo "Verfügbare Makefile-Targets (uv):"
	@echo "  Setup & Umgebung:"
	@echo "    make setup               - Synchronisiert uv Environment und Dependencies"
	@echo "    make clean               - Entfernt Caches, Build-Artefakte und lokale Daten"
	@echo ""
	@echo "  Code Quality & Tests:"
	@echo "    make lint                - Führt Ruff Linter und Formatter-Check via uv aus"
	@echo "    make format              - Formatiert Code automatisch mit Ruff via uv"
	@echo "    make test-unit           - Schnelle Tests der Domain-Logik via uv"
	@echo "    make test-integration    - Integrationstests (Spark & Delta Lake) via uv"
	@echo "    make test                - Führt alle Tests aus"
	@echo ""
	@echo "  Lokales Lakehouse (Offline Execution):"
	@echo "    make run-bronze          - Extrahiert Marktdaten in Landungszone & lokale Bronze Delta-Tabelle"
	@echo "    make run-silver          - Bereinigt Zeitreihen in lokale Silver Delta-Tabelle"
	@echo "    make run-gold            - Führt Optionsbewertung aus (Gold Delta-Tabelle)"
	@echo "    make run-local-pipeline  - Führt Bronze -> Silver -> Gold sequentiell lokal aus"
	@echo "    make inspect-delta       - Zeigt die Commits im lokalen _delta_log via jq an"
	@echo "    make duckdb-query        - Fragt lokale Delta-Tabellen via DuckDB im CLI ab"
	@echo ""
	@echo "  Databricks CLI & DABs (Cloud Execution):"
	@echo "    make db-auth             - Startet OAuth-Login für Databricks CLI"
	@echo "    make db-validate         - Validiert databricks.yml und Ressourcen"
	@echo "    make db-deploy           - Deployt Bundle (Standard: TARGET=dev)"
	@echo "    make db-deploy-prod      - Deployt Bundle nach Production"
	@echo "    make db-run              - Führt den Pipeline-Job remote im Workspace aus"
	@echo "    make db-destroy          - Zerstört Dev-Ressourcen im Workspace (Kostenstopp)"

# ==============================================================================
# LOCAL SETUP & CODE QUALITY
# ==============================================================================
.PHONY: setup
setup:
	uv sync
	uv pip install -e .

.PHONY: lint
lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

.PHONY: format
format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

.PHONY: test-unit
test-unit:
	uv run pytest tests/unit -v

.PHONY: test-integration
test-integration:
	uv run pytest tests/integration -v

.PHONY: test
test: lint test-unit test-integration

# ==============================================================================
# LOCAL PIPELINE EXECUTION & INSPECTION
# ==============================================================================
.PHONY: run-bronze
run-bronze:
	uv run python src/entrypoints/run_bronze.py

.PHONY: run-silver
run-silver:
	uv run python src/entrypoints/run_silver.py

.PHONY: run-gold
run-gold:
	uv run python src/entrypoints/run_gold.py

.PHONY: run-local-pipeline
run-local-pipeline: run-bronze run-silver run-gold

.PHONY: inspect-delta
inspect-delta:
	@echo "=== Bronze Transaktionslog ==="
	@cat data/lakehouse/bronze/_delta_log/00000000000000000000.json | jq . || true
	@echo ""
	@echo "=== Dateistruktur Bronze Layer ==="
	@ls -la data/lakehouse/bronze/

.PHONY: duckdb-query
duckdb-query:
	duckdb -c "INSTALL delta; LOAD delta; SELECT * FROM delta_scan('data/lakehouse/gold') LIMIT 10;"

# ==============================================================================
# DATABRICKS ASSET BUNDLES (DABs) & CLI WORKFLOW
# ==============================================================================
.PHONY: db-auth
db-auth:
	databricks auth login

.PHONY: db-validate
db-validate:
	databricks bundle validate -t $(TARGET)

.PHONY: db-deploy
db-deploy: db-validate
	databricks bundle deploy -t $(TARGET)

.PHONY: db-deploy-prod
db-deploy-prod:
	databricks bundle deploy -t prod

.PHONY: db-run
db-run:
	databricks bundle run $(JOB_KEY) -t $(TARGET)

.PHONY: db-destroy
db-destroy:
	databricks bundle destroy -t dev

# ==============================================================================
# CLEANUP
# ==============================================================================
.PHONY: clean
clean:
	rm -rf .venv .pytest_cache .ruff_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf data/lakehouse/* data/landing_zone/*
