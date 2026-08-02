# Deterministic analytics methodology

All bundled operational records are synthetic demonstration data. Analytics are historical evidence summaries, not trained predictions.

## Maintenance recurrence-risk score

Version: `maintenance-risk-v1.0.0`.

| Component | Weight | Normalization |
|---|---:|---|
| Dominant failure recurrence | 25 | `(dominant count - 1) / 3`, capped at 1 |
| Recent incidents | 20 | Mutually exclusive 0–90, 91–180 and 181–365 day buckets weighted 1.0, 0.6 and 0.3; divided by 3 and capped at 1 |
| Severity | 20 | Mean ordinal severity (`LOW=1` through `CRITICAL=4`) / 4 |
| Downtime burden | 15 | Equipment mean downtime / current dataset P90 downtime, capped at 1 |
| Repeated root cause | 10 | `(dominant root-cause count - 1) / 3`, capped at 1 |
| Shrinking intervals | 10 | 1 only when the latest observed interval is at least 10% shorter than the mean of earlier intervals |

The reference date is the latest date in the dataset, not wall-clock time. Risk bands are LOW `<30`, MONITOR `30–54.99`, HIGH `55–74.99`, CRITICAL `>=75`. Confidence combines record volume, date coverage, root-cause presence and field completeness. No failure date or fixed component is predicted.

## Compliance evidence-gap assessment

Version: `compliance-gap-v1.0.0`. Percentage is `COMPLIANT records / requirements checked × 100`. Counts and corrective actions are derived from the six normalized synthetic OISD-118 rows. Critical actions sort before gaps. This is not legal certification; no Factory Act, DGMS or PESO source corpus is bundled.

## Failure patterns

Version: `failure-pattern-v1.0.0`. Work orders and recovered incident-history records are normalized into one evidence model. A recurring equipment/failure combination or precursor requires at least two records. A high-downtime cluster requires at least 20 work-order downtime hours. Graph edges retain evidence IDs and source types. Correlation does not establish causality.

## Reproducibility

Every analysis returns a deterministic `analysis_id` derived from analysis type, normalized inputs, dataset SHA-256 and methodology version. `generated_at` is informational and is excluded from identity.
