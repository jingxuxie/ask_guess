# Submission Readiness Report

Generated: 2026-06-28 14:18:32

This report maps the current paper claims to the canonical evidence package and highlights what is ready versus still limited.

## Status

| Item | Value |
| --- | --- |
| Overall status | ready with stated limitations |
| Claim verification | PASS |
| Critical artifacts missing | none |
| Compiled PDF pages | 12 |
| Main benchmark rows | 1400 |
| Main split counts | dev: 200, ood_test: 200, test: 400, train: 600 |
| Style-stress rows | 50 |
| Style-stress categories | context_resolved: 10, equivalent_outcome: 10, preference_social: 10, referential: 10, risk_sensitive: 10 |
| Ambiguity-mix diagnostic rows | 1280 |
| Ambiguity-mix split counts | dev: 180, ood_ambiguity_mix: 200, test: 300, train: 600 |
| API cache responses | 914 |
| API cache total tokens | 320325 |
| API cache models | gpt-4.1-mini: 914 |
| Second-model cache responses | 109 |
| Second-model cache total tokens | 39595 |
| Second-model cache models | gpt-4.1-nano: 109 |

## Claim-to-Evidence Map

| Claim | Current evidence | Primary artifacts |
| --- | --- | --- |
| Clarification should be utility-dependent, not ambiguity-only. | All 400 canonical test episodes have multiple candidate interpretations, but 200 are oracle-act and 200 are oracle-ask. Situated contrast slices show same-action and same-instruction families flipping ask/act decisions under context, ownership, equivalence, and risk. | paper/tables/ambiguity_utility_diagnostic.md; paper/tables/situated_contrast_analysis.md; paper/tables/cost_sensitivity.md; paper/tables/qualitative_examples.md; paper/figures/cost_sensitivity_ask_cost.svg; paper/figures/cost_sensitivity_wrong_cost.svg |
| ECU improves first-turn API utility over prompting. | Main 100: ECU 0.976, Ask-Needed 0.632, DirectAct 0.420; paired ECU - Ask-Needed 0.343. Leave-one-category and leave-one-episode subset checks keep the ECU - Ask-Needed delta positive. | data/runs/api_eval_100_corrected_results.jsonl; paper/tables/api_eval_100_corrected/paired_differences.md; paper/tables/api_eval_100_corrected/subset_stability.md |
| Private-reasoning helps with scale but does not replace utility calibration in general. | GPT-4.1-mini CoT Ask-Needed utility 0.632; GPT-5.4-mini CoT 0.864 versus ECU 0.976; GPT-5.5 CoT 0.976 ties ECU 0.976 on the 100-episode subset. | data/runs/api_eval_100_cot_results.jsonl; data/runs/api_gpt_5_4_mini_test100_results.jsonl; data/runs/api_gpt_5_5_test100_results.jsonl; paper/tables/current_model_sweep.md |
| Current hosted models preserve the plain Ask-Needed calibration gap. | GPT-5.4-mini: ECU 0.976, Ask-Needed 0.868; GPT-5.5: ECU 0.976, Ask-Needed 0.821. ECU has zero missed and unnecessary clarifications in both current-model rows. | paper/tables/current_model_sweep.md; data/runs/api_gpt_5_4_mini_test100_results.jsonl; data/runs/api_gpt_5_5_test100_results.jsonl |
| ECU tracks utility margins. | Current calibration tables show ECU asks in ask-preferred bins and avoids act-preferred bins; prompted Ask-Needed asks in both bins. Cached API ECU candidate margins agree with oracle ask labels on 0.990 of main API rows. | paper/tables/api_eval_100_corrected/calibration_by_margin.md; paper/tables/api_style_stress_50/calibration_by_margin.md; paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md; paper/tables/api_candidate_calibration.md; paper/figures/api_calibration_ask_rate.svg |
| ECU uses plausible candidate probabilities, not perfect hidden-intent prediction. | On GPT-4.1-mini ECU rows, the model top success class matches the benchmark top-prior class on 0.970 of episodes, with mean prior TV 0.057; the top class matches the sampled hidden class on 0.770. Model and oracle utility margins remain strongly correlated. | paper/tables/api_candidate_calibration.md |
| ECU is stable under bounded scene-serialization perturbations. | GPT-5.4-mini shuffled object order: ECU 0.976, Ask-Needed 0.908, CoT 0.926; ECU changes ask/act decisions on 0/100 shared episodes. Natural-language scene: ECU 0.975, Ask-Needed 0.788, CoT 0.904; ECU changes ask/act decisions on 1/100 shared episodes. | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl; data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl; paper/tables/api_gpt_5_4_mini_scene_format_robustness.md; paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md |
| The main API utility advantage is not tied to one narrow scoring parameter. | Fixed cached API outputs keep positive ECU - Ask-Needed deltas across ask-cost and wrong-action-cost rescoring, with minimum delta 0.138 and minimum paired-CI lower bound 0.070. | paper/tables/api_eval_100_corrected/utility_sensitivity.md |
| The result survives a small paraphrase and answer-style stress set. | Style 50: ECU 0.977, Ask-Needed 0.814, DirectAct 0.320; paired ECU - Ask-Needed 0.163. | data/runs/api_style_stress_50_results.jsonl; paper/tables/api_style_stress_50/paired_differences.md |
| The direction survives a tiny second-model sanity check. | gpt-4.1-nano 25: ECU 0.722, Ask-Needed 0.098, DirectAct 0.040; paired ECU - Ask-Needed 0.624. | data/runs/api_second_model_25_results.jsonl; paper/tables/api_second_model_25/paired_differences.md |
| Failure modes are qualitatively diagnostic. | Failure taxonomy separates referential guessing, risk blindness, and equivalence blindness; question-usefulness tables show whether questions are needed and grounded. | paper/tables/api_eval_100_extended/failure_taxonomy.md; paper/tables/api_eval_100_extended/question_usefulness.md; paper/tables/api_style_stress_50/failure_taxonomy.md; paper/tables/api_style_stress_50/question_usefulness.md |
| Author-style audits support benchmark and question sanity. | Audit covers 100 scenarios and 100 sampled API questions; all scenario labels are ok and all audited ECU oracle-ask questions are natural and diagnostic. | paper/audits/AUDIT_SUMMARY.md; paper/audits/scenario_audit_completed.md; paper/audits/question_audit_completed.md |
| The deterministic simulated user returns visibly diagnostic answers. | Generated oracle-ask diagnostic answers resolve the hidden success class in 1233/1233 cases; actual API asked-row answers resolve in 184/184 cases. | paper/tables/simulated_user_audit.md |
| Offline controller and OOD checks support the mechanism. | Offline ECU test utility 0.958; OOD utility 0.975; held-out ambiguity-mix ECU utility 0.962. | data/runs/offline_results.jsonl; data/runs/ambiguity_mix_shift_results.jsonl; paper/tables/robustness_breakdown.md; paper/tables/ambiguity_mix_shift.md; paper/tables/controller_analysis.md |
| The learned controller has a useful category-transfer boundary. | When trained without risk-sensitive or preference/social episodes, held-out ECU utility is 0.962, while the learned controller is 0.950 and asks on 1.000 of held-out episodes. | data/generated/ambiguity_mix_shift_episodes.jsonl; paper/tables/ambiguity_mix_shift.md |
| External query-level ambiguity benchmarks motivate the task framing. | CLAMBER sanity check: provided ambiguity prediction recall is 0.284 against `require_clarification`, with missed clarification rate 0.716. | paper/tables/clamber_external_sanity.md |
| The shipped API evidence is cache-replayable without network calls. | Cache-only replay reproduces all 2225 canonical API rows across the main, CoT, style-stress, second-model, current-model, and scene-format result files with zero stable-row mismatches. | paper/tables/api_cache_replay_verification.md |
| Paper-facing numbers and caveats are stale-checked. | The consistency audit verifies that the manuscript, long draft, readiness report, and claim-scope report carry the verified headline numbers and limitation language. | paper/paper_consistency_audit.md |

## Main API Metrics

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| api_direct_act | 100 | 0.420 | [0.180, 0.640] | 0.770 | 0.000 | 1.000 | 0.000 |
| api_ask_needed | 100 | 0.632 | [0.431, 0.810] | 0.880 | 0.370 | 0.583 | 0.327 |
| api_ecu | 100 | 0.976 | [0.972, 0.981] | 1.000 | 0.480 | 0.000 | 0.000 |

## Auxiliary CoT API Metric

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| api_ask_needed_cot | 100 | 0.632 | [0.413, 0.816] | 0.890 | 0.370 | 0.604 | 0.346 |

## Style-Stress API Metrics

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| api_direct_act | 50 | 0.320 | [-0.080, 0.680] | 0.760 | 0.000 | 1.000 | 0.000 |
| api_ask_needed | 50 | 0.814 | [0.654, 0.945] | 0.920 | 0.380 | 0.478 | 0.259 |
| api_ecu | 50 | 0.977 | [0.970, 0.984] | 1.000 | 0.460 | 0.000 | 0.000 |

## Auxiliary Second-Model API Metrics

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| api_direct_act | 25 | 0.040 | [-0.520, 0.600] | 0.640 | 0.000 | 1.000 | 0.000 |
| api_ask_needed | 25 | 0.098 | [-0.456, 0.586] | 0.680 | 0.240 | 0.909 | 0.357 |
| api_ecu | 25 | 0.722 | [0.412, 0.954] | 0.880 | 0.560 | 0.182 | 0.357 |

## Critical Artifacts

| Artifact | Status | Bytes | JSONL rows |
| --- | --- | --- | --- |
| data/generated/episodes.jsonl | present | 2197056 | 1400 |
| data/generated/style_stress_episodes.jsonl | present | 85950 | 50 |
| data/generated/ambiguity_mix_shift_episodes.jsonl | present | 2061286 | 1280 |
| data/runs/offline_results.jsonl | present | 2518289 | 4200 |
| data/runs/ambiguity_mix_shift_results.jsonl | present | 2143929 | 3500 |
| data/runs/api_eval_100_corrected_results.jsonl | present | 672440 | 300 |
| data/runs/api_eval_100_cot_results.jsonl | present | 156755 | 100 |
| data/runs/api_style_stress_50_results.jsonl | present | 340112 | 150 |
| data/runs/api_second_model_25_results.jsonl | present | 171250 | 75 |
| data/runs/api_gpt_5_4_mini_test100_results.jsonl | present | 947779 | 400 |
| data/runs/api_gpt_5_5_test100_results.jsonl | present | 899888 | 400 |
| data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl | present | 961287 | 400 |
| data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl | present | 966044 | 400 |
| data/runs/api_cache.jsonl | present | 808118 | 914 |
| data/runs/api_second_model_cache.jsonl | present | 100851 | 109 |
| data/runs/api_gpt_5_4_mini_cache.jsonl | present | 616813 | 667 |
| data/runs/api_gpt_5_5_cache.jsonl | present | 576365 | 609 |
| data/runs/api_gpt_5_4_mini_scene_cache.jsonl | present | 572844 | 616 |
| data/runs/api_gpt_5_4_mini_nl_cache.jsonl | present | 575823 | 616 |
| paper/dataset_card.md | present | 5408 | - |
| paper/claim_verification.md | present | 33078 | - |
| paper/claim_scope.md | present | 9087 | - |
| paper/paper_consistency_audit.md | present | 3493 | - |
| paper/supplement_audit.md | present | 1406 | - |
| paper/latex/main.tex | present | 41021 | - |
| paper/latex/refs.bib | present | 8136 | - |
| paper/latex/colm2026_conference.sty | present | 7727 | - |
| paper/latex/colm2026_conference.bst | present | 26973 | - |
| paper/latex/fancyhdr.sty | present | 20521 | - |
| paper/latex/natbib.sty | present | 45154 | - |
| paper/latex/math_commands.tex | present | 12284 | - |
| paper/latex/main.pdf | present | 178704 | - |

## Supporting Artifacts

| Artifact | Status | Bytes | JSONL rows |
| --- | --- | --- | --- |
| paper/tables/benchmark_categories.md | present | 886 | - |
| paper/tables/qualitative_examples.md | present | 2652 | - |
| paper/tables/controller_analysis.md | present | 3229 | - |
| paper/tables/ambiguity_utility_diagnostic.md | present | 3273 | - |
| paper/tables/situated_contrast_analysis.md | present | 3115 | - |
| paper/tables/cost_sensitivity.md | present | 6030 | - |
| paper/tables/ambiguity_mix_shift.md | present | 5041 | - |
| paper/tables/clamber_external_sanity.md | present | 4198 | - |
| paper/tables/simulated_user_audit.md | present | 2684 | - |
| paper/tables/api_cache_replay_verification.md | present | 4140 | - |
| paper/tables/api_eval_100_corrected/paired_differences.md | present | 355 | - |
| paper/tables/api_eval_100_corrected/subset_stability.md | present | 1917 | - |
| paper/tables/api_eval_100_corrected/calibration_by_margin.md | present | 1401 | - |
| paper/tables/api_eval_100_corrected/ecu_ablation.md | present | 2981 | - |
| paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md | present | 2767 | - |
| paper/tables/api_candidate_calibration.md | present | 3114 | - |
| paper/tables/api_eval_100_corrected/utility_sensitivity.md | present | 5812 | - |
| paper/tables/api_eval_100_extended/failure_taxonomy.md | present | 3439 | - |
| paper/tables/api_eval_100_extended/question_usefulness.md | present | 1035 | - |
| paper/tables/api_style_stress_50/paired_differences.md | present | 370 | - |
| paper/tables/api_style_stress_50/calibration_by_margin.md | present | 1458 | - |
| paper/tables/api_style_stress_50/failure_taxonomy.md | present | 2819 | - |
| paper/tables/api_style_stress_50/question_usefulness.md | present | 970 | - |
| paper/tables/api_second_model_25/paired_differences.md | present | 353 | - |
| paper/tables/api_second_model_25/category_breakdown.md | present | 1332 | - |
| paper/tables/api_gpt_5_4_mini_test100/paired_differences.md | present | 352 | - |
| paper/tables/api_gpt_5_5_test100/paired_differences.md | present | 352 | - |
| paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md | present | 352 | - |
| paper/tables/api_gpt_5_4_mini_natural_language_test100/paired_differences.md | present | 352 | - |
| paper/tables/api_gpt_5_4_mini_scene_format_robustness.md | present | 2638 | - |
| paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md | present | 2641 | - |
| paper/tables/current_model_sweep.md | present | 798 | - |
| paper/audits/AUDIT_SUMMARY.md | present | 845 | - |
| paper/dataset_card.md | present | 5408 | - |
| paper/claim_scope.md | present | 9087 | - |
| paper/paper_consistency_audit.md | present | 3493 | - |
| paper/supplement_audit.md | present | 1406 | - |
| paper/figures/api_main_net_utility.svg | present | 2215 | - |
| paper/figures/api_category_net_utility.svg | present | 4545 | - |
| paper/figures/api_calibration_ask_rate.svg | present | 3385 | - |
| paper/figures/cost_sensitivity_ask_cost.svg | present | 3460 | - |
| paper/figures/cost_sensitivity_wrong_cost.svg | present | 3452 | - |
| paper/supplement_manifest.md | present | 9417 | - |
| tests/test_core_invariants.py | present | 13359 | - |

## Validation Commands

```bash
conda run -n ask_dont_guess python -m unittest discover -s tests
conda run -n ask_dont_guess python -m compileall -q src tests
conda run -n ask_dont_guess python src/make_ambiguity_mix_shift.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --out data/runs/ambiguity_mix_shift_results.jsonl --eval-splits test,ood_ambiguity_mix
conda run -n ask_dont_guess python src/ambiguity_mix_shift_analysis.py
conda run -n ask_dont_guess python src/api_cache_replay_verification.py
conda run -n ask_dont_guess python src/simulated_user_audit.py
conda run -n ask_dont_guess python src/api_subset_stability.py
conda run -n ask_dont_guess python src/api_utility_sensitivity.py
conda run -n ask_dont_guess python src/ambiguity_utility_diagnostic.py
conda run -n ask_dont_guess python src/situated_contrast_analysis.py
conda run -n ask_dont_guess python src/paper_consistency_audit.py
conda run -n ask_dont_guess python src/verify_claims.py
conda run -n ask_dont_guess python src/make_dataset_card.py
conda run -n ask_dont_guess python src/make_claim_scope_report.py
conda run -n ask_dont_guess python src/make_submission_readiness_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py --manifest-only
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
conda run -n ask_dont_guess python src/audit_supplement_release.py
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
cd paper/latex && latexmk -pdf -interaction=nonstopmode main.tex
```

## Cache-Only API Replays

These commands should fail on cache miss and should not spend API budget.

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_corrected_replay.jsonl --summary-out /tmp/api_eval_100_corrected_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_cot_replay.jsonl --summary-out /tmp/api_eval_100_cot_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_ask_needed_cot --cache-only
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out /tmp/api_style_stress_50_replay.jsonl --summary-out /tmp/api_style_stress_50_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_second_model_25_replay.jsonl --summary-out /tmp/api_second_model_25_replay.md --cache data/runs/api_second_model_cache.jsonl --model gpt-4.1-nano --split test --limit-per-category 5 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

## Known Limitations

| Limitation | Submission framing |
| --- | --- |
| Synthetic benchmark | Claims are about situated instruction-following episodes generated by the local benchmark, not real household deployment. |
| Model coverage | The headline API evidence uses gpt-4.1-mini. A 25-episode gpt-4.1-nano sanity check supports the direction, but broader model sweeps remain future work. |
| Scale | Main API result is 100 stratified episodes, with subset-stability checks and a 50-episode style-stress set; offline results cover the full generated test/OOD splits. |
| User model | Clarification answers are deterministic simulated user answers; the visible-answer audit supports diagnostic clarity, but this is not a human-response study. |
| Submission framing | The strongest claim is value-of-information calibration for first-turn clarify-vs-act decisions, not general interactive dialogue mastery. |
