<<<<<<< HEAD

# Aged_Care_Pipeline

Aged Care Pipeline — Python ETL + prediction pipeline for aged care outcome scoring.

# Tech: Python, Pandas, FastAPI, Docker, CI

# Aged Care Pipeline

![CI](https://github.com/ChaLyn03/Aged_Care_Pipeline/actions/workflows/ci.yml/badge.svg)

Aged Care Pipeline — production-style Python ETL + scraping pipeline for
Australian aged care provider data.

Built to transform fragmented public API data into analysis-ready datasets
supporting quality, occupancy, and funding analysis across providers.

Tech: Python, pandas, requests, APScheduler, pytest, pre-commit.

## Problem Context

Public aged care data is fragmented and not immediately analysis-ready.
This pipeline pulls provider details by NID, normalizes nested JSON into a
flat schema, and emits CSV outputs suitable for downstream reporting or
scoring.

The result is a repeatable ingestion layer suitable for analysts,
policy evaluation, or downstream scoring models.

## Architecture (High-Level)

```
           +------------------+
NID list ->| Scraper (API)    |--> raw JSON (per NID)
           +------------------+
                      |
                      v
           +------------------+
           | Parser (schema)  |--> interim JSON (rows)
           +------------------+
                      |
                      v
           +------------------+
           | Writer (CSV)     |--> processed CSV
           +------------------+
                      |
                      v
           +------------------+
           | Delivery (email/ |
           | API push)        |
           +------------------+
```

The pipeline is intentionally modular to allow independent evolution of
scraping, parsing, and delivery stages.

## Data Flow Overview

1. Load NIDs from reference CSVs in `src/aged_care_pipeline/refs`.
2. Scrape each provider from MyAgedCare endpoints.
3. Parse nested JSON into a consistent field set.
4. Write outputs to `data/processed/<pipeline>/`.
5. Archive raw/interim JSON for traceability and auditability.

## Quick Start

Tested on Python 3.10+ (Linux).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run a full scrape → parse → write pipeline:

```bash
aged-care-pipeline operations run
```

Run with a small sample:

```bash
aged-care-pipeline rads run --limit 5
```

Override output location:

```bash
export AGED_CARE_DATA_ROOT=/path/to/data
```

## CLI Usage

Pipelines available: `operations`, `rads`

```bash
aged-care-pipeline <pipeline> run      # scrape -> parse -> CSV
aged-care-pipeline <pipeline> scrape   # raw JSON only
aged-care-pipeline <pipeline> parse <raw.json>
aged-care-pipeline <pipeline> write <records.json>
aged-care-pipeline <pipeline> cleanup  # archive raw/interim
```

## Example Output

CSV output (one row per provider, hundreds of fields):

```csv
nid,name,state,postcode,agedCareHomes_occupancy_value,income_total
123456,Example Home,NSW,2000,92.1,1345000
234567,Example Lodge,VIC,3000,88.4,972000
```

Example log snippet:

```
[1/5] Scraping 123456
[Parser] Parsed 72 fields for NID 123456
Wrote CSV -> data/processed/operations/operations_12_05_2024.csv
```

## Tests

```bash
pytest -q
```

Coverage focus: parser field extraction, scraper response handling, end-to-end
pipeline flow.

## My Contributions

- Designed and implemented a full end-to-end ETL pipeline
  (scraping, parsing, validation, and CLI orchestration).
- Added pipeline validation signals (missing fields, NID coverage).
- Implemented scheduling and delivery scaffolding for automation.
- Structured tests across unit, integration, and end-to-end layers.

## Design Decisions & Trade-offs

- CSV chosen over database storage to simplify downstream analytics
  and reduce operational complexity at this stage.
- Flat CSV outputs favor analytics tooling compatibility over nested fidelity.
- Per-NID raw JSON retention balances traceability with storage cost.
- Minimal dependencies to keep the runtime footprint small and portable.

## Limitations & Next Steps

- Scrapes depend on upstream API availability and schema stability.
- Current dataset is snapshot-based; time-series diffs are planned.
- Add richer validation (schema drift detection) and coverage reporting.
- Expand delivery options and configuration (per-client filter rules).

## Repo Layout

```
src/aged_care_pipeline/  # pipeline code (scrapers, parsers, writers)
tests/                   # unit + integration + e2e tests
data/                    # raw/interim/processed outputs (gitignored)
docs/                    # roadmap and notes
```

## Roadmap (Short)

See `docs/roadmap.md` for planned improvements: scheduler automation,
change detection, and validation enhancements.

> > > > > > > 363fc26 (docs: improve README and add project docs)
