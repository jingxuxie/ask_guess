# Situated Contrast Analysis

This no-API diagnostic makes the paper's situated-decision thesis concrete: similar surface ambiguity can imply different ask/act decisions once context, equivalence, risk, and interaction cost are included.

## Aggregate Contrasts

| Slice | N | Oracle ask | Mean top prior | Mean norm. entropy | Mean success classes | Mean ask cost | Mean wrong cost | Mean EU ask-act |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bring / 2 candidates / context-resolved | 80 | 0.000 | 0.970 | 0.194 | 2.000 | 0.150 | 0.200 | -0.114 |
| bring / 2 candidates / referential | 80 | 1.000 | 0.530 | 0.997 | 2.000 | 0.050 | 1.000 | 0.891 |
| put-away preference / owner visible | 40 | 0.000 | 0.990 | 0.081 | 2.000 | 0.050 | 1.000 | -0.030 |
| put-away preference / owner hidden | 40 | 1.000 | 0.550 | 0.993 | 2.000 | 0.050 | 1.000 | 0.850 |
| high entropy / equivalent outcomes | 80 | 0.000 | 0.360 | 0.998 | 1.000 | 0.100 | 0.500 | -0.100 |
| high top-prior / high wrong-action cost | 80 | 1.000 | 0.799 | 0.720 | 2.000 | 0.050 | 3.000 | 0.752 |

## Representative Episodes

| Contrast slice | Episode | Instruction | Oracle | EU ask-act | Key factors |
| --- | --- | --- | --- | --- | --- |
| bring / 2 candidates / context-resolved | test_context_000001 | Bring me the cup. | ACT | -0.114 | candidates=2; classes=2; top_prior=0.970; norm_entropy=0.194; ask_cost=0.150; wrong_cost=0.200; context_resolves=true |
| bring / 2 candidates / referential | test_referential_000000 | Can you bring me the blue cup? | ASK | 0.875 | candidates=2; classes=2; top_prior=0.538; norm_entropy=0.996; ask_cost=0.050; wrong_cost=1.000 |
| put-away preference / owner visible | test_preference_000004 | Put my mug away. | ACT | -0.030 | candidates=2; classes=2; top_prior=0.990; norm_entropy=0.081; ask_cost=0.050; wrong_cost=1.000; context_resolves=true; owner_visible=true |
| put-away preference / owner hidden | test_preference_000009 | Put my book away. | ASK | 0.850 | candidates=2; classes=2; top_prior=0.550; norm_entropy=0.993; ask_cost=0.050; wrong_cost=1.000; owner_visible=false |
| high entropy / equivalent outcomes | test_equivalent_000002 | Move a spare box to the table. | ACT | -0.100 | candidates=3; classes=1; top_prior=0.360; norm_entropy=0.998; ask_cost=0.100; wrong_cost=0.500; equivalent_success=true |
| high top-prior / high wrong-action cost | test_risk_000003 | Delete the old folder. | ASK | 0.854 | candidates=2; classes=2; top_prior=0.774; norm_entropy=0.771; ask_cost=0.050; wrong_cost=3.000; risk=high |

## Interpretation

- The same two-candidate `bring` action family splits cleanly: context-resolved cases should act, while referential cases should ask.
- Preference/social examples use the same instruction family, but visible ownership makes acting optimal while hidden ownership makes asking optimal.
- Equivalent-outcome cases have high entropy and three candidates, yet acting is optimal because all candidates share one success class.
- Risk-sensitive cases can have high top-prior confidence, yet asking is still optimal because the wrong-action cost is high.
