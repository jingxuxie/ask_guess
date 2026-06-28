from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


CRITICAL_ARTIFACTS = [
    "data/generated/episodes.jsonl",
    "data/generated/style_stress_episodes.jsonl",
    "data/generated/ambiguity_mix_shift_episodes.jsonl",
    "data/runs/offline_results.jsonl",
    "data/runs/ambiguity_mix_shift_results.jsonl",
    "data/runs/api_eval_100_corrected_results.jsonl",
    "data/runs/api_eval_100_cot_results.jsonl",
    "data/runs/api_style_stress_50_results.jsonl",
    "data/runs/api_second_model_25_results.jsonl",
    "data/runs/api_gpt_5_4_mini_test100_results.jsonl",
    "data/runs/api_gpt_5_5_test100_results.jsonl",
    "data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl",
    "data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl",
    "data/runs/api_cache.jsonl",
    "data/runs/api_second_model_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_cache.jsonl",
    "data/runs/api_gpt_5_5_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_scene_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_nl_cache.jsonl",
    "paper/dataset_card.md",
    "paper/claim_verification.md",
    "paper/claim_scope.md",
    "paper/paper_consistency_audit.md",
    "paper/supplement_audit.md",
    "paper/latex/main.tex",
    "paper/latex/refs.bib",
    "paper/latex/colm2026_conference.sty",
    "paper/latex/colm2026_conference.bst",
    "paper/latex/fancyhdr.sty",
    "paper/latex/natbib.sty",
    "paper/latex/math_commands.tex",
    "paper/latex/main.pdf",
]

SUPPORTING_ARTIFACTS = [
    "paper/tables/benchmark_categories.md",
    "paper/tables/qualitative_examples.md",
    "paper/tables/controller_analysis.md",
    "paper/tables/ambiguity_utility_diagnostic.md",
    "paper/tables/situated_contrast_analysis.md",
    "paper/tables/cost_sensitivity.md",
    "paper/tables/ambiguity_mix_shift.md",
    "paper/tables/clamber_external_sanity.md",
    "paper/tables/simulated_user_audit.md",
    "paper/tables/api_cache_replay_verification.md",
    "paper/tables/api_eval_100_corrected/paired_differences.md",
    "paper/tables/api_eval_100_corrected/subset_stability.md",
    "paper/tables/api_eval_100_corrected/calibration_by_margin.md",
    "paper/tables/api_eval_100_corrected/ecu_ablation.md",
    "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    "paper/tables/api_candidate_calibration.md",
    "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
    "paper/tables/api_eval_100_extended/failure_taxonomy.md",
    "paper/tables/api_eval_100_extended/question_usefulness.md",
    "paper/tables/api_style_stress_50/paired_differences.md",
    "paper/tables/api_style_stress_50/calibration_by_margin.md",
    "paper/tables/api_style_stress_50/failure_taxonomy.md",
    "paper/tables/api_style_stress_50/question_usefulness.md",
    "paper/tables/api_second_model_25/paired_differences.md",
    "paper/tables/api_second_model_25/category_breakdown.md",
    "paper/tables/api_gpt_5_4_mini_test100/paired_differences.md",
    "paper/tables/api_gpt_5_5_test100/paired_differences.md",
    "paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md",
    "paper/tables/api_gpt_5_4_mini_natural_language_test100/paired_differences.md",
    "paper/tables/api_gpt_5_4_mini_scene_format_robustness.md",
    "paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md",
    "paper/tables/current_model_sweep.md",
    "paper/tables/current_model_category_failure_modes.md",
    "paper/audits/AUDIT_SUMMARY.md",
    "paper/dataset_card.md",
    "paper/claim_scope.md",
    "paper/paper_consistency_audit.md",
    "paper/supplement_audit.md",
    "paper/figures/api_main_net_utility.svg",
    "paper/figures/api_category_net_utility.svg",
    "paper/figures/current_model_category_net_utility.svg",
    "paper/figures/api_calibration_ask_rate.svg",
    "paper/figures/cost_sensitivity_ask_cost.svg",
    "paper/figures/cost_sensitivity_wrong_cost.svg",
    "paper/supplement_manifest.md",
    "tests/test_core_invariants.py",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--style-episodes", default="data/generated/style_stress_episodes.jsonl")
    parser.add_argument("--offline-results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--api-cot-results", default="data/runs/api_eval_100_cot_results.jsonl")
    parser.add_argument("--api-style-results", default="data/runs/api_style_stress_50_results.jsonl")
    parser.add_argument("--api-second-model-results", default="data/runs/api_second_model_25_results.jsonl")
    parser.add_argument("--api-gpt54-mini-results", default="data/runs/api_gpt_5_4_mini_test100_results.jsonl")
    parser.add_argument("--api-gpt55-results", default="data/runs/api_gpt_5_5_test100_results.jsonl")
    parser.add_argument("--api-gpt54-mini-shuffled-results", default="data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl")
    parser.add_argument(
        "--api-gpt54-mini-natural-language-results",
        default="data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl",
    )
    parser.add_argument("--api-second-model-cache", default="data/runs/api_second_model_cache.jsonl")
    parser.add_argument("--ambiguity-mix-episodes", default="data/generated/ambiguity_mix_shift_episodes.jsonl")
    parser.add_argument("--ambiguity-mix-results", default="data/runs/ambiguity_mix_shift_results.jsonl")
    parser.add_argument("--api-cache", default="data/runs/api_cache.jsonl")
    parser.add_argument("--claim-verification", default="paper/claim_verification.md")
    parser.add_argument("--pdf", default="paper/latex/main.pdf")
    parser.add_argument("--latex-log", default="paper/latex/main.log")
    parser.add_argument("--out", default="paper/submission_readiness.md")
    return parser.parse_args()


def count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def artifact_rows(paths: list[str]) -> list[list[str]]:
    rows = []
    for name in paths:
        path = Path(name)
        if not path.exists():
            rows.append([name, "missing", "", ""])
            continue
        row_count = str(count_jsonl(path)) if path.suffix == ".jsonl" else "-"
        rows.append([name, "present", str(path.stat().st_size), row_count])
    return rows


def stats_for(rows: list[dict], split: str, policy: str) -> dict:
    grouped = group_rows(rows, ("split", "policy"))
    return aggregate(grouped[(split, policy)])


def paired_delta(rows: list[dict], policy_a: str, policy_b: str, split: str) -> float:
    filtered = [row for row in rows if row["split"] == split and row["policy"] in {policy_a, policy_b}]
    by_policy = {
        policy: {row["episode_id"]: float(row["reward"]) for row in filtered if row["policy"] == policy}
        for policy in {policy_a, policy_b}
    }
    shared = sorted(set(by_policy[policy_a]) & set(by_policy[policy_b]))
    return sum(by_policy[policy_a][episode_id] - by_policy[policy_b][episode_id] for episode_id in shared) / max(len(shared), 1)


def cache_totals(path: Path) -> dict[str, int | str]:
    totals: Counter[str] = Counter()
    models: Counter[str] = Counter()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            totals["responses"] += 1
            models[str(row.get("model", ""))] += 1
            usage = row.get("usage", {}) if isinstance(row.get("usage"), dict) else {}
            totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
            totals["total_tokens"] += int(usage.get("total_tokens", 0) or 0)
    totals["models"] = ", ".join(f"{model}: {count}" for model, count in sorted(models.items()))
    return dict(totals)


def claim_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8")
    match = re.search(r"Overall status:\s+\*\*(PASS|FAIL)\*\*", text)
    return match.group(1) if match else "unknown"


def pdf_page_count(path: Path) -> str:
    if not path.exists():
        return "missing"
    try:
        result = subprocess.run(["pdfinfo", str(path)], check=False, capture_output=True, text=True)
    except OSError:
        result = None
    if result is not None and result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return line.split(":", 1)[1].strip()
    count = len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))
    if count:
        return str(count)
    return "unknown"


def bibliography_start_page(path: Path) -> str:
    if not path.exists():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"\(./main\.bbl\s+\[(\d+)\]", text)
    if match:
        return match.group(1)
    return "unknown"


def metric_table(rows: list[dict], split: str, policies: list[str]) -> str:
    table_rows = []
    for policy in policies:
        stats = stats_for(rows, split, policy)
        table_rows.append(
            [
                policy,
                str(stats["n"]),
                format_float(stats["net_utility"]),
                f"[{format_float(stats['net_utility_ci_low'])}, {format_float(stats['net_utility_ci_high'])}]",
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    return markdown_table(
        ["Method", "N", "Net utility", "95% CI", "Success", "Ask rate", "Missed clarif.", "Unnecessary clarif."],
        table_rows,
    )


def validation_commands() -> str:
    return """```bash
conda run -n ask_dont_guess python -m unittest discover -s tests
conda run -n ask_dont_guess python -m compileall -q src tests
conda run -n ask_dont_guess python src/make_ambiguity_mix_shift.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --out data/runs/ambiguity_mix_shift_results.jsonl --eval-splits test,ood_ambiguity_mix
conda run -n ask_dont_guess python src/ambiguity_mix_shift_analysis.py
conda run -n ask_dont_guess python src/api_cache_replay_verification.py
conda run -n ask_dont_guess python src/simulated_user_audit.py
conda run -n ask_dont_guess python src/api_subset_stability.py
conda run -n ask_dont_guess python src/api_utility_sensitivity.py
conda run -n ask_dont_guess python src/ambiguity_utility_diagnostic.py
conda run -n ask_dont_guess python src/situated_contrast_analysis.py
conda run -n ask_dont_guess python src/paper_consistency_audit.py
conda run -n ask_dont_guess python src/verify_claims.py
conda run -n ask_dont_guess python src/make_dataset_card.py
conda run -n ask_dont_guess python src/make_claim_scope_report.py
cd paper/latex && latexmk -pdf -interaction=nonstopmode main.tex && cd ../..
conda run -n ask_dont_guess python src/make_submission_readiness_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py --manifest-only
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
conda run -n ask_dont_guess python src/audit_supplement_release.py
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
```"""


def cache_replay_commands() -> str:
    return """```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_corrected_replay.jsonl --summary-out /tmp/api_eval_100_corrected_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_cot_replay.jsonl --summary-out /tmp/api_eval_100_cot_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_ask_needed_cot --cache-only
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out /tmp/api_style_stress_50_replay.jsonl --summary-out /tmp/api_style_stress_50_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_second_model_25_replay.jsonl --summary-out /tmp/api_second_model_25_replay.md --cache data/runs/api_second_model_cache.jsonl --model gpt-4.1-nano --split test --limit-per-category 5 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```"""


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    style_episodes = read_jsonl(args.style_episodes)
    ambiguity_mix_episodes = read_jsonl(args.ambiguity_mix_episodes)
    offline_rows = read_jsonl(args.offline_results)
    ambiguity_mix_rows = read_jsonl(args.ambiguity_mix_results)
    api_rows = read_jsonl(args.api_results)
    cot_rows = read_jsonl(args.api_cot_results)
    style_rows = read_jsonl(args.api_style_results)
    second_model_rows = read_jsonl(args.api_second_model_results)
    gpt54_rows = read_jsonl(args.api_gpt54_mini_results)
    gpt55_rows = read_jsonl(args.api_gpt55_results)
    gpt54_shuffled_rows = read_jsonl(args.api_gpt54_mini_shuffled_results)
    gpt54_natural_language_rows = read_jsonl(args.api_gpt54_mini_natural_language_results)
    cache = cache_totals(Path(args.api_cache))
    second_model_cache = cache_totals(Path(args.api_second_model_cache))

    missing = [path for path in CRITICAL_ARTIFACTS if not Path(path).exists()]
    verification = claim_status(Path(args.claim_verification))
    pages = pdf_page_count(Path(args.pdf))
    references_start = bibliography_start_page(Path(args.latex_log))
    main_text_pages = str(int(references_start) - 1) if references_start.isdigit() else "unknown"
    page_budget_ok = main_text_pages.isdigit() and int(main_text_pages) <= 9
    ready = not missing and verification == "PASS" and pages not in {"missing", "unknown"} and page_budget_ok
    overall = "ready with stated limitations" if ready else "not ready: refresh missing or failed checks"

    main_direct = stats_for(api_rows, "test", "api_direct_act")
    main_ask = stats_for(api_rows, "test", "api_ask_needed")
    main_ecu = stats_for(api_rows, "test", "api_ecu")
    cot = stats_for(cot_rows, "test", "api_ask_needed_cot")
    style_direct = stats_for(style_rows, "style_test", "api_direct_act")
    style_ask = stats_for(style_rows, "style_test", "api_ask_needed")
    style_ecu = stats_for(style_rows, "style_test", "api_ecu")
    second_model_direct = stats_for(second_model_rows, "test", "api_direct_act")
    second_model_ask = stats_for(second_model_rows, "test", "api_ask_needed")
    second_model_ecu = stats_for(second_model_rows, "test", "api_ecu")
    gpt54_ask = stats_for(gpt54_rows, "test", "api_ask_needed")
    gpt54_cot = stats_for(gpt54_rows, "test", "api_ask_needed_cot")
    gpt54_ecu = stats_for(gpt54_rows, "test", "api_ecu")
    gpt55_ask = stats_for(gpt55_rows, "test", "api_ask_needed")
    gpt55_cot = stats_for(gpt55_rows, "test", "api_ask_needed_cot")
    gpt55_ecu = stats_for(gpt55_rows, "test", "api_ecu")
    gpt54_shuffled_ask = stats_for(gpt54_shuffled_rows, "test", "api_ask_needed")
    gpt54_shuffled_cot = stats_for(gpt54_shuffled_rows, "test", "api_ask_needed_cot")
    gpt54_shuffled_ecu = stats_for(gpt54_shuffled_rows, "test", "api_ecu")
    gpt54_natural_language_ask = stats_for(gpt54_natural_language_rows, "test", "api_ask_needed")
    gpt54_natural_language_cot = stats_for(gpt54_natural_language_rows, "test", "api_ask_needed_cot")
    gpt54_natural_language_ecu = stats_for(gpt54_natural_language_rows, "test", "api_ecu")
    offline_test_ecu = stats_for(offline_rows, "test", "ecu")
    offline_ood_ecu = stats_for(offline_rows, "ood_test", "ecu")
    ambiguity_mix_ecu = stats_for(ambiguity_mix_rows, "ood_ambiguity_mix", "ecu")
    ambiguity_mix_controller = stats_for(ambiguity_mix_rows, "ood_ambiguity_mix", "learned_controller")

    split_counts = Counter(episode["split"] for episode in episodes)
    style_category_counts = Counter(episode["ambiguity_type"] for episode in style_episodes)
    ambiguity_mix_split_counts = Counter(episode["split"] for episode in ambiguity_mix_episodes)

    claim_rows = [
        [
            "Clarification should be utility-dependent, not ambiguity-only.",
            "All 400 canonical test episodes have multiple candidate interpretations, but 200 are oracle-act and 200 are oracle-ask. Situated contrast slices show same-action and same-instruction families flipping ask/act decisions under context, ownership, equivalence, and risk.",
            "paper/tables/ambiguity_utility_diagnostic.md; paper/tables/situated_contrast_analysis.md; paper/tables/cost_sensitivity.md; paper/tables/qualitative_examples.md; paper/figures/cost_sensitivity_ask_cost.svg; paper/figures/cost_sensitivity_wrong_cost.svg",
        ],
        [
            "ECU improves first-turn API utility over prompting.",
            (
                f"Main 100: ECU {format_float(main_ecu['net_utility'])}, "
                f"Ask-Needed {format_float(main_ask['net_utility'])}, DirectAct {format_float(main_direct['net_utility'])}; "
                f"paired ECU - Ask-Needed {format_float(paired_delta(api_rows, 'api_ecu', 'api_ask_needed', 'test'))}. "
                "Leave-one-category and leave-one-episode subset checks keep the ECU - Ask-Needed delta positive."
            ),
            "data/runs/api_eval_100_corrected_results.jsonl; paper/tables/api_eval_100_corrected/paired_differences.md; paper/tables/api_eval_100_corrected/subset_stability.md",
        ],
        [
            "Private-reasoning helps with scale but does not replace utility calibration in general.",
            (
                f"GPT-4.1-mini CoT Ask-Needed utility {format_float(cot['net_utility'])}; "
                f"GPT-5.4-mini CoT {format_float(gpt54_cot['net_utility'])} versus ECU {format_float(gpt54_ecu['net_utility'])}; "
                f"GPT-5.5 CoT {format_float(gpt55_cot['net_utility'])} ties ECU {format_float(gpt55_ecu['net_utility'])} on the 100-episode subset."
            ),
            "data/runs/api_eval_100_cot_results.jsonl; data/runs/api_gpt_5_4_mini_test100_results.jsonl; data/runs/api_gpt_5_5_test100_results.jsonl; paper/tables/current_model_sweep.md",
        ],
        [
            "Current hosted models preserve the plain Ask-Needed calibration gap.",
            (
                f"GPT-5.4-mini: ECU {format_float(gpt54_ecu['net_utility'])}, Ask-Needed {format_float(gpt54_ask['net_utility'])}; "
                f"GPT-5.5: ECU {format_float(gpt55_ecu['net_utility'])}, Ask-Needed {format_float(gpt55_ask['net_utility'])}. "
                "ECU has zero missed and unnecessary clarifications in both current-model rows; the category failure-mode table localizes the remaining plain Ask-Needed gaps."
            ),
            "paper/tables/current_model_sweep.md; paper/tables/current_model_category_failure_modes.md; paper/figures/current_model_category_net_utility.svg; data/runs/api_gpt_5_4_mini_test100_results.jsonl; data/runs/api_gpt_5_5_test100_results.jsonl",
        ],
        [
            "ECU tracks utility margins.",
            (
                "Current calibration tables show ECU asks in ask-preferred bins and avoids act-preferred bins; "
                "prompted Ask-Needed asks in both bins. Cached API ECU candidate margins agree with oracle ask labels on 0.990 of main API rows."
            ),
            "paper/tables/api_eval_100_corrected/calibration_by_margin.md; paper/tables/api_style_stress_50/calibration_by_margin.md; paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md; paper/tables/api_candidate_calibration.md; paper/figures/api_calibration_ask_rate.svg",
        ],
        [
            "ECU uses plausible candidate probabilities, not perfect hidden-intent prediction.",
            (
                "On GPT-4.1-mini ECU rows, the model top success class matches the benchmark top-prior class on 0.970 of episodes, "
                "with mean prior TV 0.057; the top class matches the sampled hidden class on 0.770. "
                "Model and oracle utility margins remain strongly correlated."
            ),
            "paper/tables/api_candidate_calibration.md",
        ],
        [
            "ECU is stable under bounded scene-serialization perturbations.",
            (
                f"GPT-5.4-mini shuffled object order: ECU {format_float(gpt54_shuffled_ecu['net_utility'])}, "
                f"Ask-Needed {format_float(gpt54_shuffled_ask['net_utility'])}, CoT {format_float(gpt54_shuffled_cot['net_utility'])}; "
                "ECU changes ask/act decisions on 0/100 shared episodes. "
                f"Natural-language scene: ECU {format_float(gpt54_natural_language_ecu['net_utility'])}, "
                f"Ask-Needed {format_float(gpt54_natural_language_ask['net_utility'])}, "
                f"CoT {format_float(gpt54_natural_language_cot['net_utility'])}; "
                "ECU changes ask/act decisions on 1/100 shared episodes."
            ),
            "data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl; data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl; paper/tables/api_gpt_5_4_mini_scene_format_robustness.md; paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md",
        ],
        [
            "The main API utility advantage is not tied to one narrow scoring parameter.",
            "Fixed cached API outputs keep positive ECU - Ask-Needed deltas across ask-cost and wrong-action-cost rescoring, with minimum delta 0.138 and minimum paired-CI lower bound 0.070.",
            "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
        ],
        [
            "The result survives a small paraphrase and answer-style stress set.",
            (
                f"Style 50: ECU {format_float(style_ecu['net_utility'])}, Ask-Needed {format_float(style_ask['net_utility'])}, "
                f"DirectAct {format_float(style_direct['net_utility'])}; paired ECU - Ask-Needed "
                f"{format_float(paired_delta(style_rows, 'api_ecu', 'api_ask_needed', 'style_test'))}."
            ),
            "data/runs/api_style_stress_50_results.jsonl; paper/tables/api_style_stress_50/paired_differences.md",
        ],
        [
            "The direction survives a tiny second-model sanity check.",
            (
                f"gpt-4.1-nano 25: ECU {format_float(second_model_ecu['net_utility'])}, "
                f"Ask-Needed {format_float(second_model_ask['net_utility'])}, DirectAct {format_float(second_model_direct['net_utility'])}; "
                f"paired ECU - Ask-Needed {format_float(paired_delta(second_model_rows, 'api_ecu', 'api_ask_needed', 'test'))}."
            ),
            "data/runs/api_second_model_25_results.jsonl; paper/tables/api_second_model_25/paired_differences.md",
        ],
        [
            "Failure modes are qualitatively diagnostic.",
            "Failure taxonomy separates referential guessing, risk blindness, and equivalence blindness; question-usefulness tables show whether questions are needed and grounded.",
            "paper/tables/api_eval_100_extended/failure_taxonomy.md; paper/tables/api_eval_100_extended/question_usefulness.md; paper/tables/api_style_stress_50/failure_taxonomy.md; paper/tables/api_style_stress_50/question_usefulness.md",
        ],
        [
            "Author-style audits support benchmark and question sanity.",
            "Audit covers 100 scenarios and 100 sampled API questions; all scenario labels are ok and all audited ECU oracle-ask questions are natural and diagnostic.",
            "paper/audits/AUDIT_SUMMARY.md; paper/audits/scenario_audit_completed.md; paper/audits/question_audit_completed.md",
        ],
        [
            "The deterministic simulated user returns visibly diagnostic answers.",
            "Generated oracle-ask diagnostic answers resolve the hidden success class in 1233/1233 cases; actual API asked-row answers resolve in 184/184 cases.",
            "paper/tables/simulated_user_audit.md",
        ],
        [
            "Offline controller and OOD checks support the mechanism.",
            (
                f"Offline ECU test utility {format_float(offline_test_ecu['net_utility'])}; "
                f"OOD utility {format_float(offline_ood_ecu['net_utility'])}; "
                f"held-out ambiguity-mix ECU utility {format_float(ambiguity_mix_ecu['net_utility'])}."
            ),
            "data/runs/offline_results.jsonl; data/runs/ambiguity_mix_shift_results.jsonl; paper/tables/robustness_breakdown.md; paper/tables/ambiguity_mix_shift.md; paper/tables/controller_analysis.md",
        ],
        [
            "The learned controller has a useful category-transfer boundary.",
            (
                f"When trained without risk-sensitive or preference/social episodes, held-out ECU utility is "
                f"{format_float(ambiguity_mix_ecu['net_utility'])}, while the learned controller is "
                f"{format_float(ambiguity_mix_controller['net_utility'])} and asks on "
                f"{format_float(ambiguity_mix_controller['ask_rate'])} of held-out episodes."
            ),
            "data/generated/ambiguity_mix_shift_episodes.jsonl; paper/tables/ambiguity_mix_shift.md",
        ],
        [
            "External query-level ambiguity benchmarks motivate the task framing.",
            "CLAMBER sanity check: provided ambiguity prediction recall is 0.284 against `require_clarification`, with missed clarification rate 0.716.",
            "paper/tables/clamber_external_sanity.md",
        ],
        [
            "The shipped API evidence is cache-replayable without network calls.",
            "Cache-only replay reproduces all 2225 canonical API rows across the main, CoT, style-stress, second-model, current-model, and scene-format result files with zero stable-row mismatches.",
            "paper/tables/api_cache_replay_verification.md",
        ],
        [
            "Paper-facing numbers and caveats are stale-checked.",
            "The consistency audit verifies that the manuscript, long draft, readiness report, and claim-scope report carry the verified headline numbers and limitation language.",
            "paper/paper_consistency_audit.md",
        ],
    ]

    status_rows = [
        ["Overall status", overall],
        ["Claim verification", verification],
        ["Critical artifacts missing", ", ".join(missing) if missing else "none"],
        ["Compiled PDF pages", pages],
        ["References start page", references_start],
        ["Main text pages before references", main_text_pages],
        ["COLM 9-page main-text budget", "PASS" if page_budget_ok else "FAIL"],
        ["Main benchmark rows", str(len(episodes))],
        ["Main split counts", ", ".join(f"{key}: {value}" for key, value in sorted(split_counts.items()))],
        ["Style-stress rows", str(len(style_episodes))],
        ["Style-stress categories", ", ".join(f"{key}: {value}" for key, value in sorted(style_category_counts.items()))],
        ["Ambiguity-mix diagnostic rows", str(len(ambiguity_mix_episodes))],
        ["Ambiguity-mix split counts", ", ".join(f"{key}: {value}" for key, value in sorted(ambiguity_mix_split_counts.items()))],
        ["API cache responses", str(cache["responses"])],
        ["API cache total tokens", str(cache["total_tokens"])],
        ["API cache models", str(cache["models"])],
        ["Second-model cache responses", str(second_model_cache["responses"])],
        ["Second-model cache total tokens", str(second_model_cache["total_tokens"])],
        ["Second-model cache models", str(second_model_cache["models"])],
    ]

    limitation_rows = [
        ["Synthetic benchmark", "Claims are about situated instruction-following episodes generated by the local benchmark, not real household deployment."],
        ["Model coverage", "The headline API evidence uses gpt-4.1-mini, with 100-episode GPT-5.4-mini/GPT-5.5 sweeps and a 25-episode gpt-4.1-nano sanity check; open-weight and multimodal agents remain future work."],
        ["Scale", "Main API result is 100 stratified episodes, with subset-stability checks and a 50-episode style-stress set; offline results cover the full generated test/OOD splits."],
        ["User model", "Clarification answers are deterministic simulated user answers; the visible-answer audit supports diagnostic clarity, but this is not a human-response study."],
        ["Submission framing", "The strongest claim is value-of-information calibration for first-turn clarify-vs-act decisions, not general interactive dialogue mastery."],
    ]

    text = "\n".join(
        [
            "# Submission Readiness Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "This report maps the current paper claims to the canonical evidence package and highlights what is ready versus still limited.",
            "",
            "## Status",
            "",
            markdown_table(["Item", "Value"], status_rows),
            "## Claim-to-Evidence Map",
            "",
            markdown_table(["Claim", "Current evidence", "Primary artifacts"], claim_rows),
            "## Main API Metrics",
            "",
            metric_table(api_rows, "test", ["api_direct_act", "api_ask_needed", "api_ecu"]),
            "## Auxiliary CoT API Metric",
            "",
            metric_table(cot_rows, "test", ["api_ask_needed_cot"]),
            "## Style-Stress API Metrics",
            "",
            metric_table(style_rows, "style_test", ["api_direct_act", "api_ask_needed", "api_ecu"]),
            "## Auxiliary Second-Model API Metrics",
            "",
            metric_table(second_model_rows, "test", ["api_direct_act", "api_ask_needed", "api_ecu"]),
            "## Critical Artifacts",
            "",
            markdown_table(["Artifact", "Status", "Bytes", "JSONL rows"], artifact_rows(CRITICAL_ARTIFACTS)),
            "## Supporting Artifacts",
            "",
            markdown_table(["Artifact", "Status", "Bytes", "JSONL rows"], artifact_rows(SUPPORTING_ARTIFACTS)),
            "## Validation Commands",
            "",
            validation_commands(),
            "",
            "## Cache-Only API Replays",
            "",
            "These commands should fail on cache miss and should not spend API budget.",
            "",
            cache_replay_commands(),
            "",
            "## Known Limitations",
            "",
            markdown_table(["Limitation", "Submission framing"], limitation_rows),
        ]
    )
    write_text(args.out, text)
    print(f"wrote submission readiness report to {args.out}")
    print(f"overall status: {overall}")


if __name__ == "__main__":
    main()
