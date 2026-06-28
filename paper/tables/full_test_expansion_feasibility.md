# Full-Test Current-Model Expansion Feasibility

This no-API report sizes the Priority 2 full 400-episode current-model expansion before spending budget.

## Target

- Split: `test`
- Limit per category: `80`
- Scene format: `json`
- Policies: `api_ask_needed, api_ask_needed_cot, api_ecu`
- Total target episodes: 400

| Category | Target episodes | Oracle ask rate |
| --- | --- | --- |
| context_resolved | 80 | 0.000 |
| equivalent_outcome | 80 | 0.000 |
| preference_social | 80 | 0.500 |
| referential | 80 | 1.000 |
| risk_sensitive | 80 | 1.000 |

## Existing Coverage and Exact Cache Hits

| Model | Coverage result path | Target rows | Existing rows | New rows | First calls | Cached first | First misses | Known ECU question calls | Cached ECU question | Known second-turn calls | Cached second-turn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.4-mini | data/runs/api_gpt_5_4_mini_test400_results.jsonl | 1200 | 1200 | 0 | 1200 | 1200 | 0 | 200 | 200 | 796 | 796 |
| gpt-5.5 | data/runs/api_gpt_5_5_test400_results.jsonl | 1200 | 1200 | 0 | 1200 | 1200 | 0 | 200 | 200 | 553 | 553 |

## Observed 100-Episode Metrics for Target Policies

| Model | Policy | Observed N | Utility | Ask rate | Missed | Unnecessary |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-5.4-mini | api_ask_needed | 100 | 0.868 | 0.690 | 0.125 | 0.519 |
| gpt-5.4-mini | api_ask_needed_cot | 100 | 0.864 | 0.740 | 0.062 | 0.558 |
| gpt-5.4-mini | api_ecu | 100 | 0.976 | 0.480 | 0.000 | 0.000 |
| gpt-5.5 | api_ask_needed | 100 | 0.821 | 0.370 | 0.271 | 0.038 |
| gpt-5.5 | api_ask_needed_cot | 100 | 0.976 | 0.480 | 0.000 | 0.000 |
| gpt-5.5 | api_ecu | 100 | 0.976 | 0.480 | 0.000 | 0.000 |

## Token and Cost Projection

For completed full-test runs, usage is measured from the full result file and remaining cost is zero. For incomplete runs, projected usage scales the observed 100-episode target-policy usage within each category to 80 episodes per category. Cost uses standard short-context OpenAI API prices per 1M tokens as checked on 2026-06-28: GPT-5.5 input/output $5.00/$30.00; GPT-5.4-mini input/output $0.75/$4.50. Verify prices again immediately before a paid run.

| Model | Observed 100 responses | Observed input | Observed output | Projected 400 responses | Projected input | Projected output | Incremental responses | Incremental input | Incremental output | Est. incremental cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-5.4-mini | 510 | 153885 | 28723 | 2084 | 628027 | 117223 | 0 | 0 | 0 | $0.00 |
| gpt-5.5 | 470 | 143864 | 27588 | 1909 | 583914 | 112728 | 0 | 0 | 0 | $0.00 |

## Recommendation

- Estimated remaining standard-price cost for configured full 400-episode runs: $0.00.
- For runs without full-test coverage, this estimate extrapolates from the already cached 100-episode current-model rows with the same balanced category mix.
- No remaining full-test API rows are needed for the configured runs.
- Use cache files already listed here and keep `api_ask_needed,api_ask_needed_cot,api_ecu` as the target policy set.
- No API calls are made by this feasibility script.
