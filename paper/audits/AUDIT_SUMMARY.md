# Audit Summary

This is an author-style sanity audit generated from the frozen audit packets.

## Scenario Audit

- Total reviewed: 100
- `ok`: 100
- `minor_issue`: 0
- `bad_label`: 0

Interpretation: the sampled scenario labels are coherent with the visible scene, hidden target, and utility oracle.

## Question Audit

- Total reviewed: 100
- `ok`: 73
- `minor_issue`: 19
- `bad_question`: 8

Interpretation: all oracle-ask ECU questions in the audit are natural and diagnostic. The main question issues are expected baseline failures: prompted Ask-Needed asks natural but unnecessary questions in equivalent-outcome and context-resolved cases. `bad_question` cases are equivalent-outcome baseline questions that ask extra/non-diagnostic table or preference questions.

Files:

- `scenario_audit_completed.md`
- `question_audit_completed.md`
