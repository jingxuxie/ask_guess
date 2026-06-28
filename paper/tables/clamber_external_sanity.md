# CLAMBER External Sanity Check

This is a small external-validity diagnostic, not a main Clarify-to-Act result. It maps CLAMBER's `require_clarification` field to an ASK label and the provided `predict_ambiguous` field to a query-only ambiguity-detector ASK prediction.

The illustrative utility column uses a Clarify-to-Act-style projection with reward `1 - ask_cost` for asking, reward `1` for correctly not asking, and `-miss_cost` for missing a required clarification. It is not CLAMBER's task metric.

## Source

| Item | Value |
| --- | --- |
| Source URL | https://raw.githubusercontent.com/zt991211/CLAMBER/main/clamber_benchmark.jsonl |
| Local input | data/external/clamber_benchmark.jsonl |
| Rows | 3202 |
| SHA256 | 58b195515fca3692c6756fc5242983461659c2f9a7f366b509f16b4cbe917fe0 |
| Ask cost | 0.05 |
| Miss cost | 1.00 |

## Overall

| Group | N | Oracle ask | Pred. ask | Accuracy | Precision | Recall | Missed | Unnec. | Illust. utility | TP/FN/FP/TN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 3202 | 0.500 | 0.246 | 0.538 | 0.577 | 0.284 | 0.716 | 0.208 | 0.271 | 454/1147/333/1268 |

## By Category

| Category | N | Oracle ask | Pred. ask | Accuracy | Precision | Recall | Missed | Unnec. | Illust. utility | TP/FN/FP/TN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FD | 800 | 0.500 | 0.104 | 0.539 | 0.687 | 0.142 | 0.858 | 0.065 | 0.137 | 57/343/26/374 |
| LA | 800 | 0.500 | 0.616 | 0.631 | 0.606 | 0.748 | 0.253 | 0.485 | 0.717 | 299/101/194/206 |
| MC | 1602 | 0.500 | 0.132 | 0.491 | 0.464 | 0.122 | 0.878 | 0.141 | 0.116 | 98/703/113/688 |

## By Subclass

| Subclass | N | Oracle ask | Pred. ask | Accuracy | Precision | Recall | Missed | Unnec. | Illust. utility | TP/FN/FP/TN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ICL | 400 | 0.500 | 0.013 | 0.492 | 0.200 | 0.005 | 0.995 | 0.020 | 0.004 | 1/199/4/196 |
| NK | 400 | 0.500 | 0.195 | 0.585 | 0.718 | 0.280 | 0.720 | 0.110 | 0.270 | 56/144/22/178 |
| co-reference | 400 | 0.500 | 0.950 | 0.535 | 0.518 | 0.985 | 0.015 | 0.915 | 0.937 | 197/3/183/17 |
| none | 801 | 0.000 | 0.141 | 0.859 | 0.000 | 0.000 | 0.000 | 0.141 | 0.993 | 0/0/113/688 |
| polysemy | 400 | 0.500 | 0.282 | 0.728 | 0.903 | 0.510 | 0.490 | 0.055 | 0.496 | 102/98/11/189 |
| what | 201 | 1.000 | 0.149 | 0.149 | 1.000 | 0.149 | 0.851 | 0.000 | -0.709 | 30/171/0/0 |
| when | 200 | 1.000 | 0.110 | 0.110 | 1.000 | 0.110 | 0.890 | 0.000 | -0.785 | 22/178/0/0 |
| where | 200 | 1.000 | 0.110 | 0.110 | 1.000 | 0.110 | 0.890 | 0.000 | -0.785 | 22/178/0/0 |
| whom | 200 | 1.000 | 0.120 | 0.120 | 1.000 | 0.120 | 0.880 | 0.000 | -0.766 | 24/176/0/0 |

## Missed-Clarification Examples

| Category | Subclass | User query excerpt | Reference clarification excerpt |
| --- | --- | --- | --- |
| MC | whom | Give me a list of good coffee shops? | What do you personally consider important in a coffee shop? Are you looking for qualities like the variety of coffee, am |
| MC | whom | Give me some Mother's Day gift ideas. | What are your mother's interests, hobbies, or something she has been wanting? Is there a particular type of gift, such a |
| MC | what | Help me come up with 3 ideas for a new business and how I can start it | What are your areas of interest or expertise, and do you have any preferences for the type of business or industry? |
| MC | whom | Give me some tips on how to train for a marathon. | Can you provide your current fitness level and running experience to tailor the training tips accordingly? |
| MC | whom | How do you improve your basketball handles? | Could you specify what level of proficiency you're at or what specific aspect of your handling you wish to improve? |

## Interpretation

- CLAMBER is query-level and not grounded in deterministic action reward, so this should only be used as external motivation.
- The provided ambiguity prediction substantially under-asks relative to CLAMBER's clarification labels, especially in multi-constraint (`MC`) cases.
- This supports the paper's framing that query-level ambiguity detection is complementary to, but weaker than, situated utility-calibrated ask/act evaluation.
