# Held-Out Ambiguity-Mix Shift

This offline diagnostic trains and tunes on referential, context-resolved, and equivalent-outcome episodes, then evaluates transfer to risk-sensitive and preference/social episodes. It is a no-API robustness check for category-shift sensitivity, not a substitute for a broad API model sweep.

## Split and Category Coverage

| Split | Category | Episodes |
| --- | --- | --- |
| dev | context_resolved | 60 |
| dev | equivalent_outcome | 60 |
| dev | referential | 60 |
| ood_ambiguity_mix | preference_social | 100 |
| ood_ambiguity_mix | risk_sensitive | 100 |
| test | context_resolved | 100 |
| test | equivalent_outcome | 100 |
| test | referential | 100 |
| train | context_resolved | 200 |
| train | equivalent_outcome | 200 |
| train | referential | 200 |

## Main Results

| Split | Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ood_ambiguity_mix | direct_act | 200 | 0.540 | [0.380, 0.690] | 0.840 | 0.000 | 1.000 | 0.000 |
| ood_ambiguity_mix | ask_always | 200 | 0.950 | [0.950, 0.950] | 1.000 | 1.000 | 0.000 | 1.000 |
| ood_ambiguity_mix | raw_ambiguity | 200 | 0.950 | [0.950, 0.950] | 1.000 | 1.000 | 0.000 | 1.000 |
| ood_ambiguity_mix | prompted_heuristic | 200 | 0.962 | [0.960, 0.966] | 1.000 | 0.750 | 0.000 | 0.000 |
| ood_ambiguity_mix | ecu | 200 | 0.962 | [0.960, 0.966] | 1.000 | 0.750 | 0.000 | 0.000 |
| ood_ambiguity_mix | ecu_threshold | 200 | 0.950 | [0.950, 0.950] | 1.000 | 1.000 | 0.000 | 1.000 |
| ood_ambiguity_mix | learned_controller | 200 | 0.950 | [0.950, 0.950] | 1.000 | 1.000 | 0.000 | 1.000 |
| test | direct_act | 300 | 0.693 | [0.611, 0.769] | 0.840 | 0.000 | 1.000 | 0.000 |
| test | ask_always | 300 | 0.900 | [0.895, 0.905] | 1.000 | 1.000 | 0.000 | 1.000 |
| test | raw_ambiguity | 300 | 0.900 | [0.895, 0.905] | 1.000 | 1.000 | 0.000 | 1.000 |
| test | prompted_heuristic | 300 | 0.930 | [0.911, 0.945] | 0.983 | 0.667 | 0.000 | 0.500 |
| test | ecu | 300 | 0.963 | [0.946, 0.979] | 0.983 | 0.333 | 0.000 | 0.000 |
| test | ecu_threshold | 300 | 0.963 | [0.946, 0.979] | 0.983 | 0.333 | 0.000 | 0.000 |
| test | learned_controller | 300 | 0.963 | [0.946, 0.979] | 0.983 | 0.333 | 0.000 | 0.000 |

## Held-Out Deltas

| Method | Seen-test utility | Held-out utility | Held-out - seen | Seen success | Held-out success | Seen ask | Held-out ask |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prompted_heuristic | 0.930 | 0.962 | 0.032 | 0.983 | 1.000 | 0.667 | 0.750 |
| ecu | 0.963 | 0.962 | -0.001 | 0.983 | 1.000 | 0.333 | 0.750 |
| ecu_threshold | 0.963 | 0.950 | -0.013 | 0.983 | 1.000 | 0.333 | 1.000 |
| learned_controller | 0.963 | 0.950 | -0.013 | 0.983 | 1.000 | 0.333 | 1.000 |

## Category Breakdown

| Split | Category | Method | N | Net utility | Success | Ask rate | Oracle ask |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ood_ambiguity_mix | preference_social | prompted_heuristic | 100 | 0.975 | 1.000 | 0.500 | 0.500 |
| ood_ambiguity_mix | preference_social | ecu | 100 | 0.975 | 1.000 | 0.500 | 0.500 |
| ood_ambiguity_mix | preference_social | ecu_threshold | 100 | 0.950 | 1.000 | 1.000 | 0.500 |
| ood_ambiguity_mix | preference_social | learned_controller | 100 | 0.950 | 1.000 | 1.000 | 0.500 |
| ood_ambiguity_mix | risk_sensitive | prompted_heuristic | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| ood_ambiguity_mix | risk_sensitive | ecu | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| ood_ambiguity_mix | risk_sensitive | ecu_threshold | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| ood_ambiguity_mix | risk_sensitive | learned_controller | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| test | context_resolved | prompted_heuristic | 100 | 0.940 | 0.950 | 0.000 | 0.000 |
| test | context_resolved | ecu | 100 | 0.940 | 0.950 | 0.000 | 0.000 |
| test | context_resolved | ecu_threshold | 100 | 0.940 | 0.950 | 0.000 | 0.000 |
| test | context_resolved | learned_controller | 100 | 0.940 | 0.950 | 0.000 | 0.000 |
| test | equivalent_outcome | prompted_heuristic | 100 | 0.900 | 1.000 | 1.000 | 0.000 |
| test | equivalent_outcome | ecu | 100 | 1.000 | 1.000 | 0.000 | 0.000 |
| test | equivalent_outcome | ecu_threshold | 100 | 1.000 | 1.000 | 0.000 | 0.000 |
| test | equivalent_outcome | learned_controller | 100 | 1.000 | 1.000 | 0.000 | 0.000 |
| test | referential | prompted_heuristic | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| test | referential | ecu | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| test | referential | ecu_threshold | 100 | 0.950 | 1.000 | 1.000 | 1.000 |
| test | referential | learned_controller | 100 | 0.950 | 1.000 | 1.000 | 1.000 |

## Interpretation

- `prompted_heuristic`: seen utility 0.930, held-out utility 0.962, held-out ask rate 0.750.
- `ecu`: seen utility 0.963, held-out utility 0.962, held-out ask rate 0.750.
- `ecu_threshold`: seen utility 0.963, held-out utility 0.950, held-out ask rate 1.000.
- `learned_controller`: seen utility 0.963, held-out utility 0.950, held-out ask rate 1.000.
