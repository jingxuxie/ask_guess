# API ECU Decision Ablations

This no-API ablation replays the cached GPT-4.1-mini candidate interpretations from the final 100-episode API evaluation. It isolates the first-turn ask/act decision; when an ablated rule asks, the simulator answer is assumed to resolve the hidden intent, matching the benchmark interaction model.

Sanity check: current-rule replay matches actual API ECU ask decisions on 100/100 episodes and rewards on 100/100 episodes.

## Main Ablation

| Decision rule | Change | N | Net utility | Delta vs current | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Current rule replay | Guarded equivalence collapse, context override, margin 0.075. | 100 | 0.976 | 0.000 | 1.000 | 0.480 | 0.000 | 0.000 |
| No equivalence guard | Accept every model-declared equivalent-success flag. | 100 | 0.745 | -0.231 [-0.387, -0.096] | 0.890 | 0.300 | 0.375 | 0.000 |
| No equivalence collapse | Treat all model candidates as distinct success classes. | 100 | 0.956 | -0.020 [-0.028, -0.013] | 1.000 | 0.680 | 0.000 | 0.385 |
| No context override | Use guarded equivalence and margin, but ignore context-resolved flag. | 100 | 0.976 | -0.001 [-0.002, 0.000] | 1.000 | 0.490 | 0.000 | 0.019 |
| No margin/context dampening | Ask on any positive utility advantage without context override. | 100 | 0.968 | -0.009 [-0.015, -0.004] | 1.000 | 0.610 | 0.000 | 0.250 |

## Category Breakdown for Equivalence Ablations

| Category | Decision rule | N | Net utility | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| context_resolved | No equivalence guard | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| context_resolved | Current rule replay | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| context_resolved | No equivalence collapse | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| equivalent_outcome | No equivalence guard | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| equivalent_outcome | Current rule replay | 20 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| equivalent_outcome | No equivalence collapse | 20 | 0.900 | 1.000 | 1.000 | 0.000 | 1.000 |
| preference_social | No equivalence guard | 20 | 0.593 | 0.800 | 0.150 | 0.625 | 0.000 |
| preference_social | Current rule replay | 20 | 0.980 | 1.000 | 0.400 | 0.000 | 0.000 |
| preference_social | No equivalence collapse | 20 | 0.980 | 1.000 | 0.400 | 0.000 | 0.000 |
| referential | No equivalence guard | 20 | 0.372 | 0.700 | 0.550 | 0.450 | 0.000 |
| referential | Current rule replay | 20 | 0.950 | 1.000 | 1.000 | 0.000 | 0.000 |
| referential | No equivalence collapse | 20 | 0.950 | 1.000 | 1.000 | 0.000 | 0.000 |
| risk_sensitive | No equivalence guard | 20 | 0.760 | 0.950 | 0.800 | 0.200 | 0.000 |
| risk_sensitive | Current rule replay | 20 | 0.950 | 1.000 | 1.000 | 0.000 | 0.000 |
| risk_sensitive | No equivalence collapse | 20 | 0.950 | 1.000 | 1.000 | 0.000 | 0.000 |
