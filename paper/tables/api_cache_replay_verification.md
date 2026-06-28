# API Cache-Only Replay Verification

This generated report replays each canonical API evidence set through `run_api_experiment.py` with `CachedResponsesClient(cache_only=True)`. It does not read an API key and fails on cache miss. Rows are compared on stable behavioral fields plus stable ECU debug fields; response IDs, timestamps, and usage metadata are intentionally ignored.

## Summary

| Replay | Status | Canonical rows | Replay rows | Cache rows | Mismatches | Cache |
| --- | --- | --- | --- | --- | --- | --- |
| main_100_gpt41mini | PASS | 300 | 300 | 914 | 0 | data/runs/api_cache.jsonl |
| cot_100_gpt41mini | PASS | 100 | 100 | 914 | 0 | data/runs/api_cache.jsonl |
| style_50_gpt41mini | PASS | 150 | 150 | 914 | 0 | data/runs/api_cache.jsonl |
| second_model_25_gpt41nano | PASS | 75 | 75 | 109 | 0 | data/runs/api_second_model_cache.jsonl |
| current_100_gpt54mini | PASS | 400 | 400 | 667 | 0 | data/runs/api_gpt_5_4_mini_cache.jsonl |
| current_100_gpt55 | PASS | 400 | 400 | 609 | 0 | data/runs/api_gpt_5_5_cache.jsonl |
| shuffled_scene_100_gpt54mini | PASS | 400 | 400 | 616 | 0 | data/runs/api_gpt_5_4_mini_scene_cache.jsonl |
| natural_language_scene_100_gpt54mini | PASS | 400 | 400 | 616 | 0 | data/runs/api_gpt_5_4_mini_nl_cache.jsonl |

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
| current_100_gpt54mini | api_direct_act | 0.380 | 0.380 | 0.000 | 0.000 | 0.750 | 0.750 |
| current_100_gpt54mini | api_ask_needed | 0.868 | 0.868 | 0.690 | 0.690 | 0.970 | 0.970 |
| current_100_gpt54mini | api_ask_needed_cot | 0.864 | 0.864 | 0.740 | 0.740 | 0.980 | 0.980 |
| current_100_gpt54mini | api_ecu | 0.976 | 0.976 | 0.480 | 0.480 | 1.000 | 1.000 |
| current_100_gpt55 | api_direct_act | 0.240 | 0.240 | 0.000 | 0.000 | 0.720 | 0.720 |
| current_100_gpt55 | api_ask_needed | 0.821 | 0.821 | 0.370 | 0.370 | 0.960 | 0.960 |
| current_100_gpt55 | api_ask_needed_cot | 0.976 | 0.976 | 0.480 | 0.480 | 1.000 | 1.000 |
| current_100_gpt55 | api_ecu | 0.976 | 0.976 | 0.480 | 0.480 | 1.000 | 1.000 |
| shuffled_scene_100_gpt54mini | api_direct_act | 0.420 | 0.420 | 0.000 | 0.000 | 0.770 | 0.770 |
| shuffled_scene_100_gpt54mini | api_ask_needed | 0.908 | 0.908 | 0.710 | 0.710 | 0.990 | 0.990 |
| shuffled_scene_100_gpt54mini | api_ask_needed_cot | 0.926 | 0.926 | 0.730 | 0.730 | 0.990 | 0.990 |
| shuffled_scene_100_gpt54mini | api_ecu | 0.976 | 0.976 | 0.480 | 0.480 | 1.000 | 1.000 |
| natural_language_scene_100_gpt54mini | api_direct_act | 0.420 | 0.420 | 0.000 | 0.000 | 0.770 | 0.770 |
| natural_language_scene_100_gpt54mini | api_ask_needed | 0.788 | 0.788 | 0.670 | 0.670 | 0.940 | 0.940 |
| natural_language_scene_100_gpt54mini | api_ask_needed_cot | 0.904 | 0.904 | 0.720 | 0.720 | 0.990 | 0.990 |
| natural_language_scene_100_gpt54mini | api_ecu | 0.975 | 0.975 | 0.490 | 0.490 | 1.000 | 1.000 |

## Mismatches

| Replay | Mismatch |
| --- | --- |
| none | none |

## Interpretation

- PASS means the shipped API caches reproduce the canonical API result rows without network calls.
- This is a reproducibility check, not a new model evaluation.

Overall status: **PASS**
