# Question Usefulness

This table evaluates whether first-turn questions are both necessary under the utility oracle and successfully grounded after the simulated user answer.

Ask precision is the fraction of asked questions that were oracle-needed. Ask recall is the fraction of oracle-needed questions that were asked. Post-answer success is final task success conditional on asking.

## Takeaways

- `style_test`: ECU ask precision/recall/post-answer success are 1.000/1.000/1.000; Ask-Needed is 0.632/0.522/1.000.

## Table

| Split | Method | N | Asked | Oracle ask | Ask precision | Ask recall | Post-answer success | Useful successful asks | Unneeded ask share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| style_test | api_direct_act | 50 | 0 | 23 | - | 0.000 | - | - | - |
| style_test | api_ask_needed | 50 | 19 | 23 | 0.632 | 0.522 | 1.000 | 0.632 | 0.368 |
| style_test | api_ecu | 50 | 23 | 23 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
