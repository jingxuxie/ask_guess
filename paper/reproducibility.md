# Reproducibility Report

Generated: 2026-06-28 03:06:06

This report records the canonical data, result, cache, and paper artifacts used by the current draft.

## Dataset Summary

| Group | Name | Count | Oracle ask rate |
| --- | --- | --- | --- |
| total | 1400 | - | 0.500 |
| split | dev | 200 |  |
| split | ood_test | 200 |  |
| split | test | 400 |  |
| split | train | 600 |  |
| category | context_resolved | 280 |  |
| category | equivalent_outcome | 280 |  |
| category | preference_social | 280 |  |
| category | referential | 280 |  |
| category | risk_sensitive | 280 |  |

## Offline Metrics

| Split | Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ood_test | direct_act | 200 | 0.550 | [0.400, 0.690] | 0.825 | 0.000 | 1.000 | 0.000 |
| ood_test | ask_always | 200 | 0.920 | [0.915, 0.925] | 1.000 | 1.000 | 0.000 | 1.000 |
| ood_test | raw_ambiguity | 200 | 0.920 | [0.915, 0.925] | 1.000 | 1.000 | 0.000 | 1.000 |
| ood_test | prompted_heuristic | 200 | 0.955 | [0.951, 0.960] | 1.000 | 0.700 | 0.000 | 0.400 |
| ood_test | ecu | 200 | 0.975 | [0.972, 0.978] | 1.000 | 0.500 | 0.000 | 0.000 |
| ood_test | ecu_threshold | 200 | 0.975 | [0.972, 0.978] | 1.000 | 0.500 | 0.000 | 0.000 |
| ood_test | learned_controller | 200 | 0.975 | [0.972, 0.978] | 1.000 | 0.500 | 0.000 | 0.000 |
| test | direct_act | 400 | 0.498 | [0.391, 0.598] | 0.792 | 0.000 | 1.000 | 0.000 |
| test | ask_always | 400 | 0.920 | [0.916, 0.924] | 1.000 | 1.000 | 0.000 | 1.000 |
| test | raw_ambiguity | 400 | 0.920 | [0.916, 0.924] | 1.000 | 1.000 | 0.000 | 1.000 |
| test | prompted_heuristic | 400 | 0.938 | [0.922, 0.951] | 0.988 | 0.700 | 0.000 | 0.400 |
| test | ecu | 400 | 0.958 | [0.942, 0.970] | 0.988 | 0.500 | 0.000 | 0.000 |
| test | ecu_threshold | 400 | 0.958 | [0.942, 0.970] | 0.988 | 0.500 | 0.000 | 0.000 |
| test | learned_controller | 400 | 0.958 | [0.942, 0.970] | 0.988 | 0.500 | 0.000 | 0.000 |

## API Metrics

| Split | Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | api_direct_act | 100 | 0.420 | [0.180, 0.640] | 0.770 | 0.000 | 1.000 | 0.000 |
| test | api_ask_needed | 100 | 0.632 | [0.431, 0.810] | 0.880 | 0.370 | 0.583 | 0.327 |
| test | api_ecu | 100 | 0.976 | [0.972, 0.981] | 1.000 | 0.480 | 0.000 | 0.000 |

## API Style-Stress Metrics

| Split | Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| style_test | api_direct_act | 50 | 0.320 | [-0.080, 0.680] | 0.760 | 0.000 | 1.000 | 0.000 |
| style_test | api_ask_needed | 50 | 0.814 | [0.654, 0.945] | 0.920 | 0.380 | 0.478 | 0.259 |
| style_test | api_ecu | 50 | 0.977 | [0.970, 0.984] | 1.000 | 0.460 | 0.000 | 0.000 |

## Auxiliary Second-Model API Metrics

This small check uses gpt-4.1-nano on 25 stratified test episodes and is not the headline API result.

| Split | Method | N | Net utility | 95% CI | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | api_direct_act | 25 | 0.040 | [-0.520, 0.600] | 0.640 | 0.000 | 1.000 | 0.000 |
| test | api_ask_needed | 25 | 0.098 | [-0.456, 0.586] | 0.680 | 0.240 | 0.909 | 0.357 |
| test | api_ecu | 25 | 0.722 | [0.412, 0.954] | 0.880 | 0.560 | 0.182 | 0.357 |

## API Cache

| Cache entries | Models | Input tokens | Output tokens | Total tokens |
| --- | --- | --- | --- | --- |
| 914 | gpt-4.1-mini: 914 | 271208 | 49117 | 320325 |

## Auxiliary Second-Model API Cache

| Cache entries | Models | Input tokens | Output tokens | Total tokens |
| --- | --- | --- | --- | --- |
| 109 | gpt-4.1-nano: 109 | 32996 | 6599 | 39595 |

## Artifact Hashes

| Artifact | Bytes | JSONL rows | SHA256 |
| --- | --- | --- | --- |
| data/generated/episodes.jsonl | 2197056 | 1400 | 4ed59f18e0c9950dc79e00516d866b65442e3eb2a530bc0be0090ebb9106d3bd |
| data/generated/style_stress_episodes.jsonl | 85950 | 50 | b8e7c5ee5de7f9f53453d790c473d929b424042a7b37b45efff18dab437e79cd |
| data/generated/ambiguity_mix_shift_episodes.jsonl | 2061286 | 1280 | ed52c77dcfc8dcb8965ec2add8855ee7aed4b8162e51ab9504bc2ac80cc3b4b7 |
| data/runs/offline_results.jsonl | 2518289 | 4200 | 8e7657cfdded57cf22abf9f0f1dd17eac657433dcd14a77b48412602d735dbbf |
| data/runs/ambiguity_mix_shift_results.jsonl | 2143929 | 3500 | 5803b2bcac2a6e9c24b5ee75ef42651ac547f337663529d2f6427d163d3e0c61 |
| data/runs/api_eval_100_corrected_results.jsonl | 672440 | 300 | 63fa53d6c3fe9f3c6098ee076b3706d3ff13c092622c3990e50580384ef7a6ea |
| data/runs/api_eval_100_cot_results.jsonl | 156755 | 100 | 3ed2d43cbba0b45767ff397bac88e82fb6bda4b7383e4958cc12202e393f7d3e |
| data/runs/api_style_stress_50_results.jsonl | 340112 | 150 | 7b9df754155d3298711da9f48e735f0d0abeb731eab6b51d6fa2b0977d6e657a |
| data/runs/api_second_model_25_results.jsonl | 171250 | 75 | bd9841ef740e3fe4092b4fdebea35180b28bbd9bf12e2e84e9fa478c81d06ef8 |
| data/runs/api_cache.jsonl | 808118 | 914 | 97a3eeed8d4abf4ca16e72975c9d501428f5c98a1964f44177b14bc2462f6ca5 |
| data/runs/api_second_model_cache.jsonl | 100851 | 109 | 1ee5f89a612d5be0c5f3a1dc1bfa8fd9f2bdc629c5c75d16ead6c8aca3b748c6 |
| paper/tables/benchmark_categories.md | 886 | - | cc9e128bc3d7be2da603f027be3370c89b621a38d0e806a9c73f04ac01013e3a |
| paper/tables/qualitative_examples.md | 2652 | - | 05b19bf7396948287d17b2024b032ddee41527e3f69d32c24c6bd7cc8f2c8fc5 |
| paper/tables/main_results.md | 1426 | - | 63bba9ac6fa825423c8b261d0f2cfe2426595210b4a81a6f906c877fa7a59f62 |
| paper/tables/category_breakdown.md | 5853 | - | 8a7d6504bd942489e048ab1f258f1836466e99d661a649d846396baff34e7bcc |
| paper/tables/paired_differences.md | 697 | - | ea5fa422feabeed76aaad6a3c0d569bc9c1af3ae1ae8044095dde245284e21c0 |
| paper/tables/robustness_breakdown.md | 4167 | - | a4c6de7dd27fe2a837d596d0152e2402d9585367acaf68a2002296c8d7d273c4 |
| paper/tables/controller_analysis.md | 3229 | - | eeea8372a1ccd072030031f40331f2ce95771c4c263e4962f6e8504b313fc088 |
| paper/tables/ambiguity_utility_diagnostic.md | 3273 | - | 2dc345a62fcb9894606b7ecdcac48b3fdcc98b5c6793e2309b9d930fa2f1b4d0 |
| paper/tables/situated_contrast_analysis.md | 3115 | - | 6b143eec927f0f861acd5e96dd6d0084229858fef99ddab3b0ae1244929dd86c |
| paper/tables/ambiguity_mix_shift.md | 5041 | - | a65bfffdf3dc1875e3bec760769b3d7a98acb9caafc46b20da9f2135eb2eb9df |
| paper/tables/clamber_external_sanity.md | 4198 | - | db1c08fa9cc14d00a25502e7899aba267b89a327ddce2660eacf11a9cf7aebe4 |
| paper/tables/simulated_user_audit.md | 2684 | - | cc0ecb9907a53af4d200e2f77ee0e5fc08870cda82b4ac0293e3a855646e9b4a |
| paper/tables/api_cache_replay_verification.md | 2218 | - | 778d75b37d3b1ef7f79c4963e513a7cd1900f46122e9665166c236c6396cc4ef |
| paper/tables/api_eval_100_corrected_results.md | 342 | - | e50a942a0016d8f3357f04ff9e73fc36795f39115397a876d7a1e034584eaf02 |
| paper/tables/api_eval_100_corrected/category_breakdown.md | 1345 | - | 472378c12b78fc42d7b44f72476ac301c2376f674d129d70aa6eac23e3e06768 |
| paper/tables/api_eval_100_corrected/paired_differences.md | 355 | - | fed2944a74ad625c7eac963940425a47f7c433c715f6d173cacd3ac97b462a2a |
| paper/tables/api_eval_100_corrected/subset_stability.md | 1917 | - | a6e8ef58d5a4f459c817d406b93bed8159421590ba8bd34ea6ccf0b5c2b026a2 |
| paper/tables/api_eval_100_corrected/ecu_ablation.md | 2981 | - | 65f37c7962080685313587bd902a8fbabe9d64ef1b5514733dcdc7c0f97c2ad7 |
| paper/tables/api_eval_100_corrected/utility_sensitivity.md | 5812 | - | 15b97c2f8023e05526c9e8f855f1d865e8984dc6b4644b487369462ceaa7afc2 |
| paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md | 2767 | - | db04fb63a69024166d7e9ff0ebc74e9b6f645c4910077b8ce2aa658924995bee |
| paper/tables/api_eval_100_corrected/calibration_by_margin.md | 1401 | - | ab2bff90763680ce908f6476354cf2213486ae708d5e4d88c6475bdaa667ac1a |
| paper/tables/api_eval_100_cot_results.md | 223 | - | 961fb52973b9972690fd17e8dc486fb8cf2f826f705592273ca526fbf8b7ac36 |
| paper/tables/api_eval_100_cot/main_results.md | 271 | - | 2821b7e2e895e5e62484aa0b2254d0c8896260346b7e3cbfe160845b03e8b34a |
| paper/tables/api_eval_100_cot/category_breakdown.md | 586 | - | 20137381c5996100ab8e7bdac13ed3d994e29b92a50bbabf2262cd672d0e2757 |
| paper/tables/api_eval_100_extended/main_results.md | 531 | - | e720ac455ce199547267f5ff45021ecc795b2a96bd50e86e35562da42f6dc867 |
| paper/tables/api_eval_100_extended/category_breakdown.md | 1772 | - | 1f5f73e7c0450e22a605b9723e66c988964698ddffd557a895a11da0756333c5 |
| paper/tables/api_eval_100_extended/paired_differences.md | 443 | - | 312cd6a32324d9d1e758b37242216a7b07e2f5fe78035632fdb967cafaac4dfe |
| paper/tables/api_eval_100_extended/failure_taxonomy.md | 3439 | - | a705ee3fdd85aa7f681744c96ad1ca828d23406de01de59e1d0626c253a62dd8 |
| paper/tables/api_eval_100_extended/question_usefulness.md | 1035 | - | a732dd4992d96269821495389d2da3c77b7847c7cdbe42ba77ed9335df007048 |
| paper/tables/api_style_stress_50_results.md | 339 | - | 21362a1db17e54b86f8064f5124271075dbf25dbf46cd76ef3de0f793122fb28 |
| paper/tables/api_style_stress_50/main_results.md | 454 | - | 4057ed7284a0349d97d87520e47ed33d40cc246e8a2f9f5c9e1bfd42a1f68428 |
| paper/tables/api_style_stress_50/category_breakdown.md | 1433 | - | ac5b5f94b3d4f6013c37e5f17e74a42a98bc19a0d02b3840137a32ae495b5fe9 |
| paper/tables/api_style_stress_50/paired_differences.md | 370 | - | 5276b05e8a6947d10396c6374d8cadbe0b0b9d6a80fadd42868b7af250f8bd94 |
| paper/tables/api_style_stress_50/calibration_by_margin.md | 1458 | - | 1d12d3409be9971c301cddd7a4048a9670acda0338085cd6cf8ec89ea9a66b38 |
| paper/tables/api_style_stress_50/failure_taxonomy.md | 2819 | - | 6573f90da7866519457c384276b1d2e2643778d7d0147377265cb1af6936f332 |
| paper/tables/api_style_stress_50/question_usefulness.md | 970 | - | 18e0e452423e148c091a1c11e392d1bd80f0fe7ea9f84de9102843b6e3d633a9 |
| paper/tables/api_second_model_25_results.md | 339 | - | d0f61c7673c5e61fe55695b9dc942c3f2ae097ff7f16557e71d1a1036f241ada |
| paper/tables/api_second_model_25/main_results.md | 437 | - | 765cb477bc54ba02505562452ae501f251b12987828755d8eacf35ac14430b84 |
| paper/tables/api_second_model_25/category_breakdown.md | 1332 | - | be36f603e4447f10f99dc1d1e80eeeaa000fd123f69a7c2caf61d2cd510ae189 |
| paper/tables/api_second_model_25/paired_differences.md | 353 | - | 25f6e439463cc7b73f52acfa1b20407cf3584a7dbf72a0023271f0294af53365 |
| paper/tables/api_second_model_25/failure_examples.md | 6883 | - | 0f8e92638ecda358752f2357b343deedf32cd7a86f8905a95a2d4816c584acd0 |
| paper/tables/cost_sensitivity.md | 6030 | - | 6dea4c8b48cd0de3a9f62aef113cb55f85d78c3018bb65d8440b6fbe6211e0e8 |
| paper/figures/api_main_net_utility.svg | 2215 | - | 291bd34ba21dbc0b00748ae9d0a20ab41b3df861ab7c5b46b7d1c2ca8180986c |
| paper/figures/api_category_net_utility.svg | 4545 | - | a38855fa7c739c14e910e02940639a0a68b44b4e39f44d72c15d4daef8006f17 |
| paper/figures/api_calibration_ask_rate.svg | 3385 | - | 4ba1b8e70fdfc09c78d3cc7737189b7a4a02454c8deb817b67892f040d50775a |
| paper/figures/cost_sensitivity_ask_cost.svg | 3460 | - | c6b698a767747a6f8920bc6ba7ddee63bf65ae19d365f921c42620ec7a5df7a1 |
| paper/figures/cost_sensitivity_wrong_cost.svg | 3452 | - | 5e38a1d7b8a3f8a1c632382525e0aa416a2d9a010971db9283b95521762ccbad |
| paper/figures/FIGURE_INDEX.md | 1106 | - | 9d2892b8f9f89b74946083eb05c266de261823b44e06bdaa3f752701edaeda46 |
| paper/audits/AUDIT_SUMMARY.md | 845 | - | 68624508358b9251c3bd40a4462aa05dad57470d34abe15f5cf53f6a70b9e5e6 |
| paper/audits/AUDIT_INDEX.md | 530 | - | 353504122c95023d2b8d97d844099f135f6c4a4a93aad9fab71a53d18446e8ce |
| paper/audits/scenario_audit_completed.md | 43622 | - | 68038747914f4e1369f296a1b8f93283dbe9dedb35e6fc647a5fa3cd274d65f4 |
| paper/audits/question_audit_completed.md | 36771 | - | 7afebf901c9bb3922d4d7aa3ec2afabbe65e5ac9643613ae3a7ad3665c55e224 |
| paper/dataset_card.md | 5408 | - | d38a344715a5dd59a30e16c12d0b175f797fe5373686418bc2d5a522aaa144b4 |
| paper/claim_verification.md | 24473 | - | 606705793058d8ce9b377b735b731d58d352ba5171a0ca2439f9a5d6c81b22dd |
| paper/claim_scope.md | 8659 | - | 24ff107f76ec097b1be89daa2e5bcf491a7f877169561b8e6ffe412afd9fc319 |
| paper/paper_consistency_audit.md | 3156 | - | bb9681e206741131dfb25c7fdd013896b984c335ca07750f9d482d137aa9225b |
| paper/submission_readiness.md | 15973 | - | 6cfbd0d63920b31aae51a44cd1161c47956cf04b09adc66f2dd9ca7f1d2b5784 |
| paper/supplement_manifest.md | 7368 | - | e205a7fbdcfe024d13eedb46b971df33be0d70ede627885f01b44cd0d021eefe |
| paper/supplement_audit.md | 1406 | - | 89e4852d5fed6d030aa09cfa02d34528d93883f4adc8ee4ad8d6f5fd03091a1c |
| src/api_cache_replay_verification.py | 8859 | - | 8523f5619cb95c0fc52316cbd29ffbfc6b86346b8ea1accd98f85e7629aff0ba |
| src/api_subset_stability.py | 7647 | - | d229caae694bec11a29392a22d6eb8a4cefcb73583cc50d2c6a740ee2385cb13 |
| src/audit_supplement_release.py | 6980 | - | 2a411c09fe9ae6334b15636a971f249f00cb7910498c54c1c6383b2143061f31 |
| src/api_ecu_margin_analysis.py | 7627 | - | 99c13b3beab8a709db8d0b8bb43d40405a60b1d1a920673c1cb522822ea74cee |
| src/api_utility_sensitivity.py | 8300 | - | ed80310920c45959715459c1095340c76b4352f65f96a6fde09864c1296e2e10 |
| src/make_audit_packet.py | 7031 | - | d72867fb85bc7944e4df90e9417e561f00ba34268da0804ca3a57e9213a8a116 |
| src/complete_audit_packet.py | 5310 | - | 30e1c0d756c03c4f7c7706b4772f25790c2989e8865ea4c3408c5a805d08e12c |
| src/clarify_to_act/environment.py | 4874 | - | 64247f293590b6111d021e195021213d5e9fefe4ca05f217d2cac2ea653c6f64 |
| src/make_dataset_card.py | 10215 | - | c393e3d7531e35d52c2e602940bfa951a3348b9ff7333e90c9d967bb5b574fc4 |
| src/ambiguity_utility_diagnostic.py | 13142 | - | b5d7111ba2b57a389677108c0cbb67aed57b9b82f5a2e451a12e38bb02881559 |
| src/situated_contrast_analysis.py | 7299 | - | 42061fda226affeb3008d2211973f24dfd17b80a96dcf0635dd4277577cedd7d |
| src/make_ambiguity_mix_shift.py | 2775 | - | 55839c4612a1f0c324437ebc76d15f29d186821417550dd90540887cfeb92249 |
| src/ambiguity_mix_shift_analysis.py | 6120 | - | fc1422ef6dfe99391ab614d40c49a8a6f152987a0707f335de4530e989c6c6d9 |
| src/clamber_external_sanity.py | 7705 | - | e057545e959c9f77865e5c29e10ed7dfa36c612142c66438bc980a2ce604cf6e |
| src/simulated_user_audit.py | 9661 | - | 8eaf409f9465a3c4a7610b510b400178d482db39630184653e42b993624ae096 |
| src/paper_consistency_audit.py | 11058 | - | 5a2a4527e8d96bf2a28b4aa3c84023bb98d8aca8db5f860b23ceee8b94341ded |
| src/make_claim_scope_report.py | 15262 | - | e5f8901a4e4c5d071ab5a4d572f2d1d80e06889af3b6ed2ce5d8d5177320c779 |
| src/run_api_experiment.py | 12854 | - | 4f236a82a1f95626b14a5c4de2141daf747a1628cc79475b4949338c5134d155 |
| src/verify_claims.py | 46981 | - | a4bb9aaf344b00e11ebc7e029b619cad4d683ba25a470e3c605fdab1a205dec7 |
| tests/test_core_invariants.py | 11994 | - | e89d9c36c517cd01cc9c0b7450a2689f37f7348250c3b206eb99ae1090afffca |
| paper/latex/main.tex | 26671 | - | f7e021b520e6cba7692f089df532ae5fd8b37478beada7015450b34b7f22421a |
| paper/latex/refs.bib | 2525 | - | 0bb64407b24b770285a012580402c4f8987c98e3544e1efb2645789a75749f30 |
| paper/latex/colm2026_conference.sty | 7727 | - | 55962ae80c25a50335825c85d23eb5f1cd9015aa8e77f7af32b483b646c7483e |
| paper/latex/colm2026_conference.bst | 26973 | - | 2d67552db7ed38ccfccb5957b52f95656e25c249724761d3cf5f7922ad1844c5 |
| paper/latex/fancyhdr.sty | 20521 | - | b56ec4434b9f4607529a4b23dc68ad8d4b94f1f631c8cddaf7da78140d53a5ea |
| paper/latex/natbib.sty | 45154 | - | 88bc70c0e48461934cab5b2accef06b74a8b3ac45ad03ccd3f2a6b7e0d6d530d |
| paper/latex/math_commands.tex | 12284 | - | 90473c4d0542070db244cea73ef962d6cddc5b2a746757e6a40ddf5fdfb90ba9 |
| paper/latex/main.pdf | 153537 | - | 81774b34b0a99e9da38a63185917306f23e1e777c6ab39ad1cc9374a3127af16 |

## Reproduction Commands

Free deterministic regeneration:

```bash
conda run -n ask_dont_guess python src/generate_scenarios.py --train 600 --dev 200 --test 400 --ood-test 200 --seed 13 --out data/generated/episodes.jsonl
conda run -n ask_dont_guess python src/benchmark_categories.py --episodes data/generated/episodes.jsonl --out paper/tables/benchmark_categories.md
conda run -n ask_dont_guess python src/qualitative_examples.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/qualitative_examples.md
conda run -n ask_dont_guess python src/make_dataset_card.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/offline_results.jsonl
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/offline_results.jsonl --out-dir paper/tables
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out-dir paper/tables/api_eval_100_extended
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/offline_results.jsonl --out paper/tables/paired_differences.md --splits test,ood_test --comparisons ecu:prompted_heuristic,learned_controller:prompted_heuristic,ecu:ask_always,ecu:direct_act
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_direct_act,api_ask_needed:api_direct_act
conda run -n ask_dont_guess python src/api_subset_stability.py --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/subset_stability.md
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out paper/tables/api_eval_100_extended/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed_cot,api_ecu:api_ask_needed,api_ask_needed_cot:api_ask_needed,api_ask_needed_cot:api_direct_act
conda run -n ask_dont_guess python src/make_style_stress_episodes.py --episodes data/generated/episodes.jsonl --source-split test --out-split style_test --limit-per-category 10 --out data/generated/style_stress_episodes.jsonl
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/api_style_stress_50_results.jsonl --out-dir paper/tables/api_style_stress_50
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/paired_differences.md --splits style_test --comparisons api_ecu:api_ask_needed,api_ecu:api_direct_act,api_ask_needed:api_direct_act
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/api_second_model_25_results.jsonl --out-dir paper/tables/api_second_model_25
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_second_model_25_results.jsonl --out paper/tables/api_second_model_25/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_direct_act,api_ask_needed:api_direct_act
conda run -n ask_dont_guess python src/calibration_analysis.py --episodes data/generated/episodes.jsonl --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/calibration_by_margin.md
conda run -n ask_dont_guess python src/calibration_analysis.py --episodes data/generated/style_stress_episodes.jsonl --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/calibration_by_margin.md
conda run -n ask_dont_guess python src/failure_taxonomy.py --episodes data/generated/episodes.jsonl --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out paper/tables/api_eval_100_extended/failure_taxonomy.md
conda run -n ask_dont_guess python src/failure_taxonomy.py --episodes data/generated/style_stress_episodes.jsonl --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/failure_taxonomy.md
conda run -n ask_dont_guess python src/question_usefulness_analysis.py --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out paper/tables/api_eval_100_extended/question_usefulness.md
conda run -n ask_dont_guess python src/question_usefulness_analysis.py --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/question_usefulness.md
conda run -n ask_dont_guess python src/api_cache_replay_verification.py --out paper/tables/api_cache_replay_verification.md
conda run -n ask_dont_guess python src/api_ecu_ablation.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/ecu_ablation.md
conda run -n ask_dont_guess python src/api_utility_sensitivity.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/utility_sensitivity.md
conda run -n ask_dont_guess python src/api_ecu_margin_analysis.py --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md
conda run -n ask_dont_guess python src/make_audit_packet.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl,data/runs/api_style_stress_50_results.jsonl --scenarios-per-category 20 --questions 100 --out-dir paper/audits
conda run -n ask_dont_guess python src/complete_audit_packet.py --audit-dir paper/audits
conda run -n ask_dont_guess python src/robustness_analysis.py --episodes data/generated/episodes.jsonl --results data/runs/offline_results.jsonl --out paper/tables/robustness_breakdown.md
conda run -n ask_dont_guess python src/controller_analysis.py --episodes data/generated/episodes.jsonl --offline-results data/runs/offline_results.jsonl --out paper/tables/controller_analysis.md
conda run -n ask_dont_guess python src/ambiguity_utility_diagnostic.py --episodes data/generated/episodes.jsonl --offline-results data/runs/offline_results.jsonl --out paper/tables/ambiguity_utility_diagnostic.md
conda run -n ask_dont_guess python src/situated_contrast_analysis.py --episodes data/generated/episodes.jsonl --out paper/tables/situated_contrast_analysis.md
conda run -n ask_dont_guess python src/make_ambiguity_mix_shift.py --out data/generated/ambiguity_mix_shift_episodes.jsonl
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --out data/runs/ambiguity_mix_shift_results.jsonl --eval-splits test,ood_ambiguity_mix
conda run -n ask_dont_guess python src/ambiguity_mix_shift_analysis.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --results data/runs/ambiguity_mix_shift_results.jsonl --out paper/tables/ambiguity_mix_shift.md
mkdir -p data/external
curl -L https://raw.githubusercontent.com/zt991211/CLAMBER/main/clamber_benchmark.jsonl -o data/external/clamber_benchmark.jsonl
conda run -n ask_dont_guess python src/clamber_external_sanity.py --input data/external/clamber_benchmark.jsonl --out paper/tables/clamber_external_sanity.md
conda run -n ask_dont_guess python src/simulated_user_audit.py --out paper/tables/simulated_user_audit.md
conda run -n ask_dont_guess python src/paper_consistency_audit.py --out paper/paper_consistency_audit.md
conda run -n ask_dont_guess python src/cost_sensitivity.py --episodes data/generated/episodes.jsonl --out paper/tables/cost_sensitivity.md
conda run -n ask_dont_guess python src/make_figures.py --api-results data/runs/api_eval_100_corrected_results.jsonl --cost-table paper/tables/cost_sensitivity.md --out-dir paper/figures
conda run -n ask_dont_guess python -m unittest discover -s tests
conda run -n ask_dont_guess python src/verify_claims.py --episodes data/generated/episodes.jsonl --offline-results data/runs/offline_results.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --api-cot-results data/runs/api_eval_100_cot_results.jsonl --style-episodes data/generated/style_stress_episodes.jsonl --api-style-results data/runs/api_style_stress_50_results.jsonl --api-cache data/runs/api_cache.jsonl --out paper/claim_verification.md
conda run -n ask_dont_guess python src/make_claim_scope_report.py
conda run -n ask_dont_guess python src/make_submission_readiness_report.py --episodes data/generated/episodes.jsonl --style-episodes data/generated/style_stress_episodes.jsonl --offline-results data/runs/offline_results.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --api-cot-results data/runs/api_eval_100_cot_results.jsonl --api-style-results data/runs/api_style_stress_50_results.jsonl --api-cache data/runs/api_cache.jsonl --claim-verification paper/claim_verification.md --pdf paper/latex/main.pdf --out paper/submission_readiness.md
conda run -n ask_dont_guess python src/make_supplement_package.py --manifest-only
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
conda run -n ask_dont_guess python src/audit_supplement_release.py
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
```

Bounded paid API command for the auxiliary private-reasoning baseline. It is cached in `data/runs/api_cache.jsonl` and should not be rerun unless this baseline needs to be regenerated:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/api_eval_100_cot_results.jsonl --summary-out paper/tables/api_eval_100_cot_results.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_ask_needed_cot
```

Bounded paid API command for the 50-episode paraphrase and answer-style stress set. It is cached in `data/runs/api_cache.jsonl` and should not be rerun unless this stress set needs to be regenerated:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out data/runs/api_style_stress_50_results.jsonl --summary-out paper/tables/api_style_stress_50_results.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu
```

Safe cached API replay, with no network calls and no API spending. This fails on any cache miss:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_corrected_replay.jsonl --summary-out /tmp/api_eval_100_corrected_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

Safe cached replay for the auxiliary private-reasoning baseline:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_cot_replay.jsonl --summary-out /tmp/api_eval_100_cot_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_ask_needed_cot --cache-only
```

Safe cached replay for the style-stress set:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out /tmp/api_style_stress_50_replay.jsonl --summary-out /tmp/api_style_stress_50_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

Safe cached replay for the auxiliary 25-episode gpt-4.1-nano second-model sanity check:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_second_model_25_replay.jsonl --summary-out /tmp/api_second_model_25_replay.md --cache data/runs/api_second_model_cache.jsonl --model gpt-4.1-nano --split test --limit-per-category 5 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

Paper build:

```bash
cd paper/latex && make
```

Supplement archive:

```bash
conda run -n ask_dont_guess python src/make_supplement_package.py
```
