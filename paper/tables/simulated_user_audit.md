# Simulated User Answer Audit

This generated audit checks whether deterministic simulated-user answers are visibly diagnostic. For each oracle-ask generated episode, it asks the policy diagnostic question and verifies that the returned answer identifies the hidden success class using only fields visible to the model. For each actual API row where a policy asked a question, it verifies the stored answer the model received in the same way.

## Summary

| Check | N | Resolved | Resolution rate |
| --- | --- | --- | --- |
| Generated oracle-ask diagnostic answers | 1233 | 1233 | 1.000 |
| Actual API asked-row answers | 184 | 184 | 1.000 |

## Generated Oracle-Ask Diagnostic Answers

| Source | Category | Oracle-ask N | Resolved | Resolution rate |
| --- | --- | --- | --- | --- |
| data/generated/ambiguity_mix_shift_episodes.jsonl | preference_social | 50 | 50 | 1.000 |
| data/generated/ambiguity_mix_shift_episodes.jsonl | referential | 360 | 360 | 1.000 |
| data/generated/ambiguity_mix_shift_episodes.jsonl | risk_sensitive | 100 | 100 | 1.000 |
| data/generated/episodes.jsonl | preference_social | 140 | 140 | 1.000 |
| data/generated/episodes.jsonl | referential | 280 | 280 | 1.000 |
| data/generated/episodes.jsonl | risk_sensitive | 280 | 280 | 1.000 |
| data/generated/style_stress_episodes.jsonl | preference_social | 3 | 3 | 1.000 |
| data/generated/style_stress_episodes.jsonl | referential | 10 | 10 | 1.000 |
| data/generated/style_stress_episodes.jsonl | risk_sensitive | 10 | 10 | 1.000 |

## Actual API Asked-Row Answers

| Source | Policy | Asked N | Resolved | Resolution rate |
| --- | --- | --- | --- | --- |
| data/runs/api_eval_100_corrected_results.jsonl | api_ask_needed | 37 | 37 | 1.000 |
| data/runs/api_eval_100_corrected_results.jsonl | api_ecu | 48 | 48 | 1.000 |
| data/runs/api_eval_100_cot_results.jsonl | api_ask_needed_cot | 37 | 37 | 1.000 |
| data/runs/api_second_model_25_results.jsonl | api_ask_needed | 6 | 6 | 1.000 |
| data/runs/api_second_model_25_results.jsonl | api_ecu | 14 | 14 | 1.000 |
| data/runs/api_style_stress_50_results.jsonl | api_ask_needed | 19 | 19 | 1.000 |
| data/runs/api_style_stress_50_results.jsonl | api_ecu | 23 | 23 | 1.000 |

## Failures

| Source | Policy | Episode | Category | Question | Answer | Top visible targets |
| --- | --- | --- | --- | --- | --- | --- |
| none | none | none | none | none | none | none |

## Interpretation

- PASS means the deterministic answer strings identify the hidden success class from visible scene fields in this audit.
- This supports the reproducibility and diagnostic clarity of the simulated user, but it is not a human-response study.

Overall status: **PASS**
