# Current-Model Sweep

## Main Comparison

| Model | Paired N | Direct utility | Ask-Needed utility | CoT Ask-Needed utility | ECU utility | ECU - AskNeeded | 95% paired CI | ECU missed | ECU unnecessary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gpt-4.1-mini | 100 | 0.420 | 0.632 | 0.632 | 0.976 | 0.343 | [0.168, 0.559] | 0.000 | 0.000 |
| gpt-5.4-mini | 100 | 0.380 | 0.868 | 0.864 | 0.976 | 0.107 | [0.030, 0.219] | 0.000 | 0.000 |
| gpt-5.5 | 100 | 0.240 | 0.821 | 0.976 | 0.976 | 0.155 | [0.035, 0.316] | 0.000 | 0.000 |


## API Usage

| Model | Responses | Input tokens | Output tokens | Reasoning tokens |
| --- | --- | --- | --- | --- |
| gpt-4.1-mini | 556 | 167871 | 27968 | 0 |
| gpt-5.4-mini | 610 | 179191 | 31439 | 0 |
| gpt-5.5 | 570 | 169170 | 30341 | 0 |
