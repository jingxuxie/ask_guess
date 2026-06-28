# Controller Analysis

This generated report documents the lightweight interaction-supervised ask/act controller trained from automatic oracle labels.

## Tuned Thresholds

| Controller | Decision score | Tuned threshold |
| --- | --- | --- |
| ECU threshold | EU(ask)-EU(act) | -0.025 |
| Learned controller | P(ask) | 0.070 |

## Learned Logistic Weights

Weights are shown in descending absolute value. Positive weights increase the probability of asking.

| Feature | Weight | Positive direction |
| --- | --- | --- |
| EU ask-act margin | 2.951 | ask |
| context resolves | -1.834 | act |
| candidates equivalent | -1.752 | act |
| ask cost x10 | -1.685 | act |
| risk level | 1.581 | ask |
| wrong-action cost / 3 | 1.099 | ask |
| salience gap | -0.993 | act |
| normalized entropy | 0.922 | ask |
| success-class ratio | 0.809 | ask |
| num candidates / 4 | -0.618 | act |
| top prior | -0.396 | act |
| intercept | -0.383 | act |

## Offline Controller Metrics

| Split | Method | N | Net utility | Success | Ask rate | Missed clarif. | Unnecessary clarif. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ood_test | prompted_heuristic | 200 | 0.955 | 1.000 | 0.700 | 0.000 | 0.400 |
| ood_test | ecu | 200 | 0.975 | 1.000 | 0.500 | 0.000 | 0.000 |
| ood_test | ecu_threshold | 200 | 0.975 | 1.000 | 0.500 | 0.000 | 0.000 |
| ood_test | learned_controller | 200 | 0.975 | 1.000 | 0.500 | 0.000 | 0.000 |
| test | prompted_heuristic | 400 | 0.938 | 0.988 | 0.700 | 0.000 | 0.400 |
| test | ecu | 400 | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| test | ecu_threshold | 400 | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |
| test | learned_controller | 400 | 0.958 | 0.988 | 0.500 | 0.000 | 0.000 |

## Learned Controller by Category

| Split | Category | N | Ask rate | Oracle ask | Net utility | Success |
| --- | --- | --- | --- | --- | --- | --- |
| test | context_resolved | 80 | 0.000 | 0.000 | 0.940 | 0.950 |
| test | equivalent_outcome | 80 | 0.000 | 0.000 | 1.000 | 1.000 |
| test | preference_social | 80 | 0.500 | 0.500 | 0.950 | 0.988 |
| test | referential | 80 | 1.000 | 1.000 | 0.950 | 1.000 |
| test | risk_sensitive | 80 | 1.000 | 1.000 | 0.950 | 1.000 |
| ood_test | context_resolved | 40 | 0.000 | 0.000 | 1.000 | 1.000 |
| ood_test | equivalent_outcome | 40 | 0.000 | 0.000 | 1.000 | 1.000 |
| ood_test | preference_social | 40 | 0.500 | 0.500 | 0.975 | 1.000 |
| ood_test | referential | 40 | 1.000 | 1.000 | 0.950 | 1.000 |
| ood_test | risk_sensitive | 40 | 1.000 | 1.000 | 0.950 | 1.000 |

## Learned Ask Probability by Category

| Split | Category | N | Mean P(ask) | Min | Max |
| --- | --- | --- | --- | --- | --- |
| test | context_resolved | 80 | 0.004 | 0.004 | 0.004 |
| test | equivalent_outcome | 80 | 0.033 | 0.033 | 0.033 |
| test | preference_social | 80 | 0.515 | 0.058 | 0.972 |
| test | referential | 80 | 0.976 | 0.969 | 0.980 |
| test | risk_sensitive | 80 | 0.980 | 0.965 | 0.989 |
| ood_test | context_resolved | 40 | 0.004 | 0.004 | 0.004 |
| ood_test | equivalent_outcome | 40 | 0.033 | 0.033 | 0.033 |
| ood_test | preference_social | 40 | 0.515 | 0.058 | 0.972 |
| ood_test | referential | 40 | 0.975 | 0.969 | 0.980 |
| ood_test | risk_sensitive | 40 | 0.979 | 0.964 | 0.990 |
