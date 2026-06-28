# Clarify-to-Act Results Summary

Generated: 2026-06-27

## What Exists

- A synthetic situated-instruction benchmark with 5 categories:
  - referential ambiguity,
  - context-resolved underspecification,
  - equivalent-outcome underspecification,
  - risk-sensitive ambiguity,
  - preference/social ambiguity.
- Deterministic environment scoring with net utility, success, ask rate, missed clarification, unnecessary clarification, and bootstrap CIs.
- Offline baselines and controllers:
  - `direct_act`
  - `ask_always`
  - `raw_ambiguity`
  - `prompted_heuristic`
  - `ecu`
  - `ecu_threshold`
  - `learned_controller`
- API policies with cached OpenAI Responses API calls:
  - `api_direct_act`
  - `api_ask_needed`
  - `api_ask_needed_cot`
  - `api_ecu`
- A 50-episode API paraphrase and answer-style stress set derived from the test split.

The preference/social category was fixed during iteration to avoid benchmark leakage:

- target IDs are neutral, for example `pref_book_black_389_a`;
- hidden-owner cases redact object owners from API prompts;
- hidden-owner cases use neutral object states rather than leaking labels like `personal` or `guest`;
- visible-owner cases include `current_user`, making "my" resolvable when owner information is visible.

## Dataset

Current generated dataset: `data/generated/episodes.jsonl`

| Split | Episodes |
| --- | ---: |
| train | 600 |
| dev | 200 |
| test | 400 |
| ood_test | 200 |

The dataset is balanced across the 5 categories. Overall oracle ask rate is 0.50.

Benchmark category table: `paper/tables/benchmark_categories.md`

| Category | Episodes | Oracle ask | Expected behavior |
| --- | ---: | ---: | --- |
| Referential ambiguity | 280 | 1.000 | Ask |
| Context-resolved | 280 | 0.000 | Act |
| Equivalent outcome | 280 | 0.000 | Act |
| Risk-sensitive | 280 | 1.000 | Ask |
| Preference/social | 280 | 0.500 | Ask iff owner hidden |

Qualitative example table: `paper/tables/qualitative_examples.md`

This table gives representative examples from the canonical API subset, including context-resolved and equivalent-outcome cases where acting is optimal, and referential, hidden-preference, and high-risk cases where asking is optimal.

Ambiguity-vs-utility diagnostic: `paper/tables/ambiguity_utility_diagnostic.md`

- All 400 canonical test episodes have multiple candidate interpretations.
- Exactly 200 are oracle-act cases and 200 are oracle-ask cases.
- A surface-ambiguity policy asks on every test episode, reaching 0.920 utility with unnecessary clarification rate 1.000.
- A supervised uncertainty-only controller trained only on candidate count, top prior, and prior entropy reaches 0.900 utility, but still misses 7.0% of oracle-ask cases and asks unnecessarily in 40.0% of oracle-act cases.

Situated contrast diagnostic: `paper/tables/situated_contrast_analysis.md`

- Two-candidate `bring` cases split by situation: 80/80 context-resolved cases are oracle-act, while 80/80 referential cases are oracle-ask.
- `put_away` preference cases split by visible ownership: 40/40 visible-owner cases are oracle-act, while 40/40 hidden-owner cases are oracle-ask.
- High-entropy equivalent-outcome cases are oracle-act because all candidates share one success class; high-top-prior risk-sensitive cases are oracle-ask because wrong actions are costly.

## Offline Main Result

Source: `paper/tables/main_results.md`

| Split | Method | Net utility | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| test | direct_act | 0.498 | 0.792 | 0.000 | 1.000 | 0.000 |
| test | ask_always | 0.920 | 1.000 | 1.000 | 0.000 | 1.000 |
| test | raw_ambiguity | 0.920 | 1.000 | 1.000 | 0.000 | 1.000 |
| test | prompted_heuristic | 0.938 | 0.988 | 0.700 | 0.000 | 0.400 |
| test | ecu | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| test | ecu_threshold | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| test | learned_controller | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| ood_test | prompted_heuristic | 0.955 | 1.000 | 0.700 | 0.000 | 0.400 |
| ood_test | ecu | 0.975 | 1.000 | 0.500 | 0.000 | 0.000 |

Interpretation: success-only metrics hide the over-asking problem. ECU/controller match task success while reducing unnecessary clarification.

Paired bootstrap differences over shared episodes:

- test `ecu` - `prompted_heuristic`: +0.020 net utility, 95% paired CI [0.016, 0.024]
- ood_test `ecu` - `prompted_heuristic`: +0.020 net utility, 95% paired CI [0.015, 0.026]

## API Evaluation

Source: `paper/tables/api_eval_100_corrected_results.md`

Setting: 100 stratified test episodes, 20 per category, `gpt-4.1-mini`, cached in `data/runs/api_cache.jsonl`.

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| api_direct_act | 100 | 0.420 | [0.180, 0.640] | 0.770 | 0.000 | 1.000 | 0.000 |
| api_ask_needed | 100 | 0.632 | [0.431, 0.810] | 0.880 | 0.370 | 0.583 | 0.327 |
| api_ecu | 100 | 0.976 | [0.972, 0.981] | 1.000 | 0.480 | 0.000 | 0.000 |

Category breakdown source: `paper/tables/api_eval_100_corrected/category_breakdown.md`

| Category | api_direct_act utility | api_ask_needed utility | api_ecu utility | api_ecu ask rate | Oracle ask rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| context_resolved | 1.000 | 0.993 | 1.000 | 0.000 | 0.000 |
| preference_social | 0.400 | 0.400 | 0.980 | 0.400 | 0.400 |
| equivalent_outcome | 1.000 | 0.920 | 1.000 | 0.000 | 0.000 |
| referential | -0.100 | 0.857 | 0.950 | 1.000 | 1.000 |
| risk_sensitive | -0.200 | -0.008 | 0.950 | 1.000 | 1.000 |

Interpretation:

- DirectAct fails because guessing is punished in true ambiguity and high-risk cases.
- Prompted ask-needed improves referential cases but misses most risk-sensitive clarifications and over-asks equivalent-outcome cases.
- API ECU is calibrated to task utility: it asks in referential/risk-sensitive cases, avoids equivalent/context-resolved cases, and matches the oracle ask rate in preference/social cases.

Paired bootstrap differences over the same 100 API episodes:

- `api_ecu` - `api_ask_needed`: +0.343 net utility, 95% paired CI [0.168, 0.559]
- `api_ecu` - `api_direct_act`: +0.556 net utility, 95% paired CI [0.355, 0.792]
- `api_ask_needed` - `api_direct_act`: +0.212 net utility, 95% paired CI [0.077, 0.350]

Subset stability source: `paper/tables/api_eval_100_corrected/subset_stability.md`

- ECU - AskNeeded point estimate is positive in every category.
- Leave-one-category minimum ECU - AskNeeded delta is +0.190.
- Leave-one-episode minimum ECU - AskNeeded delta is +0.307.
- Stratified bootstrap CI for ECU - AskNeeded is [0.183, 0.541].

Auxiliary private-reasoning baseline source: `paper/tables/api_eval_100_extended/main_results.md`

- `api_ask_needed_cot`: 0.632 net utility, 0.890 success, 0.370 ask rate, 0.604 missed clarification, 0.346 unnecessary clarification
- `api_ecu` - `api_ask_needed_cot`: +0.344 net utility, 95% paired CI [0.171, 0.564]

Interpretation: prompting the model to reason privately before emitting JSON does not close the calibration gap; it keeps the same net utility as plain Ask-Needed and still misses most risk-sensitive clarifications.

## API ECU Ablation

Source: `paper/tables/api_eval_100_corrected/ecu_ablation.md`

This no-API ablation replays cached GPT-4.1-mini candidate interpretations from the final API evaluation. The current-rule replay matches actual API ECU ask decisions and rewards on 100/100 episodes.

Key pattern:

- Current ECU decision rule: 0.976 net utility, 1.000 success, 0.480 ask rate
- No equivalence guard: 0.745 net utility, 0.890 success, 0.375 missed clarification
- No equivalence collapse: 0.956 net utility, 1.000 success, 0.385 unnecessary clarification
- No margin/context dampening: 0.968 net utility, 1.000 success, 0.250 unnecessary clarification

Interpretation: the conservative equivalence guard is necessary in both directions. It prevents unsafe over-collapsing when the model incorrectly marks true ambiguity as equivalent, while still allowing action in genuine equivalent-outcome cases.

## Utility-Margin Calibration

Sources:

- `paper/tables/api_eval_100_corrected/calibration_by_margin.md`
- `paper/tables/api_style_stress_50/calibration_by_margin.md`

The calibration analysis bins episodes by the oracle expected-utility margin `EU(ask) - EU(act)`.

Main 100-episode API set:

- In act-preferred cases, ECU asks on 0.000 of episodes; prompted Ask-Needed asks on 0.425.
- In ask-preferred cases, ECU asks on 1.000 of episodes; prompted Ask-Needed asks on 0.417.
- ECU reaches 0.950 net utility in ask-preferred cases, compared with 0.271 for prompted Ask-Needed and -0.208 for DirectAct.

50-episode paraphrase/style stress set:

- In act-preferred cases, ECU asks on 0.000 of episodes; prompted Ask-Needed asks on 0.350.
- In ask-preferred cases, ECU asks on 1.000 of episodes; prompted Ask-Needed asks on 0.522.

Interpretation: prompted Ask-Needed is not calibrated to the value of information; it asks at similar rates when asking is harmful and when asking is useful. ECU directly tracks the utility margin.

API ECU internal candidate-margin diagnostic:

Source: `paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md`

- The cached API ECU rows all include model-derived candidate utility margins.
- The raw candidate-margin threshold agrees with the oracle ask label on 0.990 of rows.
- After the effective context override, final API ECU ask/oracle agreement is 1.000 on the 100-episode API subset.
- This is an internal calibration check for the API ECU pipeline, not an independent benchmark.

## Failure Taxonomy

Sources:

- `paper/tables/api_eval_100_extended/failure_taxonomy.md`
- `paper/tables/api_eval_100_extended/question_usefulness.md`
- `paper/tables/api_style_stress_50/failure_taxonomy.md`
- `paper/tables/api_style_stress_50/question_usefulness.md`

A failure event is any wrong final action or ask/act decision that disagrees with the utility oracle. This counts successful-but-unnecessary questions and lucky unsafe guesses as calibration failures.

Main API set plus private-reasoning baseline:

- DirectAct: 48 failure events / 100 rows.
- Prompted Ask-Needed: 45 failure events / 100 rows.
- Private-reasoning Ask-Needed: 47 failure events / 100 rows.
- ECU: 0 failure events / 100 rows.
- Top failure modes: risk blindness (57), equivalence blindness (33), referential guessing (25).

50-episode paraphrase/style stress set:

- DirectAct: 23 failure events / 50 rows.
- Prompted Ask-Needed: 18 failure events / 50 rows.
- ECU: 0 failure events / 50 rows.
- Top failure modes: referential guessing (18), risk blindness (10), equivalence blindness (7).

Interpretation: prompting fails in qualitatively different ways: it can still guess under true ambiguity, ignore high-stakes uncertainty, and ask unnecessary questions when outcomes are equivalent. ECU removes those first-turn calibration failures on the evaluated API sets.

Question-usefulness diagnostics show that the issue is when to ask, not post-answer grounding after a question is asked:

- Main API set: ECU ask precision / recall / post-answer success are 1.000 / 1.000 / 1.000; prompted Ask-Needed is 0.541 / 0.417 / 1.000.
- Style-stress set: ECU is 1.000 / 1.000 / 1.000; prompted Ask-Needed is 0.632 / 0.522 / 1.000.

## Cost Sensitivity

Source: `paper/tables/cost_sensitivity.md`

Key pattern:

- When ask cost is low (`0.01`) and wrong-action cost is fixed at `1.0`, ECU asks on 0.800 of test cases and reaches net utility 0.992.
- When ask cost is high (`0.35`) and wrong-action cost is fixed at `1.0`, ECU ask rate drops to 0.455 and net utility is 0.791.
- Prompted heuristic keeps ask rate fixed at 0.700 across those ask-cost settings and loses utility.
- When wrong-action cost rises from `0.2` to `3.0`, DirectAct drops from 0.751 to 0.170 net utility, while ECU stays near 0.96 by asking on high-stakes cases.

Interpretation: this supports the central thesis that clarification is utility-dependent, not just ambiguity-dependent.

## Cached API Utility Sensitivity

Source: `paper/tables/api_eval_100_corrected/utility_sensitivity.md`

Setting: no-API fixed-output rescoring of the final 100-episode GPT-4.1-mini API outputs. The model is not rerun and policy decisions do not change; rewards and oracle ask labels are recomputed under alternate global ask/wrong-action costs.

Key pattern:

- Ask-cost sweep with wrong-action cost fixed at `1.0`: ECU - AskNeeded remains positive from +0.239 at ask cost `0.01` to +0.201 at ask cost `0.35`.
- Wrong-action-cost sweep with ask cost fixed at `0.05`: ECU - AskNeeded remains positive from +0.138 at wrong cost `0.2` to +0.475 at wrong cost `3.0`.
- Paired bootstrap intervals stay above zero throughout the grid; the smallest lower bound is +0.070.

Interpretation: the main API advantage is not an artifact of a single narrow reward parameterization. This is weaker than adaptive cost-aware rerunning, but it is a useful robustness check over the cached API outputs.

## Robustness

Source: `paper/tables/robustness_breakdown.md`

Controller analysis source: `paper/tables/controller_analysis.md`

The 200-episode OOD split keeps all five diagnostic categories and shifts object types where the generator supports it. In that split, 102 episodes contain at least one held-out object type.

Key pattern:

- `ecu`: test 0.958 net utility, OOD 0.975, OOD held-out-object slice 0.975
- `learned_controller`: test 0.958 net utility, OOD 0.975, OOD held-out-object slice 0.975
- `prompted_heuristic`: test 0.938 net utility, OOD 0.955, OOD held-out-object slice 0.975

Interpretation: the offline ECU/controller result is not driven by memorized object types in the generated train/dev/test object pool, although the stronger API robustness claim remains future work.

The learned controller is interpretable: its largest positive weight is the oracle-free expected-utility margin proxy available from generated candidates, with additional positive weights on risk and entropy; context resolution, candidate equivalence, salience gap, top prior, and ask cost push it toward acting.

## Held-Out Ambiguity-Mix Diagnostic

Source: `paper/tables/ambiguity_mix_shift.md`

Setting: no-API offline diagnostic with train/dev/test episodes drawn only from referential, context-resolved, and equivalent-outcome categories. The held-out split contains risk-sensitive and preference/social categories.

| Method | Seen-test utility | Held-out utility | Held-out - seen | Seen ask | Held-out ask |
| --- | ---: | ---: | ---: | ---: | ---: |
| prompted_heuristic | 0.930 | 0.962 | 0.032 | 0.667 | 0.750 |
| ecu | 0.963 | 0.962 | -0.001 | 0.333 | 0.750 |
| ecu_threshold | 0.963 | 0.950 | -0.013 | 0.333 | 1.000 |
| learned_controller | 0.963 | 0.950 | -0.013 | 0.333 | 1.000 |

Interpretation: ECU transfers cleanly to the held-out ambiguity mix because the decision rule uses costs, priors, context, and equivalence directly. The learned controller and tuned threshold over-ask held-out preference/social cases when that category is absent from train/dev, which is a useful claim boundary: the controller is transparent and strong when the diagnostic categories are covered, but should not be described as robust to unseen ambiguity types.

## External CLAMBER Sanity Check

Source: `paper/tables/clamber_external_sanity.md`

Setting: public CLAMBER benchmark JSONL, mapped from `require_clarification` to an ASK label. This uses the CLAMBER file's provided `predict_ambiguous` field as a query-level ambiguity-detector prediction. It does not run a Clarify-to-Act agent and should be used only as external motivation.

| N | Oracle ask | Predicted ask | Accuracy | Precision | Recall | Missed clarif. | Unnecessary clarif. |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3202 | 0.500 | 0.246 | 0.538 | 0.577 | 0.284 | 0.716 | 0.208 |

Interpretation: the provided query-level ambiguity prediction substantially under-asks relative to CLAMBER's clarification labels, especially in multi-constraint cases. This supports the paper motivation that clarification should be studied as an ask/act calibration problem, but it is not evidence of situated task utility.

## API Paraphrase and Answer-Style Stress Test

Source: `paper/tables/api_style_stress_50/main_results.md`

Setting: 50 stratified test-derived episodes, 10 per category. The stress set paraphrases the user instruction and changes simulated user answers to a terser, location/owner-style phrasing while preserving hidden intents and utility labels. It reuses `gpt-4.1-mini` with cache-only replay available after the initial bounded run.

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| api_direct_act | 50 | 0.320 | [-0.080, 0.680] | 0.760 | 0.000 | 1.000 | 0.000 |
| api_ask_needed | 50 | 0.814 | [0.654, 0.945] | 0.920 | 0.380 | 0.478 | 0.259 |
| api_ecu | 50 | 0.977 | [0.970, 0.984] | 1.000 | 0.460 | 0.000 | 0.000 |

Paired bootstrap differences:

- `api_ecu` - `api_ask_needed`: +0.163 net utility, 95% paired CI [0.040, 0.321]
- `api_ecu` - `api_direct_act`: +0.657 net utility, 95% paired CI [0.342, 1.017]

Interpretation: the main API pattern survives paraphrased instructions and shifted user-answer style. Prompted Ask-Needed improves over DirectAct but still misses nearly half of oracle clarification cases and over-asks equivalent-outcome cases; ECU remains calibrated on this small stress set.

## Auxiliary Second-Model Sanity Check

Source: `paper/tables/api_second_model_25/main_results.md`

Setting: 25 stratified test episodes, 5 per category, `gpt-4.1-nano`, cached separately in `data/runs/api_second_model_cache.jsonl`.

| Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| api_direct_act | 25 | 0.040 | [-0.520, 0.600] | 0.640 | 0.000 | 1.000 | 0.000 |
| api_ask_needed | 25 | 0.098 | [-0.456, 0.586] | 0.680 | 0.240 | 0.909 | 0.357 |
| api_ecu | 25 | 0.722 | [0.412, 0.954] | 0.880 | 0.560 | 0.182 | 0.357 |

Paired bootstrap differences:

- `api_ecu` - `api_ask_needed`: +0.624 net utility, 95% paired CI [0.074, 1.254]
- `api_ecu` - `api_direct_act`: +0.682 net utility, 95% paired CI [0.202, 1.248]

Interpretation: this is a small model-coverage sanity check, not a broad model sweep. The direction matches the main result, especially on risk-sensitive cases, but the weaker model over-asks equivalent-outcome cases and still misses some referential clarifications.

## Current Artifacts

- Dataset: `data/generated/episodes.jsonl`
- Held-out ambiguity-mix dataset: `data/generated/ambiguity_mix_shift_episodes.jsonl`
- Dataset card: `paper/dataset_card.md`
- Offline results: `data/runs/offline_results.jsonl`
- Ambiguity-vs-utility diagnostic: `paper/tables/ambiguity_utility_diagnostic.md`
- Situated contrast diagnostic: `paper/tables/situated_contrast_analysis.md`
- Held-out ambiguity-mix results: `data/runs/ambiguity_mix_shift_results.jsonl`
- CLAMBER external sanity table: `paper/tables/clamber_external_sanity.md`
- Paper consistency audit: `paper/paper_consistency_audit.md`
- API evaluation results: `data/runs/api_eval_100_corrected_results.jsonl`
- Auxiliary CoT API results: `data/runs/api_eval_100_cot_results.jsonl`
- API style-stress results: `data/runs/api_style_stress_50_results.jsonl`
- Auxiliary second-model API results: `data/runs/api_second_model_25_results.jsonl`
- API cache: `data/runs/api_cache.jsonl`
- Auxiliary second-model API cache: `data/runs/api_second_model_cache.jsonl`
- Tables:
  - `paper/tables/main_results.md`
  - `paper/tables/benchmark_categories.md`
  - `paper/tables/category_breakdown.md`
  - `paper/tables/paired_differences.md`
  - `paper/tables/robustness_breakdown.md`
  - `paper/tables/controller_analysis.md`
  - `paper/tables/ambiguity_mix_shift.md`
  - `paper/tables/clamber_external_sanity.md`
  - `paper/tables/simulated_user_audit.md`
  - `paper/tables/cost_sensitivity.md`
  - `paper/tables/api_eval_100_corrected_results.md`
  - `paper/tables/api_eval_100_corrected/category_breakdown.md`
  - `paper/tables/api_eval_100_corrected/paired_differences.md`
  - `paper/tables/api_eval_100_corrected/subset_stability.md`
  - `paper/tables/api_eval_100_corrected/ecu_ablation.md`
  - `paper/tables/api_eval_100_corrected/utility_sensitivity.md`
  - `paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md`
  - `paper/tables/api_cache_replay_verification.md`
  - `paper/tables/api_eval_100_corrected/calibration_by_margin.md`
  - `paper/tables/api_eval_100_corrected/failure_examples.md`
  - `paper/tables/api_eval_100_cot_results.md`
  - `paper/tables/api_eval_100_cot/main_results.md`
  - `paper/tables/api_eval_100_cot/category_breakdown.md`
  - `paper/tables/api_eval_100_extended/main_results.md`
  - `paper/tables/api_eval_100_extended/category_breakdown.md`
  - `paper/tables/api_eval_100_extended/paired_differences.md`
  - `paper/tables/api_eval_100_extended/failure_taxonomy.md`
  - `paper/tables/api_eval_100_extended/question_usefulness.md`
  - `paper/tables/api_style_stress_50_results.md`
  - `paper/tables/api_style_stress_50/main_results.md`
  - `paper/tables/api_style_stress_50/category_breakdown.md`
  - `paper/tables/api_style_stress_50/paired_differences.md`
  - `paper/tables/api_style_stress_50/calibration_by_margin.md`
  - `paper/tables/api_style_stress_50/failure_taxonomy.md`
  - `paper/tables/api_style_stress_50/question_usefulness.md`
  - `paper/tables/api_second_model_25/main_results.md`
  - `paper/tables/api_second_model_25/paired_differences.md`
  - `paper/tables/scenario_samples.md`
- Figures:
  - `paper/figures/api_main_net_utility.svg`
  - `paper/figures/api_category_net_utility.svg`
  - `paper/figures/api_calibration_ask_rate.svg`
  - `paper/figures/cost_sensitivity_ask_cost.svg`
  - `paper/figures/cost_sensitivity_wrong_cost.svg`
  - `paper/figures/FIGURE_INDEX.md`
- Draft and audit:
  - `paper/clarify_to_act_paper_draft.md`
  - `paper/dataset_card.md`
  - `paper/claim_verification.md`
  - `paper/claim_scope.md`
  - `paper/reproducibility.md`
  - `paper/submission_readiness.md`
  - `paper/supplement_manifest.md`
  - `paper/supplement_audit.md`
  - `paper/clarify_to_act_supplement.zip`
  - `paper/references.md`
  - `paper/latex/main.tex`
  - `paper/latex/refs.bib`
  - `paper/latex/main.pdf`
  - `paper/audits/AUDIT_INDEX.md`
  - `paper/audits/AUDIT_SUMMARY.md`
  - `paper/audits/scenario_audit_packet.md`
  - `paper/audits/question_audit_packet.md`
  - `paper/audits/scenario_audit_completed.md`
  - `paper/audits/question_audit_completed.md`

## Author Audit

Completed audit source: `paper/audits/AUDIT_SUMMARY.md`

- Scenarios reviewed: 100
- Scenario verdicts: 100 `ok`, 0 `minor_issue`, 0 `bad_label`
- Questions reviewed: 100
- Question verdicts: 73 `ok`, 19 `minor_issue`, 8 `bad_question`

Interpretation: sampled scenario labels are coherent. All audited ECU oracle-ask questions are natural and diagnostic. The question issues are primarily expected prompted-baseline failures where the model asks natural but unnecessary questions, or asks extra table/preference questions, in oracle-act equivalent-outcome and context-resolved cases.

## Simulated User Answer Audit

Source: `paper/tables/simulated_user_audit.md`

- Generated oracle-ask diagnostic answers resolve the hidden success class from visible scene fields in 1233/1233 cases.
- Actual API asked-row answers resolve the hidden success class in 184/184 stored asked rows.

Interpretation: the deterministic simulated user is reproducible and visibly diagnostic in the released benchmark. This reduces a benchmark-quality risk, but it is not a human-response study.

## Claim Scope

Claim-scope source: `paper/claim_scope.md`

Interpretation: the safe writing claim is value-of-information calibration for first-turn clarify-vs-act decisions in a controlled synthetic benchmark. The report explicitly warns against overclaiming real-world embodied performance, broad model robustness, human preference validation, or model-weight training.

## API Usage

Current cache totals:

- cached responses: 914
- input tokens: 271,208
- output tokens: 49,117
- total tokens: 320,325

This is comfortably within the stated `$10` budget for a mini model.

## LaTeX Package

Source: `paper/latex/main.tex`

- Style: local `colm2026_conference.sty`
- Bibliography: `paper/latex/refs.bib` with full author lists for cited related work
- Build command: `latexmk -pdf -interaction=nonstopmode main.tex`
- Verified output: `paper/latex/main.pdf`
- PDF length: 7 pages
- Final compile log: no unresolved references or citations
- Safe API replay: `paper/tables/api_cache_replay_verification.md` verifies that cache-only replay reproduces all 625 canonical API rows across the main, CoT, style-stress, and second-model results with zero stable-row mismatches and no network calls
- Claim verification: `conda run -n ask_dont_guess python src/verify_claims.py` reports `PASS`
- Submission readiness: `conda run -n ask_dont_guess python src/make_submission_readiness_report.py` writes the current claim-to-evidence map and limitations checklist
- Supplement archive: `conda run -n ask_dont_guess python src/make_supplement_package.py` writes `paper/clarify_to_act_supplement.zip`
- Supplement audit: `conda run -n ask_dont_guess python src/audit_supplement_release.py` checks forbidden files, local paths, API-key-like secrets, stale traces, and archive membership

## Recommended Next Steps

1. Treat the current benchmark schema, prompts, API ECU margin (`0.075`), visibility redaction, and equivalence guard as frozen for the first submission draft.
2. Optional: run a second model or larger stratified API set only after reviewer-style reading identifies a concrete gap.
