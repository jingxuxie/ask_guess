# API Cache-Only Replay Verification

This generated report replays each canonical API evidence set through `run_api_experiment.py` with `CachedResponsesClient(cache_only=True)`. It does not read an API key and fails on cache miss. Rows are compared on stable behavioral fields plus stable ECU debug fields; response IDs, timestamps, and usage metadata are intentionally ignored.

## Summary

| Replay | Status | Canonical rows | Replay rows | Cache rows | Mismatches | Cache |
| --- | --- | --- | --- | --- | --- | --- |
| main_100_gpt41mini | PASS | 300 | 300 | 914 | 0 | data/runs/api_cache.jsonl |
| cot_100_gpt41mini | PASS | 100 | 100 | 914 | 0 | data/runs/api_cache.jsonl |
| style_50_gpt41mini | PASS | 150 | 150 | 914 | 0 | data/runs/api_cache.jsonl |
| second_model_25_gpt41nano | PASS | 75 | 75 | 109 | 0 | data/runs/api_second_model_cache.jsonl |

## Metric Equality Check

| Replay | Policy | Canonical utility | Replay utility | Canonical ask | Replay ask | Canonical success | Replay success |
| --- | --- | --- | --- | --- | --- | --- | --- |
| main_100_gpt41mini | api_direct_act | 0.420 | 0.420 | 0.000 | 0.000 | 0.770 | 0.770 |
| main_100_gpt41mini | api_ask_needed | 0.632 | 0.632 | 0.370 | 0.370 | 0.880 | 0.880 |
| main_100_gpt41mini | api_ecu | 0.976 | 0.976 | 0.480 | 0.480 | 1.000 | 1.000 |
| cot_100_gpt41mini | api_ask_needed_cot | 0.632 | 0.632 | 0.370 | 0.370 | 0.890 | 0.890 |
| style_50_gpt41mini | api_direct_act | 0.320 | 0.320 | 0.000 | 0.000 | 0.760 | 0.760 |
| style_50_gpt41mini | api_ask_needed | 0.814 | 0.814 | 0.380 | 0.380 | 0.920 | 0.920 |
| style_50_gpt41mini | api_ecu | 0.977 | 0.977 | 0.460 | 0.460 | 1.000 | 1.000 |
| second_model_25_gpt41nano | api_direct_act | 0.040 | 0.040 | 0.000 | 0.000 | 0.640 | 0.640 |
| second_model_25_gpt41nano | api_ask_needed | 0.098 | 0.098 | 0.240 | 0.240 | 0.680 | 0.680 |
| second_model_25_gpt41nano | api_ecu | 0.722 | 0.722 | 0.560 | 0.560 | 0.880 | 0.880 |

## Mismatches

| Replay | Mismatch |
| --- | --- |
| none | none |

## Interpretation

- PASS means the shipped API caches reproduce the canonical API result rows without network calls.
- This is a reproducibility check, not a new model evaluation.

Overall status: **PASS**
