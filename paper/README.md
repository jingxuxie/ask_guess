# Paper Artifact Guide

Use these canonical artifacts for the current draft.

## Draft

- `clarify_to_act_paper_draft.md`
- `references.md`
- `dataset_card.md`: generated benchmark schema, split, category, leakage-control, and limitation summary.
- `latex/main.tex`: COLM-style LaTeX draft.
- `latex/refs.bib`: BibTeX entries.
- `latex/colm2026_conference.sty` and `latex/colm2026_conference.bst`: COLM 2026 template style files.
- `latex/fancyhdr.sty`, `latex/natbib.sty`, `latex/math_commands.tex`, `latex/colm2026_conference.pdf`: support files from `Template-2026.zip`.
- `latex/main.pdf`: compiled 12-page PDF.
- `latex/Makefile`: rebuild with `make` from `paper/latex`.
- `reproducibility.md`: artifact hashes, recomputed metrics, cache totals, and exact reproduction commands.
- `claim_verification.md`: automated check that headline claims match canonical artifacts.
- `claim_scope.md`: generated writing guardrail for supported claims, overclaims, and reviewer risks.
- `paper_consistency_audit.md`: generated stale-text guardrail for manuscript numbers and scope caveats.
- `submission_readiness.md`: generated claim-to-evidence map, artifact checklist, validation commands, and current limitations.
- `supplement_manifest.md`: generated file list and exclusion policy for the release supplement.
- `supplement_audit.md`: generated release audit for forbidden paths, local paths, API-key-like secrets, and stale traces.
- `clarify_to_act_supplement.zip`: deterministic supplement archive built from `supplement_manifest.md`.

## Canonical Results

- `tables/benchmark_categories.md`: generated benchmark category counts, oracle ask rates, expected behavior, and representative instructions.
- `tables/qualitative_examples.md`: representative API-subset examples showing when the same ambiguity surface should lead to asking versus acting.
- `tables/main_results.md`: full offline 400-episode test and 200-episode OOD result.
- `tables/category_breakdown.md`: full offline category breakdown.
- `tables/paired_differences.md`: paired bootstrap net-utility differences for offline results.
- `tables/robustness_breakdown.md`: OOD and held-out-object robustness slices.
- `tables/controller_analysis.md`: tuned thresholds, learned logistic weights, and learned-controller category behavior.
- `tables/ambiguity_utility_diagnostic.md`: no-API diagnostic showing why surface ambiguity and uncertainty-only policies are insufficient.
- `tables/situated_contrast_analysis.md`: no-API matched slices showing how context, ownership, equivalence, and risk flip optimal ask/act decisions.
- `tables/ambiguity_mix_shift.md`: no-API held-out ambiguity-mix diagnostic for risk-sensitive and preference/social transfer.
- `tables/clamber_external_sanity.md`: external CLAMBER ask/answer sanity check using the public benchmark labels and provided ambiguity prediction.
- `tables/simulated_user_audit.md`: visible-field audit of deterministic simulated-user answers.
- `tables/api_cache_replay_verification.md`: cache-only replay verification for all canonical API evidence files.
- `tables/cost_sensitivity.md`: offline cost-sensitivity sweep.
- `tables/api_eval_100_corrected_results.md`: final 100-episode stratified API result.
- `tables/api_eval_100_corrected/category_breakdown.md`: final API category breakdown.
- `tables/api_eval_100_corrected/paired_differences.md`: paired bootstrap differences for the final API result.
- `tables/api_eval_100_corrected/subset_stability.md`: no-API leave-one-category, leave-one-episode, and stratified-bootstrap stability check for the final API result.
- `tables/api_eval_100_corrected/ecu_ablation.md`: no-API replay ablation of ECU decision-rule safeguards.
- `tables/api_eval_100_corrected/utility_sensitivity.md`: no-API fixed-output rescoring of cached API results under alternate ask/wrong-action costs.
- `tables/api_eval_100_corrected/api_ecu_margin_analysis.md`: no-API diagnostic of cached API ECU candidate utility margins.
- `tables/api_candidate_calibration.md`: no-API diagnostic of cached API ECU candidate-probability calibration.
- `tables/api_eval_100_corrected/calibration_by_margin.md`: utility-margin calibration for the final API result.
- `tables/api_eval_100_corrected/failure_examples.md`: final API failure examples.
- `tables/api_eval_100_extended/`: auxiliary API comparison including the private-reasoning Ask-Needed baseline, failure taxonomy, and question-usefulness diagnostics.
- `tables/api_style_stress_50_results.md`: 50-episode API paraphrase and answer-style stress result.
- `tables/api_style_stress_50/`: detailed style-stress main, category, paired-difference, calibration, failure-taxonomy, question-usefulness, and failure-example tables.
- `tables/api_second_model_25_results.md`: auxiliary 25-episode `gpt-4.1-nano` sanity check.
- `tables/api_second_model_25/`: detailed second-model main, category, paired-difference, and failure-example tables.
- `tables/api_gpt_5_4_mini_test100_results.md`: current-model 100-episode `gpt-5.4-mini` sweep.
- `tables/api_gpt_5_4_mini_test100/`: detailed `gpt-5.4-mini` current-model main, category, paired-difference, and failure-example tables.
- `tables/api_gpt_5_5_test100_results.md`: current-model 100-episode `gpt-5.5` sweep.
- `tables/api_gpt_5_5_test100/`: detailed `gpt-5.5` current-model main, category, paired-difference, and failure-example tables.
- `tables/current_model_sweep.md`: combined GPT-4.1/GPT-5.4/GPT-5.5 comparison table.
- `tables/current_model_category_failure_modes.md`: no-API category-slice comparison showing where plain Ask-Needed still fails under current models.
- `tables/api_gpt_5_4_mini_shuffled_test100_results.md`: 100-episode `gpt-5.4-mini` shuffled-object-order robustness result.
- `tables/api_gpt_5_4_mini_shuffled_test100/`: detailed shuffled-object-order main, category, paired-difference, and failure-example tables.
- `tables/api_gpt_5_4_mini_scene_format_robustness.md`: baseline-vs-shuffled object-order sensitivity report.
- `tables/api_gpt_5_4_mini_natural_language_test100_results.md`: 100-episode `gpt-5.4-mini` compact natural-language scene robustness result.
- `tables/api_gpt_5_4_mini_natural_language_test100/`: detailed natural-language scene main, category, paired-difference, and failure-example tables.
- `tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md`: baseline-vs-natural-language scene sensitivity report.

Older `api_smoke*`, current-model smoke files, and `api_eval_100_results.md` files are retained as development traces, not paper evidence.

## Figures

- `figures/api_main_net_utility.svg`
- `figures/api_category_net_utility.svg`
- `figures/current_model_category_net_utility.svg`
- `figures/api_calibration_ask_rate.svg`
- `figures/cost_sensitivity_ask_cost.svg`
- `figures/cost_sensitivity_wrong_cost.svg`
- `figures/FIGURE_INDEX.md`

## Audit

- `audits/scenario_audit_packet.md`: 100 stratified scenarios for author review.
- `audits/question_audit_packet.md`: 100 sampled clarification questions for author review.
- `audits/scenario_audit_completed.md`: completed scenario verdicts.
- `audits/question_audit_completed.md`: completed question verdicts.
- `audits/AUDIT_SUMMARY.md`: compact audit result summary.
- `audits/AUDIT_INDEX.md`

## Reproducibility

Regenerate the manifest with:

```bash
conda run -n ask_dont_guess python -m unittest discover -s tests
conda run -n ask_dont_guess python src/make_ambiguity_mix_shift.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --out data/runs/ambiguity_mix_shift_results.jsonl --eval-splits test,ood_ambiguity_mix
conda run -n ask_dont_guess python src/ambiguity_mix_shift_analysis.py
conda run -n ask_dont_guess python src/api_utility_sensitivity.py
conda run -n ask_dont_guess python src/api_ecu_margin_analysis.py
conda run -n ask_dont_guess python src/api_cache_replay_verification.py
conda run -n ask_dont_guess python src/simulated_user_audit.py
conda run -n ask_dont_guess python src/api_subset_stability.py
conda run -n ask_dont_guess python src/ambiguity_utility_diagnostic.py
conda run -n ask_dont_guess python src/situated_contrast_analysis.py
conda run -n ask_dont_guess python src/make_audit_packet.py
conda run -n ask_dont_guess python src/complete_audit_packet.py
mkdir -p data/external
curl -L https://raw.githubusercontent.com/zt991211/CLAMBER/main/clamber_benchmark.jsonl -o data/external/clamber_benchmark.jsonl
conda run -n ask_dont_guess python src/clamber_external_sanity.py
conda run -n ask_dont_guess python src/paper_consistency_audit.py
conda run -n ask_dont_guess python src/verify_claims.py
conda run -n ask_dont_guess python src/make_submission_readiness_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py --manifest-only
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
conda run -n ask_dont_guess python src/audit_supplement_release.py
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
```

The test suite covers expected-utility decisions, action-equivalence rewards, hidden-owner redaction, and cache-only API replay. The final 100-episode API result, auxiliary CoT result, and 50-episode style-stress result have cache-only replay paths documented in `reproducibility.md`; they fail on cache miss instead of making network calls.
