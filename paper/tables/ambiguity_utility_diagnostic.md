# Ambiguity Is Not Enough Diagnostic

This no-API diagnostic tests the paper thesis that clarification should be optimized as situated utility, not as raw ambiguity detection.
The uncertainty-only controller is trained on train episodes and tuned on dev using only candidate count, top prior, and prior entropy. It omits context-resolution, success-equivalence, risk, cost, and ECU-margin features.

## Surface Ambiguity vs Oracle Ask

| Split | Episodes | Surface ambiguous | Oracle ask among ambiguous | Oracle act among ambiguous |
| --- | --- | --- | --- | --- |
| train | 600 | 1.000 | 0.500 | 0.500 |
| dev | 200 | 1.000 | 0.500 | 0.500 |
| test | 400 | 1.000 | 0.500 | 0.500 |
| ood_test | 200 | 1.000 | 0.500 | 0.500 |

On the test split, 400/400 episodes have multiple candidate interpretations, but 200 of those are oracle-act cases and 200 are oracle-ask cases.

## Test Category Dissociation

| Category | N | Surface ambiguous | Oracle ask | Mean top prior | Mean normalized entropy |
| --- | --- | --- | --- | --- | --- |
| context_resolved | 80 | 1.000 | 0.000 | 0.970 | 0.194 |
| equivalent_outcome | 80 | 1.000 | 0.000 | 0.360 | 0.998 |
| preference_social | 80 | 1.000 | 0.500 | 0.770 | 0.537 |
| referential | 80 | 1.000 | 1.000 | 0.530 | 0.997 |
| risk_sensitive | 80 | 1.000 | 1.000 | 0.799 | 0.720 |

## Matched Candidate-Count Slices

| Candidate count | Oracle decision | N | Categories |
| --- | --- | --- | --- |
| 2 | act | 120 | context_resolved: 80, preference_social: 40 |
| 2 | ask | 200 | preference_social: 40, referential: 80, risk_sensitive: 80 |
| 3 | act | 80 | equivalent_outcome: 80 |

## Policy Comparison

| Policy | N | Net utility | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- |
| test surface_ambiguity | 400 | 0.920 | 1.000 | 1.000 | 0.000 | 1.000 |
| test uncertainty_only_controller | 400 | 0.900 | 0.978 | 0.665 | 0.070 | 0.400 |
| test prompted_heuristic | 400 | 0.938 | 0.988 | 0.700 | 0.000 | 0.400 |
| test ecu | 400 | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| test learned_controller | 400 | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| ood_test surface_ambiguity | 200 | 0.920 | 1.000 | 1.000 | 0.000 | 1.000 |
| ood_test uncertainty_only_controller | 200 | 0.937 | 0.995 | 0.655 | 0.090 | 0.400 |
| ood_test prompted_heuristic | 200 | 0.955 | 1.000 | 0.700 | 0.000 | 0.400 |
| ood_test ecu | 200 | 0.975 | 1.000 | 0.500 | 0.000 | 0.000 |
| ood_test learned_controller | 200 | 0.975 | 1.000 | 0.500 | 0.000 | 0.000 |

## Uncertainty-Only Controller

- Tuned probability threshold: 0.53

| Feature | Weight |
| --- | --- |
| bias | -0.7966 |
| num_candidates | -3.0525 |
| top_prior | 0.4173 |
| normalized_prior_entropy | 3.1551 |

## Interpretation

- Raw surface ambiguity asks on all canonical test episodes, so it cannot distinguish ambiguity that is harmless or context-resolved from ambiguity that is worth interrupting for.
- A learned uncertainty-only controller is useful but still lacks the explicit utility ingredients needed to eliminate unnecessary clarification.
- ECU and the full learned controller use value-of-information features, so they preserve success while avoiding both missed and unnecessary clarification on the full offline test split.
