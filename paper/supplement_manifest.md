# Supplement Package Manifest

This generated manifest defines the files intended for an anonymized/release supplement.
The companion zip is built deterministically from this file list with fixed archive timestamps.

## Archive

- Default path: `paper/clarify_to_act_supplement.zip`
- Included files: 150
- Missing required files: none

## Groups

- Source: 53 files
- Canonical data and cached API evidence: 11 files
- Paper, tables, figures, and audits: 84 files
- Top-level summaries: 2 files

## Exclusion Policy

The package excludes API keys, local tool state, Python bytecode, LaTeX build intermediates, older smoke-run traces, and the zip file itself.

- `*/__pycache__/*`
- `*.pyc`
- `*.pyo`
- `.git/*`
- `.agents/*`
- `.codex/*`
- `*apikey*`
- `*.aux`
- `*.blg`
- `*.fdb_latexmk`
- `*.fls`
- `*.log`
- `paper/clarify_to_act_supplement.zip`
- `data/generated/smoke_episodes.jsonl`
- `data/runs/api_smoke*.jsonl`
- `data/runs/smoke_*.jsonl`
- `data/runs/api_eval_100_results.jsonl`
- `data/runs/api_second_model_viability_results.jsonl`
- `paper/tables/api_smoke*`
- `paper/tables/smoke*`
- `paper/tables/api_eval_100/*`
- `paper/tables/api_eval_100_results.md`
- `paper/tables/api_second_model_viability_results.md`

## Included Files

- `README.md`
- `RESULTS_SUMMARY.md`
- `data/generated/ambiguity_mix_shift_episodes.jsonl`
- `data/generated/episodes.jsonl`
- `data/generated/style_stress_episodes.jsonl`
- `data/runs/ambiguity_mix_shift_results.jsonl`
- `data/runs/api_cache.jsonl`
- `data/runs/api_eval_100_corrected_results.jsonl`
- `data/runs/api_eval_100_cot_results.jsonl`
- `data/runs/api_second_model_25_results.jsonl`
- `data/runs/api_second_model_cache.jsonl`
- `data/runs/api_style_stress_50_results.jsonl`
- `data/runs/offline_results.jsonl`
- `paper/README.md`
- `paper/audits/AUDIT_INDEX.md`
- `paper/audits/AUDIT_SUMMARY.md`
- `paper/audits/question_audit_completed.md`
- `paper/audits/question_audit_packet.md`
- `paper/audits/scenario_audit_completed.md`
- `paper/audits/scenario_audit_packet.md`
- `paper/claim_scope.md`
- `paper/claim_verification.md`
- `paper/clarify_to_act_paper_draft.md`
- `paper/dataset_card.md`
- `paper/figures/FIGURE_INDEX.md`
- `paper/figures/api_calibration_ask_rate.svg`
- `paper/figures/api_category_net_utility.svg`
- `paper/figures/api_main_net_utility.svg`
- `paper/figures/cost_sensitivity_ask_cost.svg`
- `paper/figures/cost_sensitivity_wrong_cost.svg`
- `paper/latex/Makefile`
- `paper/latex/README.md`
- `paper/latex/colm2026_conference.bst`
- `paper/latex/colm2026_conference.pdf`
- `paper/latex/colm2026_conference.sty`
- `paper/latex/fancyhdr.sty`
- `paper/latex/main.bbl`
- `paper/latex/main.pdf`
- `paper/latex/main.tex`
- `paper/latex/math_commands.tex`
- `paper/latex/natbib.sty`
- `paper/latex/refs.bib`
- `paper/paper_consistency_audit.md`
- `paper/references.md`
- `paper/reproducibility.md`
- `paper/submission_readiness.md`
- `paper/supplement_audit.md`
- `paper/supplement_manifest.md`
- `paper/tables/ambiguity_mix_shift.md`
- `paper/tables/ambiguity_utility_diagnostic.md`
- `paper/tables/api_cache_replay_verification.md`
- `paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md`
- `paper/tables/api_eval_100_corrected/calibration_by_margin.md`
- `paper/tables/api_eval_100_corrected/category_breakdown.md`
- `paper/tables/api_eval_100_corrected/ecu_ablation.md`
- `paper/tables/api_eval_100_corrected/failure_examples.md`
- `paper/tables/api_eval_100_corrected/main_results.md`
- `paper/tables/api_eval_100_corrected/paired_differences.md`
- `paper/tables/api_eval_100_corrected/subset_stability.md`
- `paper/tables/api_eval_100_corrected/utility_sensitivity.md`
- `paper/tables/api_eval_100_corrected_results.md`
- `paper/tables/api_eval_100_cot/category_breakdown.md`
- `paper/tables/api_eval_100_cot/failure_examples.md`
- `paper/tables/api_eval_100_cot/main_results.md`
- `paper/tables/api_eval_100_cot_results.md`
- `paper/tables/api_eval_100_extended/category_breakdown.md`
- `paper/tables/api_eval_100_extended/failure_examples.md`
- `paper/tables/api_eval_100_extended/failure_taxonomy.md`
- `paper/tables/api_eval_100_extended/main_results.md`
- `paper/tables/api_eval_100_extended/paired_differences.md`
- `paper/tables/api_eval_100_extended/question_usefulness.md`
- `paper/tables/api_second_model_25/category_breakdown.md`
- `paper/tables/api_second_model_25/failure_examples.md`
- `paper/tables/api_second_model_25/main_results.md`
- `paper/tables/api_second_model_25/paired_differences.md`
- `paper/tables/api_second_model_25_results.md`
- `paper/tables/api_style_stress_50/calibration_by_margin.md`
- `paper/tables/api_style_stress_50/category_breakdown.md`
- `paper/tables/api_style_stress_50/failure_examples.md`
- `paper/tables/api_style_stress_50/failure_taxonomy.md`
- `paper/tables/api_style_stress_50/main_results.md`
- `paper/tables/api_style_stress_50/paired_differences.md`
- `paper/tables/api_style_stress_50/question_usefulness.md`
- `paper/tables/api_style_stress_50_results.md`
- `paper/tables/benchmark_categories.md`
- `paper/tables/category_breakdown.md`
- `paper/tables/clamber_external_sanity.md`
- `paper/tables/controller_analysis.md`
- `paper/tables/cost_sensitivity.md`
- `paper/tables/failure_examples.md`
- `paper/tables/main_results.md`
- `paper/tables/paired_differences.md`
- `paper/tables/qualitative_examples.md`
- `paper/tables/robustness_breakdown.md`
- `paper/tables/scenario_samples.md`
- `paper/tables/simulated_user_audit.md`
- `paper/tables/situated_contrast_analysis.md`
- `prompts/act_after_answer.txt`
- `prompts/ask_when_needed.txt`
- `prompts/ask_when_needed_cot.txt`
- `prompts/candidate_interpretations.txt`
- `prompts/direct_act.txt`
- `prompts/generate_question.txt`
- `requirements.txt`
- `src/ambiguity_mix_shift_analysis.py`
- `src/ambiguity_utility_diagnostic.py`
- `src/analyze_results.py`
- `src/api_cache_replay_verification.py`
- `src/api_ecu_ablation.py`
- `src/api_ecu_margin_analysis.py`
- `src/api_subset_stability.py`
- `src/api_utility_sensitivity.py`
- `src/audit_supplement_release.py`
- `src/benchmark_categories.py`
- `src/calibration_analysis.py`
- `src/clamber_external_sanity.py`
- `src/clarify_to_act/__init__.py`
- `src/clarify_to_act/api_client.py`
- `src/clarify_to_act/controller.py`
- `src/clarify_to_act/environment.py`
- `src/clarify_to_act/generator.py`
- `src/clarify_to_act/io.py`
- `src/clarify_to_act/metrics.py`
- `src/clarify_to_act/policies.py`
- `src/complete_audit_packet.py`
- `src/controller_analysis.py`
- `src/cost_sensitivity.py`
- `src/failure_taxonomy.py`
- `src/generate_scenarios.py`
- `src/inspect_scenarios.py`
- `src/make_ambiguity_mix_shift.py`
- `src/make_audit_packet.py`
- `src/make_claim_scope_report.py`
- `src/make_dataset_card.py`
- `src/make_figures.py`
- `src/make_reproducibility_report.py`
- `src/make_style_stress_episodes.py`
- `src/make_submission_readiness_report.py`
- `src/make_supplement_package.py`
- `src/paired_differences.py`
- `src/paper_consistency_audit.py`
- `src/qualitative_examples.py`
- `src/question_usefulness_analysis.py`
- `src/robustness_analysis.py`
- `src/run_api_experiment.py`
- `src/run_experiment.py`
- `src/simulated_user_audit.py`
- `src/situated_contrast_analysis.py`
- `src/verify_claims.py`
- `tests/test_core_invariants.py`

## Rebuild

```bash
conda run -n ask_dont_guess python src/make_supplement_package.py
```
