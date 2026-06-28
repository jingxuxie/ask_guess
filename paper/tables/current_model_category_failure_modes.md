# Current-Model Category Failure Modes

This no-API analysis uses cached 100-episode stratified result files. The figure intentionally compares plain prompted Ask-Needed against ECU; the CoT column is included as context because GPT-5.5 private reasoning closes some category gaps on this subset.

## Summary

- gpt-4.1-mini: largest plain Ask-Needed gap is Risk (ECU - Ask-Needed 0.958), with under-asks behavior; missed=0.850, unnecessary=0.000.
- gpt-5.4-mini: largest plain Ask-Needed gap is Preference (ECU - Ask-Needed 0.193), with under-asks behavior; missed=0.375, unnecessary=0.000.
- gpt-5.5: largest plain Ask-Needed gap is Risk (ECU - Ask-Needed 0.767), with under-asks behavior; missed=0.650, unnecessary=0.000.
- Across these model/category cells, ECU's maximum missed and unnecessary clarification rates are 0.000 and 0.000.

## Category Table
| Model | Category | N | Ask utility | CoT utility | ECU utility | ECU - Ask | Ask rate | Oracle ask | Ask missed | Ask unnecessary | ECU missed | ECU unnecessary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4.1-mini | Context | 20 | 0.993 | 0.993 | 1.000 | 0.007 | 0.050 | 0.000 | 0.000 | 0.050 | 0.000 | 0.000 |
| gpt-4.1-mini | Preference | 20 | 0.400 | 0.598 | 0.980 | 0.580 | 0.000 | 0.400 | 1.000 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | Equivalent | 20 | 0.920 | 0.915 | 1.000 | 0.080 | 0.800 | 0.000 | 0.000 | 0.800 | 0.000 | 0.000 |
| gpt-4.1-mini | Referential | 20 | 0.857 | 0.855 | 0.950 | 0.093 | 0.850 | 1.000 | 0.150 | 0.000 | 0.000 | 0.000 |
| gpt-4.1-mini | Risk | 20 | -0.008 | -0.200 | 0.950 | 0.958 | 0.150 | 1.000 | 0.850 | 0.000 | 0.000 | 0.000 |
| gpt-5.4-mini | Context | 20 | 0.948 | 0.932 | 1.000 | 0.052 | 0.350 | 0.000 | 0.000 | 0.350 | 0.000 | 0.000 |
| gpt-5.4-mini | Preference | 20 | 0.787 | 0.980 | 0.980 | 0.193 | 0.250 | 0.400 | 0.375 | 0.000 | 0.000 | 0.000 |
| gpt-5.4-mini | Equivalent | 20 | 0.900 | 0.900 | 1.000 | 0.100 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| gpt-5.4-mini | Referential | 20 | 0.950 | 0.950 | 0.950 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gpt-5.4-mini | Risk | 20 | 0.757 | 0.557 | 0.950 | 0.193 | 0.850 | 1.000 | 0.150 | 0.000 | 0.000 | 0.000 |
| gpt-5.5 | Context | 20 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gpt-5.5 | Preference | 20 | 0.980 | 0.980 | 0.980 | 0.000 | 0.400 | 0.400 | 0.000 | 0.000 | 0.000 | 0.000 |
| gpt-5.5 | Equivalent | 20 | 0.990 | 1.000 | 1.000 | 0.010 | 0.100 | 0.000 | 0.000 | 0.100 | 0.000 | 0.000 |
| gpt-5.5 | Referential | 20 | 0.950 | 0.950 | 0.950 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| gpt-5.5 | Risk | 20 | 0.182 | 0.950 | 0.950 | 0.767 | 0.350 | 1.000 | 0.650 | 0.000 | 0.000 | 0.000 |
