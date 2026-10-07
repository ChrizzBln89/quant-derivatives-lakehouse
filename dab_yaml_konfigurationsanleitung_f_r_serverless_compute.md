# Databricks Asset Bundles (DAB) – YAML-Konfigurationsanleitung (Serverless)

Diese Anleitung erklärt den exakten Aufbau der YAML-Dateien für ein modulares Databricks Asset Bundle mit **Serverless Compute**.

---

## 1. Übersicht: Welche Dateien brauchst du?

Für ein sauberes, wartbares Projekt benötigst du genau drei YAML-Dateien:

```text
mein-projekt/
├── databricks.yml          # 1. Hauptdatei: Name, Includes, Sync, Targets & Variablen
└── resources/
    ├── schemas.yml         # 2. Infrastruktur: Unity Catalog Schemas
    └── jobs.yml            # 3. Workflows: Tasks & Serverless Environment
```

---

## 2. Datei 1: `databricks.yml` (Die Steuerzentrale)

Die `databricks.yml` deklariert Metadaten, Deployment-Ziele und Variablen. Sie enthält **keine** Job-Details.

### Vorlage:
```yaml
bundle:
  name: derivatives_pipeline

# Ressourcen modular aus dem Ordner resources/ laden
include:
  - resources/*.yml

# Lokale Dateien, die NICHT in den Databricks-Workspace synchronisiert werden dürfen
sync:
  exclude:
    - .env
    - .venv/
    - data/
    - tests/
    - __pycache__/
    - "*.parquet"

# Eigene Variablen mit Fallback-Werten definieren
variables:
  catalog:
    description: "Ziel-Katalog im Unity Catalog"
    default: "workspace"
  schema:
    description: "Ziel-Schema für die Medallion-Schichten"
    default: "silver"

# Deployment-Ziele (Umgebungen)
targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://dbc-f67052a4-d0c8.cloud.databricks.com
    variables:
      catalog: "workspace"
      schema: "silver_dev"

  prod:
    mode: production
    workspace:
      host: https://dbc-f67052a4-d0c8.cloud.databricks.com
    variables:
      catalog: "workspace"
      schema: "silver"
```

### Wie du die Felder befüllst:

| Block / Feld | Was gehört hinein? | Beispiel / Erklärung |
| :--- | :--- | :--- |
| `bundle.name` | Technischer Projektname (ohne Leerzeichen, mit Bindestrich/Unterstrich). | `derivatives_pipeline` |
| `include` | Liste von Pfaden zu ausgelagerten YAML-Dateien. | `- resources/*.yml` (lädt alles im Ordner). |
| `sync.exclude` | Alles, was groß ist oder lokal bleiben muss. | `data/` (Sample-Parquets), `.env` (Secrets), `.venv/`. |
| `variables.<name>` | Variablen, die in Jobs oder Schemas dynamisch sein sollen. | `catalog`, `schema`. |
| `targets.<name>` | Name des Environments. Typisch: `dev`, `prod`. | `dev` wird mit `-t dev` in der CLI angesprochen. |
| `targets.<name>.mode` | `development` oder `production`. | `development` hängt automatisch deinen Benutzernamen vor Ressourcen und pausiert Schedules. `production` deployt 1:1. |
| `targets.<name>.workspace.host` | Die Workspace-URL aus deinem Browser. | `https://dbc-xxxx.cloud.databricks.com` |
| `targets.<name>.variables` | Konkrete Werte für dieses Target. | In `dev` z. B. `schema: "silver_dev"`, in `prod` z. B. `schema: "silver"`. |

---

## 3. Datei 2: `resources/schemas.yml` (Unity Catalog Schemas)

Diese Datei sorgt dafür, dass Databricks das Ziel-Schema automatisch anlegt, falls es noch nicht existiert.

### Vorlage:
```yaml
resources:
  schemas:
    silver_layer_schema:
      name: ${var.schema}
      catalog_name: ${var.catalog}
      comment: "Managed Silver Schema, deployed via Databricks Asset Bundle"
```

### Wie du die Felder befüllst:

| Feld | Was gehört hinein? | Beispiel / Erklärung |
| :--- | :--- | :--- |
| `resources.schemas.<identifier>` | Ein interner Bezeichner für das Bundle (frei wählbar). | `silver_layer_schema` (nur intern für DAB relevant). |
| `name` | Der tatsächliche Name des Schemas in Unity Catalog. | `${var.schema}` (zieht den Wert aus dem aktiven Target). |
| `catalog_name` | Der Name des übergeordneten Katalogs. | `${var.catalog}` (z. B. `workspace` in der Free Edition). |
| `comment` | Optionale Beschreibung für Unity Catalog. | `"Erstellt via DAB"` |

---

## 4. Datei 3: `resources/jobs.yml` (Serverless Job & Tasks)

Hier deklarierst du deine Workflows. Für **Serverless Compute** benötigst du keinen Cluster-Block (`new_cluster` oder `job_clusters`), sondern nutzt den Block **`environments`**.

### Vorlage:
```yaml
resources:
  jobs:
    derivatives_etl_job:
      name: "[${bundle.target}] Derivatives ETL Job"

      tasks:
        - task_key: run_transformation
          spark_python_task:
            python_file: src/entrypoints/run_silver.py
            parameters: []
          # Verweist auf das unten definierte Serverless-Environment
          environment_key: serverless_env

      # Definition der Serverless-Laufzeit & Übergabe von Umgebungsvariablen
      environments:
        - environment_key: serverless_env
          spec:
            client: "1"
            spark_env_vars:
              ENV: ${bundle.target}
              INPUT_TABLE: "${var.catalog}.default.bronze_derivatives"
              OUTPUT_TABLE: "${var.catalog}.${var.schema}.silver_derivatives"
```

### Wie du die Felder befüllst:

| Feld | Was gehört hinein? | Beispiel / Erklärung |
| :--- | :--- | :--- |
| `resources.jobs.<identifier>` | Interner Bezeichner für den Job. | `derivatives_etl_job` (wird bei `bundle run` genutzt). |
| `name` | Sichtbarer Name des Jobs im Databricks UI. | `"[${bundle.target}] Derivatives ETL"` $\rightarrow$ ergibt `[dev] Derivatives ETL`. |
| `tasks` | Liste der auszuführenden Einzelschritte. | Mindestens ein Task. |
| `task_key` | Eindeutiger Name des Tasks innerhalb des Jobs. | `run_transformation` |
| `spark_python_task.python_file` | Relativer Pfad zum Python-Einstiegspunkt. | `src/entrypoints/run_silver.py` |
| `environment_key` | Bindeglied zwischen Task und Compute-Konfiguration. | `serverless_env` (muss exakt dem Key unter `environments` entsprechen). |
| `environments.spec.client` | Spezifikation des Serverless-Clients (Databricks Runtime Standard). | Immer `"1"`. |
| `environments.spec.spark_env_vars` | Key-Value-Paare, die in Python über `os.environ` abrufbar sind. | Werden über `${var.<name>}` aus der `databricks.yml` gespeist. |

---

## 5. Das Zusammenspiel der Variablen

So fließen die Werte von der YAML-Datei in deinen Python-Code:

```text
1. databricks.yml (Target 'dev')
   variables:
     catalog: "workspace"
     schema: "silver_dev"
        │
        ▼
2. resources/jobs.yml
   spark_env_vars:
     OUTPUT_TABLE: "${var.catalog}.${var.schema}.silver_derivatives"
     (Wird aufgelöst zu: "workspace.silver_dev.silver_derivatives")
        │
        ▼
3. src/entrypoints/run_silver.py (Python)
   import os
   output_table = os.environ["OUTPUT_TABLE"]
   df.write.saveAsTable(output_table)
```

---

## 6. Deployment-Befehle im Terminal

Sobald die drei YAML-Dateien angelegt sind, steuerst du den Lifecycle über die CLI:

```bash
# 1. Prüfen, ob alle YAML-Dateien syntaktisch und semantisch korrekt sind
databricks bundle validate -t dev

# 2. Schema anlegen und Job in Databricks registrieren
databricks bundle deploy -t dev

# 3. Den Serverless Job manuell anstoßen
databricks bundle run -t dev derivatives_etl_job
```