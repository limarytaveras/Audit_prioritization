# Explainable Audit Prioritization

Python portfolio project for **risk-based audit planning with entirely synthetic data**.

Author: **Limary Taveras Cruz** · Version 3.0.0 · Educational prototype

[Español](docs/README_ES.md) · [Methodology](docs/METHODOLOGY.md) · [Data dictionary](docs/DATA_DICTIONARY.md) · [GitHub setup](docs/GITHUB_SETUP_ES.md)

## Business problem

Prioritize auditable processes using risk, findings, incidents and coverage; then select work within available hours. Mandatory work comes first and capacity shortfalls remain visible. Human review is required.

## Implemented

- Validated process-year snapshots and cutoff-aware event aggregation.
- Transparent expert scoring with fixed scales and component explanations.
- Per-job estimated hours, reserve and mandatory-work handling.
- Optional logistic regression estimating historical audit selection, evaluated on a temporal holdout. Its output remains separate from priority scores.
- Synthetic generator, CSV results, input hashes and automated tests.

## Quick start

Python 3.10 or later, from this folder:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell alternative: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m audit_planner --demo --with-model
python -m unittest discover -s tests -v
```

The demo generates 48 fictional processes over five snapshots. `outputs/` contains `ranking_2027.csv`, `portfolio_2027.csv` and `run_manifest.json`. Committed sample results are in `examples/`.

Run existing inputs:

```bash
python -m audit_planner --data-dir data/synthetic --output outputs --plan-year 2027 --with-model
```

`universe.csv` is required; findings, incidents and capacity files are optional. Missing event sources mean unknown information; empty tables with headers mean known zero events. Without capacity, the tool uses Top N plus all mandatory jobs. The built-in demo supports 2027; supplied snapshots may use other years.

## Structure

| Location | Purpose |
|---|---|
| src/audit_planner/core.py | Validation, scoring, model, capacity |
| src/audit_planner/demo.py | Reproducible fictional generator |
| src/audit_planner/__main__.py | CLI and export |
| data/synthetic/ | Fictional inputs |
| examples/ | Executed sample results |
| tests/ | Functional and temporal tests |
| docs/ | Methodology, case study, privacy and publishing guidance |

## Limits

Weights and thresholds are illustrative. Historical selection is not adverse-outcome risk. Synthetic metrics do not establish real-world performance. The model is experimental and uncalibrated. Capacity selection is greedy, not mathematical optimization or calendar scheduling. See methodology for historical-data assumptions and selection bias.

## Roadmap

Future high-severity finding prediction, versioned snapshots, calibration, recall at available capacity, sensitivity analysis, human-decision logging and portfolio optimization. Office ranking, dashboards and production deployment are outside this release.

## Privacy and rights

All included records and results are fictional. No original institutional documents are included. See `docs/PRIVACY.md`. No open-source license has been selected; see `RIGHTS.md`.
