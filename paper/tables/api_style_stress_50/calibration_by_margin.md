# Utility-Margin Calibration

Bins are defined by the oracle expected-utility margin `EU(ask) - EU(act)`: `Act preferred` is <= -0.05, `Near tie` is (-0.05, 0.05], and `Ask preferred` is > 0.05.

## Takeaways

- `style_test`: ECU asks on 1.000 of ask-preferred episodes and 0.000 of act-preferred episodes; Ask-Needed asks on 0.522 and 0.350, respectively.

## Calibration Table

| Split | Utility-margin bin | Method | N | Mean EU ask-act | Oracle ask | Ask rate | Net utility | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| style_test | Act preferred | api_direct_act | 20 | -0.107 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| style_test | Act preferred | api_ask_needed | 20 | -0.107 | 0.000 | 0.350 | 0.965 | 0.000 | 0.350 |
| style_test | Act preferred | api_ecu | 20 | -0.107 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| style_test | Near tie | api_direct_act | 7 | -0.030 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| style_test | Near tie | api_ask_needed | 7 | -0.030 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| style_test | Near tie | api_ecu | 7 | -0.030 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| style_test | Ask preferred | api_direct_act | 23 | 0.831 | 1.000 | 0.000 | -0.478 | 1.000 | 0.000 |
| style_test | Ask preferred | api_ask_needed | 23 | 0.831 | 1.000 | 0.522 | 0.626 | 0.478 | 0.000 |
| style_test | Ask preferred | api_ecu | 23 | 0.831 | 1.000 | 1.000 | 0.950 | 0.000 | 0.000 |
