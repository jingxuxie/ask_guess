# Scene-Format Robustness

This report compares baseline JSON prompts against a perturbed scene serialization on shared episode-policy pairs.

## Policy Summary

| Policy | Shared N | Baseline utility | Perturbed utility | Delta | Baseline ask | Perturbed ask | Ask/act changed | First output changed | Perturbed missed | Perturbed unnecessary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| api_ask_needed | 100 | 0.868 | 0.788 | -0.080 | 0.690 | 0.670 | 0.080 | 0.080 | 0.167 | 0.519 |
| api_ask_needed_cot | 100 | 0.864 | 0.904 | 0.040 | 0.740 | 0.720 | 0.100 | 0.100 | 0.104 | 0.558 |
| api_direct_act | 100 | 0.380 | 0.420 | 0.040 | 0.000 | 0.000 | 0.000 | 0.060 | 1.000 | 0.000 |
| api_ecu | 100 | 0.976 | 0.975 | -0.001 | 0.480 | 0.490 | 0.010 | 0.010 | 0.000 | 0.019 |


## Category Summary

| Category | Policy | Shared N | Baseline utility | Perturbed utility | Ask/act changed | Perturbed missed | Perturbed unnecessary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| context_resolved | api_ask_needed | 20 | 0.948 | 0.932 | 0.100 | 0.000 | 0.450 |
| context_resolved | api_ask_needed_cot | 20 | 0.932 | 0.925 | 0.250 | 0.000 | 0.500 |
| context_resolved | api_direct_act | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| context_resolved | api_ecu | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| equivalent_outcome | api_ask_needed | 20 | 0.900 | 0.910 | 0.100 | 0.000 | 0.900 |
| equivalent_outcome | api_ask_needed_cot | 20 | 0.900 | 0.905 | 0.050 | 0.000 | 0.950 |
| equivalent_outcome | api_direct_act | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| equivalent_outcome | api_ecu | 20 | 1.000 | 0.995 | 0.050 | 0.000 | 0.050 |
| preference_social | api_ask_needed | 20 | 0.787 | 0.590 | 0.150 | 0.500 | 0.000 |
| preference_social | api_ask_needed_cot | 20 | 0.980 | 0.980 | 0.000 | 0.000 | 0.000 |
| preference_social | api_direct_act | 20 | 0.400 | 0.500 | 0.000 | 1.000 | 0.000 |
| preference_social | api_ecu | 20 | 0.980 | 0.980 | 0.000 | 0.000 | 0.000 |
| referential | api_ask_needed | 20 | 0.950 | 0.950 | 0.000 | 0.000 | 0.000 |
| referential | api_ask_needed_cot | 20 | 0.950 | 0.950 | 0.000 | 0.000 | 0.000 |
| referential | api_direct_act | 20 | -0.300 | -0.200 | 0.000 | 1.000 | 0.000 |
| referential | api_ecu | 20 | 0.950 | 0.950 | 0.000 | 0.000 | 0.000 |
| risk_sensitive | api_ask_needed | 20 | 0.757 | 0.560 | 0.050 | 0.200 | 0.000 |
| risk_sensitive | api_ask_needed_cot | 20 | 0.557 | 0.762 | 0.200 | 0.250 | 0.000 |
| risk_sensitive | api_direct_act | 20 | -0.200 | -0.200 | 0.000 | 1.000 | 0.000 |
| risk_sensitive | api_ecu | 20 | 0.950 | 0.950 | 0.000 | 0.000 | 0.000 |
