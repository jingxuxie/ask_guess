# Paper Consistency Audit

This generated audit checks that paper-facing text contains the verified headline numbers and required scope caveats.
It is a stale-text guardrail; claim correctness is still recomputed in `paper/claim_verification.md`.

Overall status: **PASS**

| Check | File | Status | Why it matters | Missing patterns |
| --- | --- | --- | --- | --- |
| main API headline metrics | paper/latex/main.tex | PASS | Headline paper text should expose the main API comparison and calibration failure. | none |
| main API paired comparisons | paper/latex/main.tex | PASS | The manuscript should report paired intervals for shared-episode API comparisons. | none |
| subset stability | paper/latex/main.tex | PASS | Subset-stability numbers guard against overclaiming from one category or outlier episode. | none |
| ambiguity is not enough diagnostic | paper/latex/main.tex | PASS | The paper should quantify why raw ambiguity detection is not the same as utility-calibrated clarification. | none |
| situated contrast diagnostic | paper/latex/main.tex | PASS | The paper should include concrete situated slices where similar ambiguity surfaces require different decisions. | none |
| API ECU margin diagnostic | paper/latex/main.tex | PASS | The paper should mention that the API-side margin diagnostic is internal and cached-row based. | none |
| external CLAMBER sanity | paper/latex/main.tex | PASS | External evidence must remain framed as motivation, not method evaluation. | none |
| style stress result | paper/latex/main.tex | PASS | The stress result should include both effect size and its limited scope. | none |
| second model sanity check | paper/latex/main.tex | PASS | The auxiliary model result should be present but not oversold. | none |
| fixed-output utility sensitivity | paper/latex/main.tex | PASS | Reward-sensitivity claims should make clear that outputs are fixed cached API rows. | none |
| failure taxonomy | paper/latex/main.tex | PASS | Qualitative failure claims should match the generated taxonomy counts. | none |
| cache-only reproducibility caveat | paper/latex/main.tex | PASS | The paper should state how API evidence is replayed without spending more API budget. | none |
| COLM template shell | paper/latex/main.tex | PASS | The LaTeX source should use the official COLM submission shell conventions. | none |
| main limitations | paper/latex/main.tex | PASS | Top-tier submission framing needs explicit scope boundaries in the main paper. | none |
| simulated user audit counts in manuscript | paper/latex/main.tex | PASS | The paper should give exact evidence for the deterministic simulated-user audit. | none |
| simulated user audit counts in full draft | paper/clarify_to_act_paper_draft.md | PASS | The longer draft should carry exact audit counts and the human-study caveat. | none |
| submission readiness status | paper/submission_readiness.md | PASS | The readiness report should present a conservative publishability status with traceable evidence. | none |
| claim scope guardrails | paper/claim_scope.md | PASS | The claim-scope report should block likely reviewer-facing overclaims. | none |
