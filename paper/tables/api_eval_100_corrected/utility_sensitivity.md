# Cached API Utility Sensitivity

This no-API diagnostic re-scores the fixed GPT-4.1-mini outputs from the final 100-episode API evaluation under alternate ask and wrong-action costs. It does not rerun the model or change each policy's original ask/act decisions. Oracle ask labels are recomputed for each cost setting from the benchmark candidate intents.

## Ask-Cost Sweep

| Ask cost | Wrong cost | Method | N | Net utility | Success | Ask rate | Oracle ask | Missed clarif. | Unnecessary clarif. | ECU - method | 95% paired CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.01 | 1.00 | api_direct_act | 100 | 0.540 | 0.770 | 0.000 | 0.800 | 1.000 | 0.000 | 0.455 | [0.296, 0.634] |
| 0.01 | 1.00 | api_ask_needed | 100 | 0.756 | 0.880 | 0.370 | 0.800 | 0.738 | 0.800 | 0.239 | [0.120, 0.378] |
| 0.01 | 1.00 | api_ecu | 100 | 0.995 | 1.000 | 0.480 | 0.800 | 0.400 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.05 | 1.00 | api_direct_act | 100 | 0.540 | 0.770 | 0.000 | 0.680 | 1.000 | 0.000 | 0.436 | [0.279, 0.611] |
| 0.05 | 1.00 | api_ask_needed | 100 | 0.741 | 0.880 | 0.370 | 0.680 | 0.691 | 0.500 | 0.234 | [0.118, 0.372] |
| 0.05 | 1.00 | api_ecu | 100 | 0.976 | 1.000 | 0.480 | 0.680 | 0.294 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.10 | 1.00 | api_direct_act | 100 | 0.540 | 0.770 | 0.000 | 0.480 | 1.000 | 0.000 | 0.412 | [0.259, 0.583] |
| 0.10 | 1.00 | api_ask_needed | 100 | 0.723 | 0.880 | 0.370 | 0.480 | 0.583 | 0.327 | 0.229 | [0.117, 0.364] |
| 0.10 | 1.00 | api_ecu | 100 | 0.952 | 1.000 | 0.480 | 0.480 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.20 | 1.00 | api_direct_act | 100 | 0.540 | 0.770 | 0.000 | 0.480 | 1.000 | 0.000 | 0.364 | [0.218, 0.528] |
| 0.20 | 1.00 | api_ask_needed | 100 | 0.686 | 0.880 | 0.370 | 0.480 | 0.583 | 0.327 | 0.218 | [0.112, 0.346] |
| 0.20 | 1.00 | api_ecu | 100 | 0.904 | 1.000 | 0.480 | 0.480 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.35 | 1.00 | api_direct_act | 100 | 0.540 | 0.770 | 0.000 | 0.460 | 1.000 | 0.000 | 0.292 | [0.151, 0.444] |
| 0.35 | 1.00 | api_ask_needed | 100 | 0.631 | 0.880 | 0.370 | 0.460 | 0.565 | 0.315 | 0.201 | [0.098, 0.326] |
| 0.35 | 1.00 | api_ecu | 100 | 0.832 | 1.000 | 0.480 | 0.460 | 0.000 | 0.037 | 0.000 | [0.000, 0.000] |

## Wrong-Action Cost Sweep

| Ask cost | Wrong cost | Method | N | Net utility | Success | Ask rate | Oracle ask | Missed clarif. | Unnecessary clarif. | ECU - method | 95% paired CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 0.20 | api_direct_act | 100 | 0.724 | 0.770 | 0.000 | 0.480 | 1.000 | 0.000 | 0.252 | [0.159, 0.355] |
| 0.05 | 0.20 | api_ask_needed | 100 | 0.838 | 0.880 | 0.370 | 0.480 | 0.583 | 0.327 | 0.138 | [0.070, 0.220] |
| 0.05 | 0.20 | api_ecu | 100 | 0.976 | 1.000 | 0.480 | 0.480 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.05 | 0.50 | api_direct_act | 100 | 0.655 | 0.770 | 0.000 | 0.480 | 1.000 | 0.000 | 0.321 | [0.204, 0.451] |
| 0.05 | 0.50 | api_ask_needed | 100 | 0.801 | 0.880 | 0.370 | 0.480 | 0.583 | 0.327 | 0.174 | [0.088, 0.277] |
| 0.05 | 0.50 | api_ecu | 100 | 0.976 | 1.000 | 0.480 | 0.480 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.05 | 1.00 | api_direct_act | 100 | 0.540 | 0.770 | 0.000 | 0.680 | 1.000 | 0.000 | 0.436 | [0.279, 0.611] |
| 0.05 | 1.00 | api_ask_needed | 100 | 0.741 | 0.880 | 0.370 | 0.680 | 0.691 | 0.500 | 0.234 | [0.118, 0.372] |
| 0.05 | 1.00 | api_ecu | 100 | 0.976 | 1.000 | 0.480 | 0.680 | 0.294 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.05 | 2.00 | api_direct_act | 100 | 0.310 | 0.770 | 0.000 | 0.680 | 1.000 | 0.000 | 0.666 | [0.429, 0.931] |
| 0.05 | 2.00 | api_ask_needed | 100 | 0.621 | 0.880 | 0.370 | 0.680 | 0.691 | 0.500 | 0.355 | [0.179, 0.562] |
| 0.05 | 2.00 | api_ecu | 100 | 0.976 | 1.000 | 0.480 | 0.680 | 0.294 | 0.000 | 0.000 | [0.000, 0.000] |
| 0.05 | 3.00 | api_direct_act | 100 | 0.080 | 0.770 | 0.000 | 0.680 | 1.000 | 0.000 | 0.896 | [0.580, 1.252] |
| 0.05 | 3.00 | api_ask_needed | 100 | 0.501 | 0.880 | 0.370 | 0.680 | 0.691 | 0.500 | 0.475 | [0.239, 0.752] |
| 0.05 | 3.00 | api_ecu | 100 | 0.976 | 1.000 | 0.480 | 0.680 | 0.294 | 0.000 | 0.000 | [0.000, 0.000] |

## Paired Delta Summary

Positive values favor API ECU under the counterfactual scoring.

### Ask-Cost Sweep

| Ask cost | Wrong cost | ECU - AskNeeded | 95% paired CI | ECU - DirectAct | 95% paired CI |
| --- | --- | --- | --- | --- | --- |
| 0.01 | 1.00 | 0.239 | [0.120, 0.378] | 0.455 | [0.296, 0.634] |
| 0.05 | 1.00 | 0.234 | [0.118, 0.372] | 0.436 | [0.279, 0.611] |
| 0.10 | 1.00 | 0.229 | [0.117, 0.364] | 0.412 | [0.259, 0.583] |
| 0.20 | 1.00 | 0.218 | [0.112, 0.346] | 0.364 | [0.218, 0.528] |
| 0.35 | 1.00 | 0.201 | [0.098, 0.326] | 0.292 | [0.151, 0.444] |

### Wrong-Action Cost Sweep

| Ask cost | Wrong cost | ECU - AskNeeded | 95% paired CI | ECU - DirectAct | 95% paired CI |
| --- | --- | --- | --- | --- | --- |
| 0.05 | 0.20 | 0.138 | [0.070, 0.220] | 0.252 | [0.159, 0.355] |
| 0.05 | 0.50 | 0.174 | [0.088, 0.277] | 0.321 | [0.204, 0.451] |
| 0.05 | 1.00 | 0.234 | [0.118, 0.372] | 0.436 | [0.279, 0.611] |
| 0.05 | 2.00 | 0.355 | [0.179, 0.562] | 0.666 | [0.429, 0.931] |
| 0.05 | 3.00 | 0.475 | [0.239, 0.752] | 0.896 | [0.580, 1.252] |

## Interpretation

- ECU's observed API outputs retain a positive paired utility delta over prompted Ask-Needed across the tested ask-cost and wrong-action-cost settings; all paired bootstrap lower bounds are above zero in this grid.
- This is a fixed-output sensitivity check. A fully adaptive policy would recompute its ask decision when costs change, as the offline cost-sensitivity analysis does.
- The diagnostic supports that the main API result is not an artifact of one narrow reward parameterization, while preserving the paper's stronger claim for the original benchmark costs.
