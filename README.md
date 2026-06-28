# Clarify-to-Act

Minimal benchmark and experiment scaffold for **Ask, Don't Guess: Learning When to Clarify in Situated Instruction Following**.

The current implementation is intentionally cheap to run:

- Generates synthetic situated instruction episodes with hidden intents.
- Computes oracle ask/act labels from expected communicative utility.
- Evaluates deterministic offline baselines before any API spending.
- Trains a small stdlib-only logistic ask/act controller.
- Writes paper-ready Markdown result tables.

## Quick Start

```bash
conda run -n ask_dont_guess python src/generate_scenarios.py --train 600 --dev 200 --test 400 --ood-test 200 --out data/generated/episodes.jsonl
conda run -n ask_dont_guess python src/inspect_scenarios.py --episodes data/generated/episodes.jsonl --out paper/tables/scenario_samples.md
conda run -n ask_dont_guess python src/qualitative_examples.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/qualitative_examples.md
conda run -n ask_dont_guess python src/make_dataset_card.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/offline_results.jsonl
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/offline_results.jsonl --out-dir paper/tables
conda run -n ask_dont_guess python src/robustness_analysis.py --episodes data/generated/episodes.jsonl --results data/runs/offline_results.jsonl --out paper/tables/robustness_breakdown.md
conda run -n ask_dont_guess python src/api_ecu_ablation.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/ecu_ablation.md
conda run -n ask_dont_guess python src/api_utility_sensitivity.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/utility_sensitivity.md
conda run -n ask_dont_guess python src/api_ecu_margin_analysis.py --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md
conda run -n ask_dont_guess python src/api_cache_replay_verification.py --out paper/tables/api_cache_replay_verification.md
conda run -n ask_dont_guess python src/simulated_user_audit.py --out paper/tables/simulated_user_audit.md
conda run -n ask_dont_guess python src/api_subset_stability.py --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/subset_stability.md
conda run -n ask_dont_guess python src/ambiguity_utility_diagnostic.py --out paper/tables/ambiguity_utility_diagnostic.md
conda run -n ask_dont_guess python src/situated_contrast_analysis.py --out paper/tables/situated_contrast_analysis.md
conda run -n ask_dont_guess python src/make_ambiguity_mix_shift.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --out data/runs/ambiguity_mix_shift_results.jsonl --eval-splits test,ood_ambiguity_mix
conda run -n ask_dont_guess python src/ambiguity_mix_shift_analysis.py
conda run -n ask_dont_guess python src/make_audit_packet.py
conda run -n ask_dont_guess python src/complete_audit_packet.py
mkdir -p data/external
curl -L https://raw.githubusercontent.com/zt991211/CLAMBER/main/clamber_benchmark.jsonl -o data/external/clamber_benchmark.jsonl
conda run -n ask_dont_guess python src/clamber_external_sanity.py
conda run -n ask_dont_guess python src/paper_consistency_audit.py
conda run -n ask_dont_guess python -m unittest discover -s tests
conda run -n ask_dont_guess python src/verify_claims.py
conda run -n ask_dont_guess python src/make_claim_scope_report.py
conda run -n ask_dont_guess python src/make_submission_readiness_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py --manifest-only
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
conda run -n ask_dont_guess python src/audit_supplement_release.py
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
```

For a very fast smoke test:

```bash
conda run -n ask_dont_guess python src/generate_scenarios.py --train 80 --dev 40 --test 80 --out data/generated/smoke_episodes.jsonl
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/smoke_episodes.jsonl --out data/runs/smoke_offline_results.jsonl
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/smoke_offline_results.jsonl --out-dir paper/tables/smoke
```

## Current Baselines

- `direct_act`: acts on the highest-prior interpretation and never asks.
- `ask_always`: always asks one question, then acts using the simulated answer.
- `raw_ambiguity`: asks whenever multiple candidate targets exist.
- `prompted_heuristic`: a hand-coded proxy for "ask when needed" prompting.
- `ecu`: expected communicative utility using generated priors and costs.
- `ecu_threshold`: tunes the ECU ask margin threshold on dev.
- `learned_controller`: stdlib logistic controller trained from interaction-derived oracle labels.

These are not the final API LLM policies. They are a low-cost validation layer for the benchmark mechanics and expected paper story.

## Reproducibility

The canonical artifact manifest is `paper/reproducibility.md`. It records dataset/result hashes, recomputed metrics, API cache token totals, and exact reproduction commands. `paper/claim_verification.md` recomputes headline paper claims from the canonical artifacts and should report `PASS`. `paper/paper_consistency_audit.md` checks that paper-facing text contains the verified headline numbers and scope caveats. `paper/claim_scope.md` is the generated writing guardrail for supported claims and reviewer-risk boundaries. `paper/supplement_audit.md` checks the release package for forbidden files, local paths, and API-key-like secrets.

Core benchmark and API replay invariants are covered by a stdlib test suite:

```bash
conda run -n ask_dont_guess python -m unittest discover -s tests
```

The final API evaluation can be replayed without network calls or API spending:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_corrected_replay.jsonl --summary-out /tmp/api_eval_100_corrected_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

The 50-episode paraphrase and answer-style stress result can also be replayed from cache:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out /tmp/api_style_stress_50_replay.jsonl --summary-out /tmp/api_style_stress_50_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

`--cache-only` fails on any cache miss, so prompt or code drift cannot silently create new paid API calls.

The auxiliary private-reasoning API baseline is cached in `data/runs/api_eval_100_cot_results.jsonl` and summarized in `paper/tables/api_eval_100_extended/`.
The style-stress result is summarized in `paper/tables/api_style_stress_50/`.
The auxiliary 25-episode `gpt-4.1-nano` sanity check is cached in `data/runs/api_second_model_25_results.jsonl` and summarized in `paper/tables/api_second_model_25/`.
The current-model 100-episode sweeps are cached in `data/runs/api_gpt_5_4_mini_test100_results.jsonl` and `data/runs/api_gpt_5_5_test100_results.jsonl`, with combined summary `paper/tables/current_model_sweep.md`.
The `gpt-5.4-mini` scene-serialization robustness checks are cached in `data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl` and `data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl`, with paired summaries in `paper/tables/api_gpt_5_4_mini_scene_format_robustness.md` and `paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md`.
The no-API held-out ambiguity-mix diagnostic is in `data/generated/ambiguity_mix_shift_episodes.jsonl` and `data/runs/ambiguity_mix_shift_results.jsonl`, with summary table `paper/tables/ambiguity_mix_shift.md`.
The no-API ambiguity-vs-utility diagnostic is summarized in `paper/tables/ambiguity_utility_diagnostic.md`; the situated contrast slices are summarized in `paper/tables/situated_contrast_analysis.md`.
The CLAMBER external sanity check is summarized in `paper/tables/clamber_external_sanity.md`; it uses a locally downloaded public CLAMBER JSONL and does not make OpenAI API calls.

## Supplement Package

Build the deterministic release archive with:

```bash
conda run -n ask_dont_guess python src/make_supplement_package.py
```

The archive is written to `paper/clarify_to_act_supplement.zip`. Its file list and exclusion policy are recorded in `paper/supplement_manifest.md`; API keys, bytecode, LaTeX intermediates, and older smoke-run traces are excluded.
