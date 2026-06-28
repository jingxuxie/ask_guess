# API ECU Candidate-Margin Analysis

This no-API diagnostic inspects cached GPT-4.1-mini API ECU rows. The API ECU first asks the model for candidate interpretations and probabilities, computes a utility margin from those model-derived candidates, then asks only when the margin clears the configured threshold unless the model also marks the instruction as sufficiently context-resolved.

## Summary

| Quantity | Value | Definition |
| --- | --- | --- |
| API ECU rows | 100 | cached rows with `policy == api_ecu` |
| Rows with API advantage | 100 | debug field present |
| Mean API advantage | 0.353 | model-derived candidate utility margin |
| Configured API ECU margin | 0.075 | ask when advantage is greater than this, unless context override applies |
| Margin-positive rate | 0.490 | `api_advantage > api_ecu_margin` |
| Context-override rate | 0.010 | margin-positive but context-resolved enough to act |
| Oracle ask rate | 0.480 | benchmark label |
| Final ask rate | 0.480 | actual API ECU first-turn decision |
| Margin/oracle agreement | 0.990 | before context override |
| Final ask/oracle agreement | 1.000 | after margin rule and context override |

## By API Candidate-Margin Bin

| API margin bin | N | Mean API advantage | Oracle ask | Final ask | Context override | Success | Net utility |
| --- | --- | --- | --- | --- | --- | --- | --- |
| margin <= threshold | 51 | -0.048 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| margin > threshold | 49 | 0.770 | 0.980 | 0.980 | 0.020 | 1.000 | 0.951 |

## By Ambiguity Category

| Category | N | Mean API advantage | Margin positive | Context override | Oracle ask | Final ask | Success | Net utility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| context_resolved | 20 | -0.045 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| equivalent_outcome | 20 | -0.100 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 |
| preference_social | 20 | 0.300 | 0.450 | 0.050 | 0.400 | 0.400 | 1.000 | 0.980 |
| referential | 20 | 0.716 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.950 |
| risk_sensitive | 20 | 0.894 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | 0.950 |

## Margin/Oracle Disagreements

| Episode | Category | API advantage | Margin positive | Context override | Oracle ask | Final ask | Reward |
| --- | --- | --- | --- | --- | --- | --- | --- |
| test_preference_000264 | preference_social | 0.150 | True | True | False | False | 1.000 |

## Interpretation

- The diagnostic uses cached API debug fields and does not make new model calls.
- It tests whether the API-side candidate utility margin aligns with the benchmark ask labels on the final 100-episode API subset.
- It should be read as an internal calibration check for the API ECU pipeline, not as an independent benchmark result.
