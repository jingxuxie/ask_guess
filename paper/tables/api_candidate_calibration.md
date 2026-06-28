# API ECU Candidate-Probability Calibration

This no-API diagnostic inspects cached `api_ecu` rows. It maps model-generated candidate target IDs back to benchmark success classes, compares model probabilities with benchmark priors and hidden success classes, and compares model-derived utility margins with oracle utility margins.

## Run Summary

| Run | N | Top matches benchmark | Top matches hidden | Prior TV | Mean hidden prob. | Brier | Top-prob. ECE | Margin Pearson | Margin Spearman | Ask/oracle agree | Unknown prob. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4.1-mini | 100 | 0.970 | 0.770 | 0.057 | 0.752 | 0.252 | 0.101 | 0.948 | 0.741 | 1.000 | 0.000 |
| gpt-5.4-mini-json | 100 | 0.970 | 0.770 | 0.035 | 0.772 | 0.238 | 0.088 | 0.985 | 0.912 | 1.000 | 0.000 |
| gpt-5.5 | 100 | 0.970 | 0.770 | 0.019 | 0.772 | 0.233 | 0.065 | 0.991 | 0.954 | 1.000 | 0.000 |
| gpt-5.4-mini-shuffled | 100 | 0.970 | 0.770 | 0.032 | 0.764 | 0.239 | 0.082 | 0.988 | 0.858 | 1.000 | 0.000 |
| gpt-5.4-mini-natural-language | 100 | 0.970 | 0.770 | 0.020 | 0.770 | 0.237 | 0.069 | 0.976 | 0.959 | 0.990 | 0.000 |

## Top-Probability Calibration (gpt-4.1-mini)

| Top-prob. bin | N | Mean top prob. | Hidden accuracy | Benchmark top match | Prior TV | Mean hidden prob. | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.50-0.60 | 3 | 0.547 | 0.333 | 1.000 | 0.013 | 0.487 | 0.531 |
| 0.60-0.70 | 17 | 0.600 | 0.353 | 0.882 | 0.070 | 0.471 | 0.579 |
| 0.70-0.80 | 28 | 0.746 | 0.643 | 1.000 | 0.069 | 0.574 | 0.475 |
| 0.80-0.90 | 2 | 0.850 | 1.000 | 1.000 | 0.120 | 0.850 | 0.045 |
| >=0.90 | 50 | 0.959 | 1.000 | 0.980 | 0.045 | 0.959 | 0.007 |

## Ask/Oracle Agreement by Oracle-Margin Size (gpt-4.1-mini)

| Oracle-margin abs. bin | N | Mean oracle margin | Mean model margin | Ask/oracle agree | Top benchmark match | Prior TV | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| <0.05 | 12 | -0.030 | 0.050 | 1.000 | 0.917 | 0.108 | 0.006 |
| 0.05-0.20 | 40 | -0.107 | -0.072 | 1.000 | 1.000 | 0.030 | 0.009 |
| >=0.50 | 48 | 0.837 | 0.783 | 1.000 | 0.958 | 0.066 | 0.515 |

## Category Breakdown (gpt-4.1-mini)

| Category | N | Top benchmark match | Top hidden match | Prior TV | Mean hidden prob. | Brier | Ask/oracle agree |
| --- | --- | --- | --- | --- | --- | --- | --- |
| context_resolved | 20 | 1.000 | 1.000 | 0.060 | 0.912 | 0.018 | 1.000 |
| equivalent_outcome | 20 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| preference_social | 20 | 0.950 | 0.700 | 0.100 | 0.740 | 0.282 | 1.000 |
| referential | 20 | 0.900 | 0.450 | 0.091 | 0.503 | 0.525 | 1.000 |
| risk_sensitive | 20 | 1.000 | 0.700 | 0.033 | 0.604 | 0.433 | 1.000 |

## Interpretation

- The analysis uses shipped cached API debug fields and makes no model calls.
- Top-probability calibration is measured against the sampled hidden success class, so it is noisy on 100-row subsets.
- The margin-correlation rows test whether model-derived candidate probabilities preserve the ordering of utility-relevant uncertainty, not whether they are perfectly calibrated probabilities.
