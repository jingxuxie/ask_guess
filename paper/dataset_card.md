# Clarify-to-Act Dataset Card

This generated card summarizes the canonical synthetic benchmark data used by the current paper draft.

## Overview

| Item | Value |
| --- | --- |
| Canonical file | data/generated/episodes.jsonl |
| Total episodes | 1400 |
| Overall oracle ask rate | 0.500 |
| Style-stress file | data/generated/style_stress_episodes.jsonl |
| Style-stress episodes | 50 |
| Ambiguity-mix shift file | data/generated/ambiguity_mix_shift_episodes.jsonl |
| Ambiguity-mix shift episodes | 1280 |

## Intended Use

The dataset is intended for controlled evaluation of first-turn clarify-versus-act policies in situated instruction following. It isolates context resolution, outcome equivalence, ask cost, wrong-action cost, and hidden user intent under deterministic scoring.

## Not Intended Use

The dataset is not evidence for real household deployment, perception, long-horizon planning, or unconstrained human dialogue. It should not be used to claim broad embodied robustness without external validation.

## Splits

| Split | Episodes | Oracle ask rate | Categories |
| --- | --- | --- | --- |
| dev | 200 | 0.500 | 5 |
| ood_test | 200 | 0.500 | 5 |
| test | 400 | 0.500 | 5 |
| train | 600 | 0.500 | 5 |

## Categories

| Category | Episodes | Oracle ask rate | Variants | Diagnostic purpose |
| --- | --- | --- | --- | --- |
| context_resolved | 280 | 0.000 | active_workspace_salience | Language is underspecified, but reachability, salience, or local context makes one action utility-dominant. |
| equivalent_outcome | 280 | 0.000 | interchangeable_targets | Multiple candidates exist, but they share one success-equivalence class. |
| preference_social | 280 | 0.500 | owner_hidden, owner_visible | Owner or user preference determines whether to infer from visible context or ask. |
| referential | 280 | 1.000 | two_matching_objects | Multiple visible candidates match the instruction and wrong target matters. |
| risk_sensitive | 280 | 1.000 | high_wrong_action_cost | One candidate may be likely, but wrong-action cost makes asking utility-dominant. |

## Schema

| Record | Fields |
| --- | --- |
| Episode | ambiguity_type, ask_cost, candidate_intents, candidates_equivalent_for_success, context_resolves_instruction, episode_id, features, hidden_intent_id, oracle_clarifying_answers, oracle_should_ask, risk_level, scene, split, user_instruction, variant, wrong_action_cost |
| Scene | current_user, objects, rooms |
| Object | color, id, location, owner, reachable, salience, state, type, visible_owner |
| Candidate intent | action, intent_id, prior, success_equivalence_class, target_id |

## Actions, Costs, and Object Types

| Dimension | Values |
| --- | --- |
| Actions | bring, delete, move, put_away |
| Ask costs | 0.05, 0.10, 0.15 |
| Wrong-action costs | 0.20, 0.50, 1.00, 3.00 |
| Object types | book, bowl, box, chair, charger, cup, draft, file, folder, keys, mug, notebook, remote, water_bottle |

## Leakage Controls

| Check | Value | Purpose |
| --- | --- | --- |
| Hidden-owner preference episodes | 140 | Owners are present in the canonical JSON for scoring but marked `visible_owner=false` for API prompts. |
| Visible-owner preference episodes | 140 | `current_user` is included and object owners are visible, so `my` can be resolved without asking. |
| Hidden-owner object states | unlabeled | Hidden-owner states are neutral rather than labels such as personal or guest. |
| Hidden-owner object owner visibility | True | API prompts replace hidden owners with `unknown`. |
| Visible-owner object owner visibility | True | Visible cases keep owner information available. |

## Style-Stress Set

The style-stress set preserves hidden intents and utility labels while paraphrasing instructions and changing simulated user answer style.

| Category | Style-stress episodes | Oracle ask rate |
| --- | --- | --- |
| context_resolved | 10 | 0.000 |
| equivalent_outcome | 10 | 0.000 |
| preference_social | 10 | 0.300 |
| referential | 10 | 1.000 |
| risk_sensitive | 10 | 1.000 |

## Held-Out Ambiguity-Mix Diagnostic

This auxiliary no-API diagnostic trains and tunes offline policies on referential, context-resolved, and equivalent-outcome episodes, then tests transfer to risk-sensitive and preference/social episodes.

| Split | Category | Episodes | Oracle ask rate |
| --- | --- | --- | --- |
| dev | context_resolved | 60 | 0.000 |
| dev | equivalent_outcome | 60 | 0.000 |
| dev | referential | 60 | 1.000 |
| ood_ambiguity_mix | preference_social | 100 | 0.500 |
| ood_ambiguity_mix | risk_sensitive | 100 | 1.000 |
| test | context_resolved | 100 | 0.000 |
| test | equivalent_outcome | 100 | 0.000 |
| test | referential | 100 | 1.000 |
| train | context_resolved | 200 | 0.000 |
| train | equivalent_outcome | 200 | 0.000 |
| train | referential | 200 | 1.000 |

## Scoring

The agent receives the visible scene and instruction, then either acts immediately or asks one clarifying question. A final action succeeds if it matches the hidden intent's success-equivalence class. Net reward is task success minus clarification cost and wrong-action cost.

## Known Limitations

- Synthetic scenes and deterministic simulated answers.
- No perception, physics, or long-horizon planning.
- Generated candidate priors and costs are part of the controlled benchmark design.
- Author audits are sanity checks, not independent human-subject validation.