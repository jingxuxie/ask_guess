# Claim Verification Report

Overall status: **PASS**

This report recomputes headline claims from the canonical JSONL artifacts and generated analysis outputs.

| Claim | Expected | Observed | Status | Evidence |
| --- | --- | --- | --- | --- |
| dataset total episodes | 1400 | 1400 | PASS | data/generated/episodes.jsonl |
| dataset split counts | {'dev': 200, 'ood_test': 200, 'test': 400, 'train': 600} | {'dev': 200, 'ood_test': 200, 'test': 400, 'train': 600} | PASS | data/generated/episodes.jsonl |
| dataset category counts | {'context_resolved': 280, 'equivalent_outcome': 280, 'preference_social': 280, 'referential': 280, 'risk_sensitive': 280} | {'context_resolved': 280, 'equivalent_outcome': 280, 'preference_social': 280, 'referential': 280, 'risk_sensitive': 280} | PASS | data/generated/episodes.jsonl |
| dataset oracle ask rate | 0.500 | 0.500 | PASS | data/generated/episodes.jsonl |
| dataset category context_resolved oracle ask rate | 0.000 | 0.000 | PASS | data/generated/episodes.jsonl |
| dataset category equivalent_outcome oracle ask rate | 0.000 | 0.000 | PASS | data/generated/episodes.jsonl |
| dataset category preference_social oracle ask rate | 0.500 | 0.500 | PASS | data/generated/episodes.jsonl |
| dataset category referential oracle ask rate | 1.000 | 1.000 | PASS | data/generated/episodes.jsonl |
| dataset category risk_sensitive oracle ask rate | 1.000 | 1.000 | PASS | data/generated/episodes.jsonl |
| style-stress total episodes | 50 | 50 | PASS | data/generated/style_stress_episodes.jsonl |
| style-stress split counts | {'style_test': 50} | {'style_test': 50} | PASS | data/generated/style_stress_episodes.jsonl |
| style-stress category counts | {'context_resolved': 10, 'equivalent_outcome': 10, 'preference_social': 10, 'referential': 10, 'risk_sensitive': 10} | {'context_resolved': 10, 'equivalent_outcome': 10, 'preference_social': 10, 'referential': 10, 'risk_sensitive': 10} | PASS | data/generated/style_stress_episodes.jsonl |
| style-stress oracle ask rate | 0.460 | 0.460 | PASS | data/generated/style_stress_episodes.jsonl |
| offline test direct_act net_utility | 0.498 | 0.498 | PASS | data/runs/offline_results.jsonl |
| offline test ask_always net_utility | 0.920 | 0.920 | PASS | data/runs/offline_results.jsonl |
| offline test prompted_heuristic net_utility | 0.938 | 0.938 | PASS | data/runs/offline_results.jsonl |
| offline test ecu net_utility | 0.958 | 0.958 | PASS | data/runs/offline_results.jsonl |
| offline test learned_controller net_utility | 0.958 | 0.958 | PASS | data/runs/offline_results.jsonl |
| offline ood_test prompted_heuristic net_utility | 0.955 | 0.955 | PASS | data/runs/offline_results.jsonl |
| offline ood_test ecu net_utility | 0.975 | 0.975 | PASS | data/runs/offline_results.jsonl |
| offline test ecu ask_rate | 0.500 | 0.500 | PASS | data/runs/offline_results.jsonl |
| offline ood_test ecu ask_rate | 0.500 | 0.500 | PASS | data/runs/offline_results.jsonl |
| ambiguity diagnostic test surface-ambiguous episodes | 400 | 400 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic test oracle-ask among surface-ambiguous | 200 | 200 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic test oracle-act among surface-ambiguous | 200 | 200 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic surface-ambiguity test net_utility | 0.920 | 0.920 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic surface-ambiguity test unnecessary_clarification_rate | 1.000 | 1.000 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic uncertainty-only test net_utility | 0.900 | 0.900 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic uncertainty-only test missed_clarification_rate | 0.070 | 0.070 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| ambiguity diagnostic uncertainty-only test unnecessary_clarification_rate | 0.400 | 0.400 | PASS | paper/tables/ambiguity_utility_diagnostic.md |
| situated contrast bring / 2 candidates / context-resolved n | 80 | 80 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast bring / 2 candidates / context-resolved oracle ask rate | 0.000 | 0.000 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast bring / 2 candidates / referential n | 80 | 80 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast bring / 2 candidates / referential oracle ask rate | 1.000 | 1.000 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast put-away preference / owner visible n | 40 | 40 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast put-away preference / owner visible oracle ask rate | 0.000 | 0.000 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast put-away preference / owner hidden n | 40 | 40 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast put-away preference / owner hidden oracle ask rate | 1.000 | 1.000 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast high entropy / equivalent outcomes mean normalized entropy | 0.998 | 0.998 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast high entropy / equivalent outcomes oracle ask rate | 0.000 | 0.000 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast high top-prior / high wrong-action cost mean top prior | 0.799 | 0.799 | PASS | paper/tables/situated_contrast_analysis.md |
| situated contrast high top-prior / high wrong-action cost oracle ask rate | 1.000 | 1.000 | PASS | paper/tables/situated_contrast_analysis.md |
| API api_direct_act net_utility | 0.420 | 0.420 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_direct_act success | 0.770 | 0.770 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ask_needed net_utility | 0.632 | 0.632 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ask_needed success | 0.880 | 0.880 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ask_needed missed_clarification_rate | 0.583 | 0.583 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ask_needed unnecessary_clarification_rate | 0.327 | 0.327 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ecu net_utility | 0.976 | 0.976 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ecu success | 1.000 | 1.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ecu ask_rate | 0.480 | 0.480 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ecu missed_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API api_ecu unnecessary_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API auxiliary api_ask_needed_cot net_utility | 0.632 | 0.632 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API auxiliary api_ask_needed_cot success | 0.890 | 0.890 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API auxiliary api_ask_needed_cot ask_rate | 0.370 | 0.370 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API auxiliary api_ask_needed_cot missed_clarification_rate | 0.604 | 0.604 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API auxiliary api_ask_needed_cot unnecessary_clarification_rate | 0.346 | 0.346 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API second-model api_direct_act net_utility | 0.040 | 0.040 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_direct_act success | 0.640 | 0.640 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ask_needed net_utility | 0.098 | 0.098 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ask_needed success | 0.680 | 0.680 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ask_needed missed_clarification_rate | 0.909 | 0.909 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ecu net_utility | 0.722 | 0.722 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ecu success | 0.880 | 0.880 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ecu ask_rate | 0.560 | 0.560 | PASS | data/runs/api_second_model_25_results.jsonl |
| API second-model api_ecu missed_clarification_rate | 0.182 | 0.182 | PASS | data/runs/api_second_model_25_results.jsonl |
| paired second-model ECU - Ask-Needed utility delta | 0.624 | 0.624 | PASS | paper/tables/api_second_model_25/paired_differences.md |
| paired second-model ECU - DirectAct utility delta | 0.682 | 0.682 | PASS | paper/tables/api_second_model_25/paired_differences.md |
| current-model gpt-5.4-mini api_direct_act net_utility | 0.380 | 0.380 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_direct_act success | 0.750 | 0.750 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ask_needed net_utility | 0.868 | 0.868 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ask_needed success | 0.970 | 0.970 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ask_needed missed_clarification_rate | 0.125 | 0.125 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ask_needed unnecessary_clarification_rate | 0.519 | 0.519 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ask_needed_cot net_utility | 0.864 | 0.864 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ecu net_utility | 0.976 | 0.976 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ecu success | 1.000 | 1.000 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ecu ask_rate | 0.480 | 0.480 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ecu missed_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| current-model gpt-5.4-mini api_ecu unnecessary_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_4_mini_test100_results.jsonl |
| paired current-model gpt-5.4-mini api_ecu - api_ask_needed utility delta | 0.107 | 0.107 | PASS | paper/tables/current_model_sweep.md |
| paired current-model gpt-5.4-mini api_ecu - api_ask_needed_cot utility delta | 0.112 | 0.112 | PASS | paper/tables/current_model_sweep.md |
| current-model gpt-5.5 api_direct_act net_utility | 0.240 | 0.240 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_direct_act success | 0.720 | 0.720 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ask_needed net_utility | 0.821 | 0.821 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ask_needed success | 0.960 | 0.960 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ask_needed missed_clarification_rate | 0.271 | 0.271 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ask_needed unnecessary_clarification_rate | 0.038 | 0.038 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ask_needed_cot net_utility | 0.976 | 0.976 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ecu net_utility | 0.976 | 0.976 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ecu success | 1.000 | 1.000 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ecu ask_rate | 0.480 | 0.480 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ecu missed_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| current-model gpt-5.5 api_ecu unnecessary_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_5_test100_results.jsonl |
| paired current-model gpt-5.5 api_ecu - api_ask_needed utility delta | 0.155 | 0.155 | PASS | paper/tables/current_model_sweep.md |
| paired current-model gpt-5.5 api_ecu - api_ask_needed_cot utility delta | 0.000 | 0.000 | PASS | paper/tables/current_model_sweep.md |
| scene-format shuffled gpt-5.4-mini api_direct_act net_utility | 0.420 | 0.420 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ask_needed net_utility | 0.908 | 0.908 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ask_needed missed_clarification_rate | 0.042 | 0.042 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ask_needed unnecessary_clarification_rate | 0.481 | 0.481 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ask_needed_cot net_utility | 0.926 | 0.926 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ecu net_utility | 0.976 | 0.976 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ecu success | 1.000 | 1.000 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ecu ask_rate | 0.480 | 0.480 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ecu missed_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini api_ecu unnecessary_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl |
| scene-format shuffled gpt-5.4-mini paired ECU - Ask-Needed utility delta | 0.068 | 0.068 | PASS | paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md |
| scene-format shuffled gpt-5.4-mini paired ECU - CoT Ask-Needed utility delta | 0.049 | 0.049 | PASS | paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md |
| scene-format shuffled gpt-5.4-mini ECU ask-act change rate | 0.000 | 0.000 | PASS | paper/tables/api_gpt_5_4_mini_scene_format_robustness.md |
| scene-format natural-language gpt-5.4-mini api_direct_act net_utility | 0.420 | 0.420 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ask_needed net_utility | 0.788 | 0.788 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ask_needed missed_clarification_rate | 0.167 | 0.167 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ask_needed unnecessary_clarification_rate | 0.519 | 0.519 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ask_needed_cot net_utility | 0.904 | 0.904 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ecu net_utility | 0.975 | 0.975 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ecu success | 1.000 | 1.000 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ecu ask_rate | 0.490 | 0.490 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ecu missed_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini api_ecu unnecessary_clarification_rate | 0.019 | 0.019 | PASS | data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl |
| scene-format natural-language gpt-5.4-mini paired ECU - Ask-Needed utility delta | 0.186 | 0.186 | PASS | paper/tables/api_gpt_5_4_mini_natural_language_test100/paired_differences.md |
| scene-format natural-language gpt-5.4-mini paired ECU - CoT Ask-Needed utility delta | 0.070 | 0.070 | PASS | paper/tables/api_gpt_5_4_mini_natural_language_test100/paired_differences.md |
| scene-format natural-language gpt-5.4-mini ECU ask-act change rate | 0.010 | 0.010 | PASS | paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md |
| API question usefulness test api_ask_needed ask_precision | 0.541 | 0.541 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ask_needed ask_recall | 0.417 | 0.417 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ask_needed post_answer_success | 1.000 | 1.000 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ask_needed_cot ask_precision | 0.514 | 0.514 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ask_needed_cot ask_recall | 0.396 | 0.396 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ecu ask_precision | 1.000 | 1.000 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ecu ask_recall | 1.000 | 1.000 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ecu post_answer_success | 1.000 | 1.000 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API question usefulness test api_ecu unneeded_ask_share | 0.000 | 0.000 | PASS | paper/tables/api_eval_100_extended/question_usefulness.md |
| API ECU candidate-margin positive rate | 0.490 | 0.490 | PASS | paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md |
| API ECU candidate-margin/oracle agreement | 0.990 | 0.990 | PASS | paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md |
| API ECU effective context override rate | 0.010 | 0.010 | PASS | paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md |
| API ECU final ask/oracle agreement | 1.000 | 1.000 | PASS | paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md |
| API ECU candidate calibration top benchmark match | 0.970 | 0.970 | PASS | paper/tables/api_candidate_calibration.md |
| API ECU candidate calibration top hidden match | 0.770 | 0.770 | PASS | paper/tables/api_candidate_calibration.md |
| API ECU candidate calibration prior TV | 0.057 | 0.057 | PASS | paper/tables/api_candidate_calibration.md |
| API ECU candidate calibration gpt-4.1-mini margin Pearson | 0.948 | 0.948 | PASS | paper/tables/api_candidate_calibration.md |
| API ECU candidate calibration gpt-4.1-mini margin Spearman | 0.741 | 0.741 | PASS | paper/tables/api_candidate_calibration.md |
| API ECU candidate calibration gpt-5.5 margin Pearson | 0.991 | 0.991 | PASS | paper/tables/api_candidate_calibration.md |
| API ECU candidate calibration gpt-5.5 margin Spearman | 0.954 | 0.954 | PASS | paper/tables/api_candidate_calibration.md |
| API cache-only replay checks | {'main_100_gpt41mini': {'canonical_rows': 300, 'replay_rows': 300, 'mismatches': 0}, 'cot_100_gpt41mini': {'canonical_rows': 100, 'replay_rows': 100, 'mismatches': 0}, 'style_50_gpt41mini': {'canonical_rows': 150, 'replay_rows': 150, 'mismatches': 0}, 'second_model_25_gpt41nano': {'canonical_rows': 75, 'replay_rows': 75, 'mismatches': 0}, 'current_100_gpt54mini': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}, 'current_100_gpt55': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}, 'shuffled_scene_100_gpt54mini': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}, 'natural_language_scene_100_gpt54mini': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}} | {'main_100_gpt41mini': {'canonical_rows': 300, 'replay_rows': 300, 'mismatches': 0}, 'cot_100_gpt41mini': {'canonical_rows': 100, 'replay_rows': 100, 'mismatches': 0}, 'style_50_gpt41mini': {'canonical_rows': 150, 'replay_rows': 150, 'mismatches': 0}, 'second_model_25_gpt41nano': {'canonical_rows': 75, 'replay_rows': 75, 'mismatches': 0}, 'current_100_gpt54mini': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}, 'current_100_gpt55': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}, 'shuffled_scene_100_gpt54mini': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}, 'natural_language_scene_100_gpt54mini': {'canonical_rows': 400, 'replay_rows': 400, 'mismatches': 0}} | PASS | paper/tables/api_cache_replay_verification.md |
| simulated user visible-answer audit | {'generated_oracle_ask_answers': 1233, 'generated_failures': 0, 'api_asked_answers': 184, 'api_failures': 0} | {'generated_oracle_ask_answers': 1233, 'generated_failures': 0, 'api_asked_answers': 184, 'api_failures': 0} | PASS | paper/tables/simulated_user_audit.md |
| API subset stability minimum leave-one-category ECU - Ask-Needed delta | 0.190 | 0.190 | PASS | paper/tables/api_eval_100_corrected/subset_stability.md |
| API subset stability minimum leave-one-episode ECU - Ask-Needed delta | 0.307 | 0.307 | PASS | paper/tables/api_eval_100_corrected/subset_stability.md |
| API subset stability stratified bootstrap lower bound ECU - Ask-Needed | 0.183 | 0.183 | PASS | paper/tables/api_eval_100_corrected/subset_stability.md |
| paired API ECU - Ask-Needed utility delta | 0.343 | 0.343 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| paired API ECU - DirectAct utility delta | 0.556 | 0.556 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| paired API ECU - CoT Ask-Needed utility delta | 0.344 | 0.344 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| paired CoT Ask-Needed - plain Ask-Needed utility delta | -0.001 | -0.001 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| paired offline ECU - prompted utility delta | 0.020 | 0.020 | PASS | data/runs/offline_results.jsonl |
| cached API utility sensitivity minimum ECU - Ask-Needed delta | 0.138 | 0.138 | PASS | paper/tables/api_eval_100_corrected/utility_sensitivity.md |
| cached API utility sensitivity maximum ECU - Ask-Needed delta | 0.475 | 0.475 | PASS | paper/tables/api_eval_100_corrected/utility_sensitivity.md |
| cached API utility sensitivity minimum ECU - Ask-Needed paired CI lower | 0.070 | 0.070 | PASS | paper/tables/api_eval_100_corrected/utility_sensitivity.md |
| API calibration test api_ecu act_preferred ask_rate | 0.000 | 0.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API calibration test api_ecu ask_preferred ask_rate | 1.000 | 1.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API calibration test api_ask_needed act_preferred ask_rate | 0.425 | 0.425 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API calibration test api_ask_needed ask_preferred ask_rate | 0.417 | 0.417 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API calibration test api_ecu ask_preferred net_utility | 0.950 | 0.950 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API category context_resolved api_ecu net_utility | 1.000 | 1.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API category equivalent_outcome api_ecu ask_rate | 0.000 | 0.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API category referential api_ecu ask_rate | 1.000 | 1.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API category risk_sensitive api_ecu ask_rate | 1.000 | 1.000 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API category preference_social api_ecu ask_rate | 0.400 | 0.400 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API category risk_sensitive api_ask_needed net_utility | -0.008 | -0.008 | PASS | data/runs/api_eval_100_corrected_results.jsonl |
| API auxiliary category equivalent_outcome api_ask_needed_cot ask_rate | 0.850 | 0.850 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API auxiliary category risk_sensitive api_ask_needed_cot net_utility | -0.200 | -0.200 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| API auxiliary category preference_social api_ask_needed_cot net_utility | 0.598 | 0.598 | PASS | data/runs/api_eval_100_cot_results.jsonl |
| api failure events direct_act | 48 | 48 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| api failure events ask_needed | 45 | 45 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| api failure events ask_needed_cot | 47 | 47 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| api failure events ecu | 0 | 0 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| api failure taxonomy risk blindness | 57 | 57 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| api failure taxonomy equivalence blindness | 33 | 33 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| api failure taxonomy referential guessing | 25 | 25 | PASS | paper/tables/api_eval_100_extended/failure_taxonomy.md |
| API style-stress api_direct_act net_utility | 0.320 | 0.320 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_direct_act success | 0.760 | 0.760 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ask_needed net_utility | 0.814 | 0.814 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ask_needed success | 0.920 | 0.920 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ask_needed missed_clarification_rate | 0.478 | 0.478 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ask_needed unnecessary_clarification_rate | 0.259 | 0.259 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ecu net_utility | 0.977 | 0.977 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ecu success | 1.000 | 1.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ecu ask_rate | 0.460 | 0.460 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ecu missed_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress api_ecu unnecessary_clarification_rate | 0.000 | 0.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress question usefulness api_ask_needed ask_precision | 0.632 | 0.632 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| API style-stress question usefulness api_ask_needed ask_recall | 0.522 | 0.522 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| API style-stress question usefulness api_ask_needed post_answer_success | 1.000 | 1.000 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| API style-stress question usefulness api_ecu ask_precision | 1.000 | 1.000 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| API style-stress question usefulness api_ecu ask_recall | 1.000 | 1.000 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| API style-stress question usefulness api_ecu post_answer_success | 1.000 | 1.000 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| API style-stress question usefulness api_ecu unneeded_ask_share | 0.000 | 0.000 | PASS | paper/tables/api_style_stress_50/question_usefulness.md |
| paired style-stress ECU - Ask-Needed utility delta | 0.163 | 0.163 | PASS | data/runs/api_style_stress_50_results.jsonl |
| paired style-stress ECU - DirectAct utility delta | 0.657 | 0.657 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress category equivalent_outcome api_ask_needed ask_rate | 0.700 | 0.700 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress category referential api_ecu ask_rate | 1.000 | 1.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress category risk_sensitive api_ecu ask_rate | 1.000 | 1.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress category preference_social api_ecu net_utility | 0.985 | 0.985 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress calibration api_ecu act_preferred ask_rate | 0.000 | 0.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress calibration api_ecu ask_preferred ask_rate | 1.000 | 1.000 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress calibration api_ask_needed act_preferred ask_rate | 0.350 | 0.350 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress calibration api_ask_needed ask_preferred ask_rate | 0.522 | 0.522 | PASS | data/runs/api_style_stress_50_results.jsonl |
| API style-stress calibration api_ecu ask_preferred net_utility | 0.950 | 0.950 | PASS | data/runs/api_style_stress_50_results.jsonl |
| style-stress failure events direct_act | 23 | 23 | PASS | paper/tables/api_style_stress_50/failure_taxonomy.md |
| style-stress failure events ask_needed | 18 | 18 | PASS | paper/tables/api_style_stress_50/failure_taxonomy.md |
| style-stress failure events ecu | 0 | 0 | PASS | paper/tables/api_style_stress_50/failure_taxonomy.md |
| style-stress failure taxonomy referential guessing | 18 | 18 | PASS | paper/tables/api_style_stress_50/failure_taxonomy.md |
| style-stress failure taxonomy risk blindness | 10 | 10 | PASS | paper/tables/api_style_stress_50/failure_taxonomy.md |
| style-stress failure taxonomy equivalence blindness | 7 | 7 | PASS | paper/tables/api_style_stress_50/failure_taxonomy.md |
| ablation current-rule ask decision matches actual API ECU | 100 | 100 | PASS | paper/tables/api_eval_100_corrected/ecu_ablation.md |
| API ECU ablation current_rule_replay net_utility | 0.976 | 0.976 | PASS | paper/tables/api_eval_100_corrected/ecu_ablation.md |
| API ECU ablation accept_model_equivalence net_utility | 0.745 | 0.745 | PASS | paper/tables/api_eval_100_corrected/ecu_ablation.md |
| API ECU ablation accept_model_equivalence missed_clarification_rate | 0.375 | 0.375 | PASS | paper/tables/api_eval_100_corrected/ecu_ablation.md |
| API ECU ablation never_collapse_equivalence unnecessary_clarification_rate | 0.385 | 0.385 | PASS | paper/tables/api_eval_100_corrected/ecu_ablation.md |
| API ECU ablation no_margin_or_context unnecessary_clarification_rate | 0.250 | 0.250 | PASS | paper/tables/api_eval_100_corrected/ecu_ablation.md |
| OOD episodes with held-out object type | 102 | 102 | PASS | paper/tables/robustness_breakdown.md |
| OOD held-out object types | ['charger', 'keys', 'notebook', 'remote', 'water_bottle'] | ['charger', 'keys', 'notebook', 'remote', 'water_bottle'] | PASS | paper/tables/robustness_breakdown.md |
| OOD held-out slice ecu net utility | 0.975 | 0.975 | PASS | paper/tables/robustness_breakdown.md |
| OOD held-out slice ecu success | 1.000 | 1.000 | PASS | paper/tables/robustness_breakdown.md |
| OOD held-out slice learned_controller net utility | 0.975 | 0.975 | PASS | paper/tables/robustness_breakdown.md |
| OOD held-out slice learned_controller success | 1.000 | 1.000 | PASS | paper/tables/robustness_breakdown.md |
| ambiguity-mix shift split counts | {'dev': 180, 'ood_ambiguity_mix': 200, 'test': 300, 'train': 600} | {'dev': 180, 'ood_ambiguity_mix': 200, 'test': 300, 'train': 600} | PASS | data/generated/ambiguity_mix_shift_episodes.jsonl |
| ambiguity-mix train categories | ['context_resolved', 'equivalent_outcome', 'referential'] | ['context_resolved', 'equivalent_outcome', 'referential'] | PASS | data/generated/ambiguity_mix_shift_episodes.jsonl |
| ambiguity-mix held-out categories | ['preference_social', 'risk_sensitive'] | ['preference_social', 'risk_sensitive'] | PASS | data/generated/ambiguity_mix_shift_episodes.jsonl |
| ambiguity-mix test ecu net_utility | 0.963 | 0.963 | PASS | paper/tables/ambiguity_mix_shift.md |
| ambiguity-mix ood_ambiguity_mix ecu net_utility | 0.962 | 0.962 | PASS | paper/tables/ambiguity_mix_shift.md |
| ambiguity-mix ood_ambiguity_mix ecu ask_rate | 0.750 | 0.750 | PASS | paper/tables/ambiguity_mix_shift.md |
| ambiguity-mix ood_ambiguity_mix learned_controller net_utility | 0.950 | 0.950 | PASS | paper/tables/ambiguity_mix_shift.md |
| ambiguity-mix ood_ambiguity_mix learned_controller ask_rate | 1.000 | 1.000 | PASS | paper/tables/ambiguity_mix_shift.md |
| audit scenario total reviewed | 100 | 100 | PASS | paper/audits/AUDIT_SUMMARY.md |
| audit scenario ok | 100 | 100 | PASS | paper/audits/AUDIT_SUMMARY.md |
| audit scenario bad_label | 0 | 0 | PASS | paper/audits/AUDIT_SUMMARY.md |
| audit question total reviewed | 100 | 100 | PASS | paper/audits/AUDIT_SUMMARY.md |
| audit question ok | 73 | 73 | PASS | paper/audits/AUDIT_SUMMARY.md |
| audit question minor_issue | 19 | 19 | PASS | paper/audits/AUDIT_SUMMARY.md |
| audit question bad_question | 8 | 8 | PASS | paper/audits/AUDIT_SUMMARY.md |
| paper consistency audit failures | 0 | 0 | PASS | paper/paper_consistency_audit.md |
| API cache response count | 914 | 914 | PASS | data/runs/api_cache.jsonl |
| API cache input tokens | 271208 | 271208 | PASS | data/runs/api_cache.jsonl |
| API cache output tokens | 49117 | 49117 | PASS | data/runs/api_cache.jsonl |
| API cache total tokens | 320325 | 320325 | PASS | data/runs/api_cache.jsonl |
| API second-model cache response count | 109 | 109 | PASS | data/runs/api_second_model_cache.jsonl |
| API second-model cache input tokens | 32996 | 32996 | PASS | data/runs/api_second_model_cache.jsonl |
| API second-model cache output tokens | 6599 | 6599 | PASS | data/runs/api_second_model_cache.jsonl |
| API second-model cache total tokens | 39595 | 39595 | PASS | data/runs/api_second_model_cache.jsonl |
