# Claim Scope and Reviewer Risk Report

This generated report is a writing guardrail. It separates claims supported by the current evidence package from claims that would overreach.

## Status

| Item | Value |
| --- | --- |
| Claim verification | PASS |
| Headline API model | gpt-4.1-mini |
| Headline API episodes | 100 stratified test episodes |
| Auxiliary stress evidence | 50 style-stress episodes; 25 gpt-4.1-nano episodes; offline held-out ambiguity-mix diagnostic |

## Supported Claims

| Safe claim | Recommended wording | Evidence | Avoid |
| --- | --- | --- | --- |
| Clarification is a utility-sensitive situated decision. | Use as the central thesis. | Ambiguity/utility diagnostic shows all 400 test episodes are surface-ambiguous while only half should ask; situated contrast slices show context, ownership, equivalence, and risk flipping ask/act decisions; cost sweep changes ECU ask rate. | Do not claim that ambiguity detection is useless in all settings. |
| ECU improves first-turn net utility over prompted Ask-Needed on the main API set. | Main result: ECU 0.976 vs Ask-Needed 0.632; paired delta 0.343. | data/runs/api_eval_100_corrected_results.jsonl; paired bootstrap and subset-stability tables. | Do not describe this as a universal model improvement across tasks. |
| The gap is ask timing, not inability to act after useful answers. | Ask-Needed post-answer success is 1.000 but ask recall is 0.417; ECU ask precision/recall is 1.000/1.000. | paper/tables/api_eval_100_extended/question_usefulness.md | Do not claim open-ended dialogue competence. |
| API ECU's model-derived candidate margins align on the main cached API subset. | The candidate-margin threshold agrees with the oracle ask label on 0.990 of rows; final ask/oracle agreement is 1.000 after the effective context override. | paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md | Do not treat this internal cached-row diagnostic as an independent external benchmark. |
| Private reasoning alone does not close the calibration gap. | CoT Ask-Needed utility 0.632; missed clarification 0.604. | data/runs/api_eval_100_cot_results.jsonl | Do not claim all chain-of-thought methods fail. |
| The API utility advantage survives fixed-output reward rescoring. | Cached API outputs keep positive ECU minus Ask-Needed deltas over the tested ask-cost and wrong-action-cost grid; the smallest paired bootstrap lower bound is +0.070. | paper/tables/api_eval_100_corrected/utility_sensitivity.md | Do not claim the API policy was rerun or adaptively retuned under each cost. |
| The result survives small paraphrase and answer-style stress. | Style set ECU 0.977 vs Ask-Needed 0.814. | data/runs/api_style_stress_50_results.jsonl | Do not call this broad linguistic robustness. |
| A tiny second-model check supports the direction. | gpt-4.1-nano 25: ECU 0.722 vs Ask-Needed 0.098. | data/runs/api_second_model_25_results.jsonl | Do not present this as a comprehensive model sweep. |
| The API evidence is reproducible from shipped caches. | Cache-only replay reproduces all 625 canonical API rows with zero stable-row mismatches. | paper/tables/api_cache_replay_verification.md | Do not present cache replay as a fresh model evaluation. |
| The main API advantage is not carried by a single category or episode. | Leave-one-category minimum ECU minus Ask-Needed delta is 0.190; leave-one-episode minimum is 0.307; stratified bootstrap lower bound is 0.183. | paper/tables/api_eval_100_corrected/subset_stability.md | Do not present this as a substitute for a larger paid API sweep. |
| The simulated user is visibly diagnostic in the released benchmark. | Generated oracle-ask answers resolve 1233/1233 hidden success classes, and actual API asked-row answers resolve 184/184 from visible scene fields. | paper/tables/simulated_user_audit.md | Do not claim this replaces human-response validation. |
| Author-style audits support benchmark and question sanity. | 100/100 sampled scenario labels are ok; all audited ECU oracle-ask questions are natural and diagnostic. | paper/audits/AUDIT_SUMMARY.md | Do not call this an independent human-subject study. |
| Offline controller and OOD checks support the mechanism. | Offline ECU test 0.958; OOD 0.975; held-out ambiguity-mix ECU 0.962. | data/runs/offline_results.jsonl; robustness, ambiguity-mix, and controller tables. | Do not overstate as real-world deployment robustness. |
| The learned controller has a category-transfer boundary. | With risk-sensitive and preference/social absent from training, learned-controller held-out utility is 0.950 and ask rate is 1.000. | data/runs/ambiguity_mix_shift_results.jsonl; paper/tables/ambiguity_mix_shift.md | Do not claim the learned controller generalizes to unseen ambiguity types without coverage. |
| CLAMBER provides external motivation for clarification calibration. | Provided CLAMBER ambiguity prediction recall is 0.284 against `require_clarification`, with missed clarification rate 0.716. | paper/tables/clamber_external_sanity.md | Do not present this as a Clarify-to-Act method transfer result. |

## Reviewer Risk Register

| Risk | Severity | How to frame | Boundary |
| --- | --- | --- | --- |
| Synthetic benchmark | High | Frame as controlled diagnostic benchmark; emphasize deterministic rewards and category design. | Do not claim physical robot deployment or real household generalization. |
| Single headline API model | Medium | Use gpt-4.1-mini as headline and gpt-4.1-nano as auxiliary direction check. | Broader model sweep remains future work. |
| Small paid API subset | Medium | Report paired CIs, subset-stability checks, full offline splits, cache-only replay, and style-stress set. | Do not hide that the main API set is 100 episodes. |
| Category-shift learning boundary | Medium | Use the held-out ambiguity-mix diagnostic to separate ECU's rule-based transfer from learned-controller over-asking. | Do not present the learned controller as robust to unseen ambiguity categories. |
| External CLAMBER sanity check | Low | Use as motivation that query-level ambiguity prediction can miss clarification needs. | Do not claim CLAMBER has situated action rewards or that ECU was evaluated on it. |
| Fixed-output API cost sensitivity | Low | Use to show the observed API outputs are not fragile to one reward parameter setting. | Do not imply decisions were recomputed under new costs. |
| Simulated user | Medium | State that answers are deterministic, visible-field diagnostic, and enable reproducible first-turn calibration. | Human interaction study is not included. |
| ECU uses generated candidate probabilities | Medium | Present as a controller around frozen LLM candidates, with ablations of equivalence safeguards. | Do not imply model weights were trained. |
| Action scoring aliases | Low | Document that aliases normalize surface verbs to benchmark actions and are tested. | Do not use overly broad aliases that collapse distinct actions. |
| Author audit rather than independent human evaluation | Medium | Use as sanity audit only; keep deterministic metrics as primary evidence. | Do not call it a human study. |

## Claims Not Supported

| Do not claim | Reason |
| --- | --- |
| Real-world embodied performance | No perception, physics, long-horizon planning, or human-in-the-loop deployment is evaluated. |
| General dialogue mastery | Episodes are one ask-or-act decision plus one answer before final action. |
| Model training breakthrough | The learned component is a lightweight controller; API model weights are frozen. |
| Broad model robustness | Only one headline model and one tiny second-model sanity check are included. |
| Learned-controller category transfer | When trained without risk-sensitive and preference/social categories, the controller over-asks held-out preference/social cases. |
| External benchmark transfer | CLAMBER analysis uses the dataset's provided ambiguity prediction, not a Clarify-to-Act agent running in CLAMBER. |
| Human preference validation | The user model is deterministic; author audits check coherence and question naturalness. |

## Evidence That Would Upgrade the Claim

| Upgrade | Concrete next evidence |
| --- | --- |
| Broader model sweep | Repeat the 100-episode API set on 2-3 additional model families. |
| Human/user study | Ask humans to answer sampled clarification questions and rate whether questions are necessary. |
| External transfer | Map a small CLAMBER or situated-instruction subset into ask/act utility labels. |
| Realistic action backend | Connect the first-turn ask/act policy to a simulator or tool environment with irreversible actions. |
