# Methodology

One row represents one process at December 31 of a cutoff year. Plan year Y uses only snapshot Y-1. Historical rows are never selected into the current portfolio.

## Scores

| Component | Formula |
|---|---|
| Risk R | .40 final + .25 residual + .20 trend + .15 criticality |
| Coverage C | 100 × min(months since audit / recommended interval, 1) |
| Findings H | 100 × [.45 min(high/5,1) + .30 min(recurrent/3,1) + .25 min(open/8,1)] |
| Incidents I | 100 × [.60 min(high incidents/3,1) + .40 min(total incidents/10,1)] |
| Priority | .45 R + .25 C + .20 H + .10 I |

Risk fields are supplied 0–100 values. Suggested ordinal trend values (25 decreasing, 50 stable, 90 increasing) are illustrative assumptions. All caps, weights and thresholds require domain validation. No quantiles are calculated across training and test data. If an optional event source is absent, its weight is redistributed. Known zero events score zero.

Findings are counted through cutoff. Open means no closure or closure after cutoff. High includes critical. Incidents use the preceding 12 months. Severity and recurrence are assumed known at event identification and static; changing assessments need versioned history. Event dates assume no reporting delay. Supplied risk and coverage snapshots must also be point-in-time accurate.

Mandatory flags mean obligations due in the following plan year, supplied by the user rather than inferred from names. Mandatory jobs rank first. High starts at 70, medium at 50. Reasons show component values, not causal explanations.

## Capacity

Usable hours = available hours × (1 − reserve), with 15% default reserve. Select mandatory work, then descending score with process ID as deterministic tie-break. Deduct per-job estimated effort. Mandatory work may cause negative remaining hours, reported explicitly as a shortfall. This is greedy selection, not optimized staffing or scheduling. Without capacity use Top N plus all mandatory work and mark capacity unvalidated.

## Historical model

The target `selected_next_year` is an observed planning decision, not underlying need or finding severity. Unknown labels remain missing. History must precede the current snapshot. At least 80 labeled rows and three years are needed. The latest labeled historical year is held out; training requires 50 rows, test 10, with both classes in each.

Median imputation, scaling and logistic regression are fit on training only. Report ROC AUC, average precision, Brier score and prevalence. Refit on historical rows for current predictions. No model score enters the expert index, and there is no production acceptance gate, calibration validation, persistence or deployment.

Past selection can encode institutional preferences and selection bias. Unaudited processes cannot be labeled as having no findings in a future adverse-outcome model. One temporal holdout is not comprehensive validation.

Synthetic labels follow a probabilistic rule involving risk and coverage. Event counts are generated separately. Demonstration metrics verify the pipeline, not audit effectiveness or generalization to real data.
