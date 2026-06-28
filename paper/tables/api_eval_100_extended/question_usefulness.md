# Question Usefulness

This table evaluates whether first-turn questions are both necessary under the utility oracle and successfully grounded after the simulated user answer.

Ask precision is the fraction of asked questions that were oracle-needed. Ask recall is the fraction of oracle-needed questions that were asked. Post-answer success is final task success conditional on asking.

## Takeaways

- `test`: ECU ask precision/recall/post-answer success are 1.000/1.000/1.000; Ask-Needed is 0.541/0.417/1.000.

## Table

| Split | Method | N | Asked | Oracle ask | Ask precision | Ask recall | Post-answer success | Useful successful asks | Unneeded ask share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| test | api_direct_act | 100 | 0 | 48 | - | 0.000 | - | - | - |
| test | api_ask_needed | 100 | 37 | 48 | 0.541 | 0.417 | 1.000 | 0.541 | 0.459 |
| test | api_ask_needed_cot | 100 | 37 | 48 | 0.514 | 0.396 | 1.000 | 0.514 | 0.486 |
| test | api_ecu | 100 | 48 | 48 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
