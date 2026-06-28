# Utility-Margin Calibration

Bins are defined by the oracle expected-utility margin `EU(ask) - EU(act)`: `Act preferred` is <= -0.05, `Near tie` is (-0.05, 0.05], and `Ask preferred` is > 0.05.

## Takeaways

- `test`: ECU asks on 1.000 of ask-preferred episodes and 0.000 of act-preferred episodes; Ask-Needed asks on 0.417 and 0.425, respectively.

## Calibration Table

| Split | Utility-margin bin | Method | N | Mean EU ask-act | Oracle ask | Ask rate | Net utility | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | Act preferred | api_direct_act | 40 | -0.107 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| test | Act preferred | api_ask_needed | 40 | -0.107 | 0.000 | 0.425 | 0.956 | 0.000 | 0.425 |
| test | Act preferred | api_ecu | 40 | -0.107 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| test | Near tie | api_direct_act | 12 | -0.030 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| test | Near tie | api_ask_needed | 12 | -0.030 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| test | Near tie | api_ecu | 12 | -0.030 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| test | Ask preferred | api_direct_act | 48 | 0.837 | 1.000 | 0.000 | -0.208 | 1.000 | 0.000 |
| test | Ask preferred | api_ask_needed | 48 | 0.837 | 1.000 | 0.417 | 0.271 | 0.583 | 0.000 |
| test | Ask preferred | api_ecu | 48 | 0.837 | 1.000 | 1.000 | 0.950 | 0.000 | 0.000 |
