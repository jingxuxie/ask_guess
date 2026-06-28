from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from clarify_to_act.io import write_text
from clarify_to_act.metrics import markdown_table


DEFAULT_OUT = "paper/paper_consistency_audit.md"


@dataclass(frozen=True)
class TextCheck:
    name: str
    path: str
    patterns: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class CheckResult:
    name: str
    path: str
    status: str
    rationale: str
    missing: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return self.status == "PASS"


CHECKS: tuple[TextCheck, ...] = (
    TextCheck(
        "main API headline metrics",
        "paper/latex/main.tex",
        (
            r"100-episode stratified API evaluation with GPT-4\.1-mini",
            r"0\.632 net utility",
            r"58\.3\\%",
            r"0\.976 net utility",
            r"100\\% task success",
        ),
        "Headline paper text should expose the main API comparison and calibration failure.",
    ),
    TextCheck(
        "main API paired comparisons",
        "paper/latex/main.tex",
        (
            r"0\.343 net utility with 95\\% paired CI \[0\.168, 0\.559\]",
            r"private-reasoning variant by 0\.344 \[0\.171, 0\.564\]",
        ),
        "The manuscript should report paired intervals for shared-episode API comparisons.",
    ),
    TextCheck(
        "subset stability",
        "paper/latex/main.tex",
        (
            r"minimum \+0\.190",
            r"minimum \+0\.307",
            r"95\\% CI \[0\.183, 0\.541\]",
        ),
        "Subset-stability numbers guard against overclaiming from one category or outlier episode.",
    ),
    TextCheck(
        "ambiguity is not enough diagnostic",
        "paper/latex/main.tex",
        (
            r"All 400 canonical test episodes have multiple candidate interpretations",
            r"200 are oracle-act cases and 200 are oracle-ask cases",
            r"surface-ambiguity policy.*0\.920 utility",
            r"unnecessary clarification rate 1\.000",
            r"uncertainty-only controller.*0\.900 utility",
            r"misses 7\.0\\% of oracle-ask cases",
            r"asks unnecessarily in 40\.0\\%",
            r"0\.958 utility",
        ),
        "The paper should quantify why raw ambiguity detection is not the same as utility-calibrated clarification.",
    ),
    TextCheck(
        "situated contrast diagnostic",
        "paper/latex/main.tex",
        (
            r"two-candidate \\texttt\{bring\} episodes",
            r"80 context-resolved cases are oracle-act",
            r"80 referential cases are oracle-ask",
            r"visible ownership gives oracle-act on 40/40 cases",
            r"hidden ownership gives oracle-ask on 40/40",
            r"High-entropy equivalent-outcome cases are oracle-act",
            r"high-top-prior risk-sensitive cases are oracle-ask",
        ),
        "The paper should include concrete situated slices where similar ambiguity surfaces require different decisions.",
    ),
    TextCheck(
        "API ECU margin diagnostic",
        "paper/latex/main.tex",
        (
            r"agrees with the oracle ask label on 99/100 main API rows",
            r"final ask/oracle agreement is 100/100",
        ),
        "The paper should mention that the API-side margin diagnostic is internal and cached-row based.",
    ),
    TextCheck(
        "API ECU candidate-probability diagnostic",
        "paper/latex/main.tex",
        (
            r"top success class matches the benchmark top-prior success class on 97/100 episodes",
            r"mean total-variation distance 0\.057",
            r"top class matches the sampled hidden success class on 77/100 episodes",
            r"Pearson 0\.948, Spearman 0\.741",
            r"Pearson 0\.991, Spearman 0\.954",
            r"not perfect hidden-intent calibration",
        ),
        "The paper should report candidate-probability calibration as a bounded mechanism diagnostic.",
    ),
    TextCheck(
        "external CLAMBER sanity",
        "paper/latex/main.tex",
        (
            r"0\.284 recall",
            r"0\.716 missed-clarification rate",
            r"not a situated task-utility result",
        ),
        "External evidence must remain framed as motivation, not method evaluation.",
    ),
    TextCheck(
        "style stress result",
        "paper/latex/main.tex",
        (
            r"50-episode API stress set",
            r"0\.977 net utility",
            r"0\.814 utility",
            r"0\.320 utility",
            r"\+0\.163 with 95\\% CI \[0\.040, 0\.321\]",
            r"does not prove broad linguistic robustness",
        ),
        "The stress result should include both effect size and its limited scope.",
    ),
    TextCheck(
        "scene-format robustness",
        "paper/latex/main.tex",
        (
            r"original JSON scene serialization",
            r"Reversing the object order",
            r"GPT-5\.4-mini episodes",
            r"0\.976 net utility",
            r"ask/act decision changes on 0/100",
            r"Prompted Ask-Needed changes ask/act decisions on 10\\%",
            r"compact natural-language scene description",
            r"0\.975 utility",
            r"one unnecessary clarification",
            r"ask/act decision changes on 1/100",
            r"two bounded serialization perturbations",
        ),
        "The manuscript should report serialization robustness without overstating broad prompt robustness.",
    ),
    TextCheck(
        "second model sanity check",
        "paper/latex/main.tex",
        (
            r"25-episode GPT-4\.1-nano check",
            r"0\.722 utility versus 0\.098",
            r"0\.040 for DirectAct",
            r"\+0\.624 \[0\.074, 1\.254\]",
            r"too small to substitute for a broad model sweep",
        ),
        "The auxiliary model result should be present but not oversold.",
    ),
    TextCheck(
        "fixed-output utility sensitivity",
        "paper/latex/main.tex",
        (
            r"\+0\.201 to \+0\.239",
            r"\+0\.138 to \+0\.475",
            r"minimum \+0\.070",
            r"does not test adaptive retuning",
        ),
        "Reward-sensitivity claims should make clear that outputs are fixed cached API rows.",
    ),
    TextCheck(
        "failure taxonomy",
        "paper/latex/main.tex",
        (
            r"DirectAct has 48 failure events",
            r"Ask-Needed has 45",
            r"private reasoning has 47",
            r"API ECU has 0",
            r"risk blindness \(57 events\)",
            r"equivalence blindness \(33\)",
            r"referential guessing \(25\)",
        ),
        "Qualitative failure claims should match the generated taxonomy counts.",
    ),
    TextCheck(
        "cache-only reproducibility caveat",
        "paper/latex/main.tex",
        (
            r"cache-only mode",
            r"fails on any cache miss",
            r"network call",
        ),
        "The paper should state how API evidence is replayed without spending more API budget.",
    ),
    TextCheck(
        "COLM template shell",
        "paper/latex/main.tex",
        (
            r"\\usepackage\[submission\]\{colm2026_conference\}",
            r"\\ifcolmsubmission",
            r"\\linenumbers",
            r"\\bibliographystyle\{colm2026_conference\}",
        ),
        "The LaTeX source should use the official COLM submission shell conventions.",
    ),
    TextCheck(
        "current-model sweep",
        "paper/latex/main.tex",
        (
            r"GPT-5\.4-mini",
            r"GPT-5\.5",
            r"plain Ask-Needed remains below",
            r"GPT-5\.5 with private reasoning matches \\ecu",
            r"reasoning effort set to \\texttt\{none\}",
        ),
        "The manuscript should report the current-model sweep without overstating it as a universal frontier result.",
    ),
    TextCheck(
        "current-model category failure modes",
        "paper/latex/main.tex",
        (
            r"largest GPT-5\.4-mini gap is preference/social",
            r"\+0\.193 \\ecu--Ask utility",
            r"37\.5\\% missed oracle asks",
            r"largest GPT-5\.5 gap is risk-sensitive",
            r"\+0\.767",
            r"65\.0\\% missed",
            r"zero missed or unnecessary clarifications in every model/category cell",
        ),
        "The manuscript should localize residual current-model prompting gaps by category without overclaiming.",
    ),
    TextCheck(
        "main limitations",
        "paper/latex/main.tex",
        (
            r"synthetic text/JSON environment",
            r"not a physical simulator",
            r"not a human-response study",
            r"hosted models on 100-episode stratified subsets",
            r"not a replacement for full-scale deployment evaluations",
            r"not open-weight local models",
            r"long-horizon embodied controllers",
        ),
        "Top-tier submission framing needs explicit scope boundaries in the main paper.",
    ),
    TextCheck(
        "simulated user audit counts in manuscript",
        "paper/latex/main.tex",
        (
            r"1233/1233 generated oracle-ask cases",
            r"184/184 actual API asked rows",
        ),
        "The paper should give exact evidence for the deterministic simulated-user audit.",
    ),
    TextCheck(
        "simulated user audit counts in full draft",
        "paper/clarify_to_act_paper_draft.md",
        (
            r"1233/1233",
            r"184/184",
            r"not a human-response study",
        ),
        "The longer draft should carry exact audit counts and the human-study caveat.",
    ),
    TextCheck(
        "submission readiness status",
        "paper/submission_readiness.md",
        (
            r"Overall status \| ready with stated limitations",
            r"Claim verification \| PASS",
            r"All 400 canonical test episodes have multiple candidate interpretations, but 200 are oracle-act and 200 are oracle-ask",
            r"same-action and same-instruction families flipping ask/act decisions",
            r"Generated oracle-ask diagnostic answers resolve the hidden success class in 1233/1233 cases",
            r"Cache-only replay reproduces all 2225 canonical API rows",
        ),
        "The readiness report should present a conservative publishability status with traceable evidence.",
    ),
    TextCheck(
        "claim scope guardrails",
        "paper/claim_scope.md",
        (
            r"Do not claim physical robot deployment",
            r"Full 400-episode current-model sweeps, open-weight models, multimodal agents, and non-OpenAI model families remain future work",
            r"Do not present the 100-episode OpenAI-only sweep as full cross-family or full-test coverage",
            r"Human interaction study is not included",
            r"Do not present cache replay as a fresh model evaluation",
        ),
        "The claim-scope report should block likely reviewer-facing overclaims.",
    ),
)


def run_checks(checks: tuple[TextCheck, ...] = CHECKS) -> list[CheckResult]:
    results: list[CheckResult] = []
    cache: dict[str, str | None] = {}
    for check in checks:
        if check.path not in cache:
            path = Path(check.path)
            cache[check.path] = path.read_text(encoding="utf-8") if path.exists() else None
        text = cache[check.path]
        if text is None:
            results.append(
                CheckResult(
                    name=check.name,
                    path=check.path,
                    status="FAIL",
                    rationale=check.rationale,
                    missing=("file missing",),
                )
            )
            continue
        missing = tuple(pattern for pattern in check.patterns if re.search(pattern, text, re.S) is None)
        results.append(
            CheckResult(
                name=check.name,
                path=check.path,
                status="PASS" if not missing else "FAIL",
                rationale=check.rationale,
                missing=missing,
            )
        )
    return results


def render_report(results: list[CheckResult]) -> str:
    failed = [result for result in results if not result.ok]
    rows = [
        [
            result.name,
            result.path,
            result.status,
            result.rationale,
            "none" if not result.missing else "; ".join(f"`{pattern}`" for pattern in result.missing),
        ]
        for result in results
    ]
    return "\n".join(
        [
            "# Paper Consistency Audit",
            "",
            "This generated audit checks that paper-facing text contains the verified headline numbers and required scope caveats.",
            "It is a stale-text guardrail; claim correctness is still recomputed in `paper/claim_verification.md`.",
            "",
            f"Overall status: **{'PASS' if not failed else 'FAIL'}**",
            "",
            markdown_table(["Check", "File", "Status", "Why it matters", "Missing patterns"], rows),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_checks()
    write_text(args.out, render_report(results))
    failed = [result for result in results if not result.ok]
    print(f"wrote paper consistency audit to {args.out}")
    if failed:
        for result in failed:
            print(f"FAIL {result.path}: {result.name}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
