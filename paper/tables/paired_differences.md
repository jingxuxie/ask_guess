# Paired Net-Utility Differences

| Split | Method A | Method B | Shared N | A - B utility | 95% paired CI |
| --- | --- | --- | --- | --- | --- |
| test | ecu | prompted_heuristic | 400 | 0.020 | [0.016, 0.024] |
| test | learned_controller | prompted_heuristic | 400 | 0.020 | [0.016, 0.024] |
| test | ecu | ask_always | 400 | 0.038 | [0.021, 0.052] |
| test | ecu | direct_act | 400 | 0.460 | [0.361, 0.564] |
| ood_test | ecu | prompted_heuristic | 200 | 0.020 | [0.015, 0.026] |
| ood_test | learned_controller | prompted_heuristic | 200 | 0.020 | [0.015, 0.026] |
| ood_test | ecu | ask_always | 200 | 0.055 | [0.047, 0.064] |
| ood_test | ecu | direct_act | 200 | 0.425 | [0.287, 0.573] |
