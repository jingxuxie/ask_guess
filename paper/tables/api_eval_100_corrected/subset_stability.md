# API Subset Stability

This no-API diagnostic checks whether the final 100-episode GPT-4.1-mini API advantage is concentrated in one category or one episode. It uses the cached canonical API result rows and paired rewards.

## Category Paired Deltas

| Category | N | ECU - AskNeeded | 95% paired CI | ECU - DirectAct | 95% paired CI |
| --- | --- | --- | --- | --- | --- |
| context_resolved | 20 | 0.008 | [0.000, 0.023] | 0.000 | [0.000, 0.000] |
| equivalent_outcome | 20 | 0.080 | [0.060, 0.095] | 0.000 | [0.000, 0.000] |
| preference_social | 20 | 0.580 | [0.190, 0.975] | 0.580 | [0.190, 0.975] |
| referential | 20 | 0.092 | [-0.010, 0.290] | 1.050 | [0.650, 1.450] |
| risk_sensitive | 20 | 0.958 | [0.350, 1.758] | 1.150 | [0.350, 1.950] |

## Leave-One-Category-Out Deltas

| Omitted category | Remaining N | ECU - AskNeeded | ECU - DirectAct |
| --- | --- | --- | --- |
| context_resolved | 80 | 0.427 | 0.695 |
| equivalent_outcome | 80 | 0.409 | 0.695 |
| preference_social | 80 | 0.284 | 0.550 |
| referential | 80 | 0.406 | 0.432 |
| risk_sensitive | 80 | 0.190 | 0.407 |

## Leave-One-Episode-Out Deltas

| Comparison | Leave-one runs | Min delta | Max delta | Positive runs |
| --- | --- | --- | --- | --- |
| api_ecu - api_ask_needed | 100 | 0.307 | 0.347 | 100 |
| api_ecu - api_direct_act | 100 | 0.522 | 0.562 | 100 |

## Stratified Bootstrap

| Comparison | N | Mean delta | Stratified 95% CI |
| --- | --- | --- | --- |
| api_ecu - api_ask_needed | 100 | 0.343 | [0.183, 0.541] |
| api_ecu - api_direct_act | 100 | 0.556 | [0.357, 0.756] |

## Interpretation

- ECU's paired advantage over Ask-Needed has a positive point estimate in every category and remains positive after omitting any single category.
- Leave-one-episode-out deltas remain positive for every omitted episode.
- This is a subset-stability diagnostic for the bounded API set, not a substitute for a larger paid API sweep.
