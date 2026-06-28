# Robustness Breakdown

The OOD split uses the same diagnostic categories with shifted object types where the generator supports them. This table is offline-only and uses the frozen deterministic results.

## Headline OOD Deltas

- `prompted_heuristic`: test 0.938, OOD 0.955, delta 0.017
- `ecu`: test 0.958, OOD 0.975, delta 0.017
- `learned_controller`: test 0.958, OOD 0.975, delta 0.017

## Split-Level Deltas

| Method | Test utility | OOD utility | OOD - test | Test success | OOD success | Test ask | OOD ask |
| --- | --- | --- | --- | --- | --- | --- | --- |
| direct_act | 0.498 | 0.550 | 0.052 | 0.792 | 0.825 | 0.000 | 0.000 |
| ask_always | 0.920 | 0.920 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| raw_ambiguity | 0.920 | 0.920 | 0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| prompted_heuristic | 0.938 | 0.955 | 0.017 | 0.988 | 1.000 | 0.700 | 0.700 |
| ecu | 0.958 | 0.975 | 0.017 | 0.988 | 1.000 | 0.500 | 0.500 |
| ecu_threshold | 0.958 | 0.975 | 0.017 | 0.988 | 1.000 | 0.500 | 0.500 |
| learned_controller | 0.958 | 0.975 | 0.017 | 0.988 | 1.000 | 0.500 | 0.500 |

## Category-Level Deltas

| Category | Method | Test N | OOD N | Test utility | OOD utility | OOD - test |
| --- | --- | --- | --- | --- | --- | --- |
| context_resolved | direct_act | 80 | 40 | 0.940 | 1.000 | 0.060 |
| context_resolved | prompted_heuristic | 80 | 40 | 0.940 | 1.000 | 0.060 |
| context_resolved | ecu | 80 | 40 | 0.940 | 1.000 | 0.060 |
| context_resolved | learned_controller | 80 | 40 | 0.940 | 1.000 | 0.060 |
| equivalent_outcome | direct_act | 80 | 40 | 1.000 | 1.000 | 0.000 |
| equivalent_outcome | prompted_heuristic | 80 | 40 | 0.900 | 0.900 | 0.000 |
| equivalent_outcome | ecu | 80 | 40 | 1.000 | 1.000 | 0.000 |
| equivalent_outcome | learned_controller | 80 | 40 | 1.000 | 1.000 | 0.000 |
| preference_social | direct_act | 80 | 40 | 0.475 | 0.600 | 0.125 |
| preference_social | prompted_heuristic | 80 | 40 | 0.950 | 0.975 | 0.025 |
| preference_social | ecu | 80 | 40 | 0.950 | 0.975 | 0.025 |
| preference_social | learned_controller | 80 | 40 | 0.950 | 0.975 | 0.025 |
| referential | direct_act | 80 | 40 | 0.025 | 0.150 | 0.125 |
| referential | prompted_heuristic | 80 | 40 | 0.950 | 0.950 | 0.000 |
| referential | ecu | 80 | 40 | 0.950 | 0.950 | 0.000 |
| referential | learned_controller | 80 | 40 | 0.950 | 0.950 | 0.000 |
| risk_sensitive | direct_act | 80 | 40 | 0.050 | 0.000 | -0.050 |
| risk_sensitive | prompted_heuristic | 80 | 40 | 0.950 | 0.950 | 0.000 |
| risk_sensitive | ecu | 80 | 40 | 0.950 | 0.950 | 0.000 |
| risk_sensitive | learned_controller | 80 | 40 | 0.950 | 0.950 | 0.000 |

## OOD Held-Out Object Slice

| OOD slice | Method | N | Net utility | Success | Ask rate |
| --- | --- | --- | --- | --- | --- |
| held-out object | direct_act | 102 | 0.588 | 0.794 | 0.000 |
| held-out object | ask_always | 102 | 0.911 | 1.000 | 1.000 |
| held-out object | raw_ambiguity | 102 | 0.911 | 1.000 | 1.000 |
| held-out object | prompted_heuristic | 102 | 0.975 | 1.000 | 0.500 |
| held-out object | ecu | 102 | 0.975 | 1.000 | 0.500 |
| held-out object | ecu_threshold | 102 | 0.975 | 1.000 | 0.500 |
| held-out object | learned_controller | 102 | 0.975 | 1.000 | 0.500 |
| no held-out object | direct_act | 98 | 0.510 | 0.857 | 0.000 |
| no held-out object | ask_always | 98 | 0.930 | 1.000 | 1.000 |
| no held-out object | raw_ambiguity | 98 | 0.930 | 1.000 | 1.000 |
| no held-out object | prompted_heuristic | 98 | 0.934 | 1.000 | 0.908 |
| no held-out object | ecu | 98 | 0.975 | 1.000 | 0.500 |
| no held-out object | ecu_threshold | 98 | 0.975 | 1.000 | 0.500 |
| no held-out object | learned_controller | 98 | 0.975 | 1.000 | 0.500 |

## Object Type Coverage

| Object type | Test episodes | OOD episodes | Held out from train/dev/test pools |
| --- | --- | --- | --- |
| book | 52 | 0 | no |
| bowl | 28 | 0 | no |
| box | 64 | 11 | no |
| chair | 25 | 12 | no |
| charger | 0 | 22 | yes |
| cup | 47 | 10 | no |
| draft | 33 | 14 | no |
| file | 22 | 16 | no |
| folder | 86 | 27 | no |
| keys | 0 | 20 | yes |
| mug | 43 | 8 | no |
| notebook | 0 | 30 | yes |
| remote | 0 | 16 | yes |
| water_bottle | 0 | 14 | yes |
