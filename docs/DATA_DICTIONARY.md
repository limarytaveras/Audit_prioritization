# Data dictionary

UTF-8 CSV, exact column names, ISO dates YYYY-MM-DD. All distributed rows are synthetic.

## universe.csv

| Column | Meaning |
|---|---|
| process_id | Stable nonempty ID, unique with cutoff_year |
| process_name | Fictional name |
| unit | Team ID matching capacity |
| cutoff_year | Integer snapshot year |
| risk_final, risk_residual | Numbers 0–100 |
| risk_trend, criticality | Ordinal numbers 0–100, higher means greater concern |
| months_since_audit | Nonnegative months |
| audit_interval_months | Positive recommended interval |
| mandatory | 0/1 obligation due in next plan year |
| estimated_hours | Positive job effort |
| selected_next_year | Optional observed 0/1 label, blank when unknown |

## findings.csv

| Column | Meaning |
|---|---|
| finding_id | Unique event ID |
| process_id | Existing universe ID |
| identified_date | Required date known at identification |
| closed_date | Closure date, blank if open |
| severity | low, medium, high, critical |
| recurrent | 0/1 known at identification |

## incidents.csv

| Column | Meaning |
|---|---|
| incident_id | Unique event ID |
| process_id | Existing universe ID |
| event_date | Required known event date |
| severity | low, medium, high, critical |

## capacity.csv

| Column | Meaning |
|---|---|
| unit | Unique team; all current teams required |
| available_hours | Nonnegative finite hours before reserve |

## Outputs

`priority_score` is an index, not a probability. Optional `historical_selection_estimate` is an experimental model estimate kept separate. `reason` lists component scores; `selected` and `selection_reason` record the preliminary portfolio. The manifest includes configuration, SHA-256 input hashes, temporal metrics and remaining hours. Missing optional sources are unknown, while empty valid tables mean zero known events.
