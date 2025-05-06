# Architecture Overview

This document describes the high-level structure and major components of the Aged Care Pipeline project.

---

## 1. Project Layout

```text
.
├── README.md
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   ├── adr/
│   ├── architecture.md      ← this file
│   └── howto/
├── pyproject.toml
├── requirements-dev.txt
├── src/
│   └── aged_care_pipeline/
│       ├── cli.py
│       ├── config/
│       ├── delivery/
│       ├── interfaces/
│       ├── logging_config.py
│       ├── monitoring/
│       ├── parsers/
│       ├── refs/
│       ├── scheduler/
│       ├── scrapers/
│       ├── services/
│       ├── utils/
│       └── writers/
└── tests/
```

---

## 2. Major Components

### 2.1 CLI (`src/aged_care_pipeline/cli.py` & `__main__.py`)

- **Entry point** for running the pipeline in one-off or scheduled modes.
- Parses command-line flags (e.g. `--save-raw`, `--save-processed`).

### 2.2 Configuration (`src/aged_care_pipeline/config/`)

- **`endpoints.py`**: URL definitions for each scraper (operations, rads).
- **`global_settings.py`**: shared constants (timeouts, retry limits).
- **`schedules.yaml`**: cron expressions and job schedules.

### 2.3 Scrapers (`src/aged_care_pipeline/scrapers/`)

- **`operations_scraper.py`** & **`rads_scraper.py`**

  - Fetch raw JSON for each NID in `refs/NIDs_Only.csv`.
  - Rate-limit and retry logic in utils.

### 2.4 Parsers (`src/aged_care_pipeline/parsers/`)

- **Field-path definitions** (`*_field_paths.py`) drive each parser.
- **`operations_parser.py`** & **`rads_parser.py`**

  - Convert raw JSON → flattened Python dicts ready for CSV.

### 2.5 Writers (`src/aged_care_pipeline/writers/csv_writer.py`)

- Consolidate parsed records into CSV files under

  - `data/interim/{operations,rads}/`
  - then to `data/processed/{operations,rads}/`

### 2.6 Services (`src/aged_care_pipeline/services/`)

- **Business logic** orchestrating scrapers, parsers, writers.
- Provides a simple function call API for CLI and scheduler layers.

### 2.7 Scheduler (`src/aged_care_pipeline/scheduler/`)

- **`cron_scheduler.py`** & **`apscheduler_runner.py`**

  - Periodically invoke Services according to `schedules.yaml`.

- **Task registry** manages job definitions.

### 2.8 Delivery (`src/aged_care_pipeline/delivery/`)

- **`api_push_delivery.py`**: send processed CSV to external API.
- **`email_delivery.py`**: email notifications on success/failure.

### 2.9 Monitoring & Alerting (`src/aged_care_pipeline/monitoring/`)

- **`healthcheck.py`**: HTTP endpoint for liveness.
- **`alerting.py`**: hooks into delivery failures.

### 2.10 Utilities (`src/aged_care_pipeline/utils/`)

- **`limiter.py`**, **`retry.py`**, **`request_handler.py`**

  - Shared helpers for rate limiting, backoff, and HTTP calls.

- **`validator.py`**: schema-level sanity checks on parsed data.
- **`logger.py`**: standard logger configuration.

### 2.11 Interfaces (`src/aged_care_pipeline/interfaces/`)

- Base classes for Scraper, Parser, Writer, Scheduler to enforce consistent API.

### 2.12 References (`src/aged_care_pipeline/refs/`)

- Static CSVs:

  - `NIDs_Only.csv` – list of target NIDs
  - `ProviderDirectory.csv` – master provider metadata

---

## 3. Data Flow

1. **Raw fetch**
   Scraper pulls JSON from endpoints → `data/raw/{operations,rads}/`.
2. **Interim write**
   Parsers flatten JSON → interim CSV in `data/interim/…/`.
3. **Processing & aggregation**
   Writers consolidate interim files into timestamped CSVs in `data/processed/…/`.
4. **Archive & cleanup**
   Raw JSONs are merged → archived under `data/raw/archive/` → originals deleted.
5. **Delivery**
   Processed CSVs are pushed via API or emailed.
6. **Monitoring**
   Healthcheck and alerting ensure pipeline reliability.

---

## 4. Testing Strategy

- **Unit tests** under `tests/` for each scraper, parser, service, writer.
- **End-to-end tests** (`test_end_to_end/`) validate full pipeline turn-key runs.
- Continuous Integration runs all tests on every commit.

---

## 5. Architecture Decisions

See ADRs in `docs/adr/` for rationale on major design choices (e.g., choice of CSV vs. database, scheduler framework, retry strategy).

---

## 6. Developer Tooling and Configuration

### 6.1 Build & Packaging

Key settings in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "aged_care_pipeline"
version = "0.1.0"
description = "ETL pipeline for Australian aged-care provider data"
authors = [{name = "Charles Lynch"}]
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "structlog>=24.1.0",
  "requests",
  "pandas"
]

[project.scripts]
aged-care-scheduler = "aged_care_pipeline.scheduler.__main__:main"
aged-care-pipeline  = "aged_care_pipeline.cli:main"

[tool.setuptools.package-data]
aged_care_pipeline = [
  "config/*.yaml",
  "data/refs/*.csv"
]
```

### 6.2 Pre-commit Hooks

Defined in `.pre-commit-config.yaml` to enforce style and quality:

```yaml
default_language_version:
  python: python3.10

repos:
  - repo: https://github.com/psf/black
    rev: 25.1.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.11.7
    hooks:
      - id: ruff

  - repo: https://github.com/pycqa/isort
    rev: 6.0.1
    hooks:
      - id: isort

  - repo: https://github.com/pappasam/toml-sort
    rev: v0.24.2
    hooks:
      - id: toml-sort
        args: ["--check"]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier

  - repo: local
    hooks:
      - id: pytest
        name: pytest (collect only)
        entry: pytest tests --collect-only
        pass_filenames: false
        language: system
        always_run: true
```

### 6.3 Git Ignore

Critical patterns in `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
data/**
!data/references/
node_modules/.cache/prettier/
```

_Last updated: 2025-05-06_
