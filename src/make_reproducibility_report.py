from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


ARTIFACTS = [
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
    "data/runs/api_cache.jsonl",
    "data/runs/api_second_model_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_cache.jsonl",
    "data/runs/api_gpt_5_5_cache.jsonl",
    "data/runs/api_gpt_5_4_mini_scene_cache.jsonl",
    "paper/tables/benchmark_categories.md",
    "paper/tables/qualitative_examples.md",
    "paper/tables/main_results.md",
    "paper/tables/category_breakdown.md",
    "paper/tables/paired_differences.md",
    "paper/tables/robustness_breakdown.md",
    "paper/tables/controller_analysis.md",
    "paper/tables/ambiguity_utility_diagnostic.md",
    "paper/tables/situated_contrast_analysis.md",
    "paper/tables/ambiguity_mix_shift.md",
    "paper/tables/clamber_external_sanity.md",
    "paper/tables/simulated_user_audit.md",
    "paper/tables/api_cache_replay_verification.md",
    "paper/tables/api_eval_100_corrected_results.md",
    "paper/tables/api_eval_100_corrected/category_breakdown.md",
    "paper/tables/api_eval_100_corrected/paired_differences.md",
    "paper/tables/api_eval_100_corrected/subset_stability.md",
    "paper/tables/api_eval_100_corrected/ecu_ablation.md",
    "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
    "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    "paper/tables/api_eval_100_corrected/calibration_by_margin.md",
    "paper/tables/api_eval_100_cot_results.md",
    "paper/tables/api_eval_100_cot/main_results.md",
    "paper/tables/api_eval_100_cot/category_breakdown.md",
    "paper/tables/api_eval_100_extended/main_results.md",
    "paper/tables/api_eval_100_extended/category_breakdown.md",
    "paper/tables/api_eval_100_extended/paired_differences.md",
    "paper/tables/api_eval_100_extended/failure_taxonomy.md",
    "paper/tables/api_eval_100_extended/question_usefulness.md",
    "paper/tables/api_style_stress_50_results.md",
    "paper/tables/api_style_stress_50/main_results.md",
    "paper/tables/api_style_stress_50/category_breakdown.md",
    "paper/tables/api_style_stress_50/paired_differences.md",
    "paper/tables/api_style_stress_50/calibration_by_margin.md",
    "paper/tables/api_style_stress_50/failure_taxonomy.md",
    "paper/tables/api_style_stress_50/question_usefulness.md",
    "paper/tables/api_second_model_25_results.md",
    "paper/tables/api_second_model_25/main_results.md",
    "paper/tables/api_second_model_25/category_breakdown.md",
    "paper/tables/api_second_model_25/paired_differences.md",
    "paper/tables/api_second_model_25/failure_examples.md",
    "paper/tables/api_gpt_5_4_mini_test100_results.md",
    "paper/tables/api_gpt_5_4_mini_test100/main_results.md",
    "paper/tables/api_gpt_5_4_mini_test100/category_breakdown.md",
    "paper/tables/api_gpt_5_4_mini_test100/paired_differences.md",
    "paper/tables/api_gpt_5_4_mini_test100/failure_examples.md",
    "paper/tables/api_gpt_5_5_test100_results.md",
    "paper/tables/api_gpt_5_5_test100/main_results.md",
    "paper/tables/api_gpt_5_5_test100/category_breakdown.md",
    "paper/tables/api_gpt_5_5_test100/paired_differences.md",
    "paper/tables/api_gpt_5_5_test100/failure_examples.md",
    "paper/tables/api_gpt_5_4_mini_shuffled_test100_results.md",
    "paper/tables/api_gpt_5_4_mini_shuffled_test100/main_results.md",
    "paper/tables/api_gpt_5_4_mini_shuffled_test100/category_breakdown.md",
    "paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md",
    "paper/tables/api_gpt_5_4_mini_shuffled_test100/failure_examples.md",
    "paper/tables/api_gpt_5_4_mini_scene_format_robustness.md",
    "paper/tables/current_model_sweep.md",
    "paper/tables/cost_sensitivity.md",
    "paper/figures/api_main_net_utility.svg",
    "paper/figures/api_category_net_utility.svg",
    "paper/figures/api_calibration_ask_rate.svg",
    "paper/figures/cost_sensitivity_ask_cost.svg",
    "paper/figures/cost_sensitivity_wrong_cost.svg",
    "paper/figures/FIGURE_INDEX.md",
    "paper/audits/AUDIT_SUMMARY.md",
    "paper/audits/AUDIT_INDEX.md",
    "paper/audits/scenario_audit_completed.md",
    "paper/audits/question_audit_completed.md",
    "paper/dataset_card.md",
    "paper/claim_verification.md",
    "paper/claim_scope.md",
    "paper/paper_consistency_audit.md",
    "paper/submission_readiness.md",
    "paper/supplement_manifest.md",
    "paper/supplement_audit.md",
    "src/api_cache_replay_verification.py",
    "src/api_subset_stability.py",
    "src/audit_supplement_release.py",
    "src/api_ecu_margin_analysis.py",
    "src/api_utility_sensitivity.py",
    "src/make_audit_packet.py",
    "src/complete_audit_packet.py",
    "src/clarify_to_act/environment.py",
    "src/make_dataset_card.py",
    "src/ambiguity_utility_diagnostic.py",
    "src/situated_contrast_analysis.py",
    "src/make_ambiguity_mix_shift.py",
    "src/ambiguity_mix_shift_analysis.py",
    "src/clamber_external_sanity.py",
    "src/simulated_user_audit.py",
    "src/current_model_sweep_report.py",
    "src/paper_consistency_audit.py",
    "src/make_claim_scope_report.py",
    "src/run_api_experiment.py",
    "src/verify_claims.py",
    "tests/test_core_invariants.py",
    "paper/latex/main.tex",
    "paper/latex/refs.bib",
    "paper/latex/colm2026_conference.sty",
    "paper/latex/colm2026_conference.bst",
    "paper/latex/fancyhdr.sty",
    "paper/latex/natbib.sty",
    "paper/latex/math_commands.tex",
    "paper/latex/main.pdf",
]

OFFLINE_POLICY_ORDER = [
    "direct_act",
    "ask_always",
    "raw_ambiguity",
    "prompted_heuristic",
    "ecu",
    "ecu_threshold",
    "learned_controller",
]

API_POLICY_ORDER = ["api_direct_act", "api_ask_needed", "api_ecu"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--offline-results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--api-style-results", default="data/runs/api_style_stress_50_results.jsonl")
    parser.add_argument("--api-second-model-results", default="data/runs/api_second_model_25_results.jsonl")
    parser.add_argument("--api-gpt54-mini-results", default="data/runs/api_gpt_5_4_mini_test100_results.jsonl")
    parser.add_argument("--api-gpt55-results", default="data/runs/api_gpt_5_5_test100_results.jsonl")
    parser.add_argument("--api-gpt54-mini-shuffled-results", default="data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl")
    parser.add_argument("--api-cache", default="data/runs/api_cache.jsonl")
    parser.add_argument("--api-second-model-cache", default="data/runs/api_second_model_cache.jsonl")
    parser.add_argument("--api-gpt54-mini-cache", default="data/runs/api_gpt_5_4_mini_cache.jsonl")
    parser.add_argument("--api-gpt55-cache", default="data/runs/api_gpt_5_5_cache.jsonl")
    parser.add_argument("--api-gpt54-mini-scene-cache", default="data/runs/api_gpt_5_4_mini_scene_cache.jsonl")
    parser.add_argument("--out", default="paper/reproducibility.md")
    return parser.parse_args()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def jsonl_count(path: Path) -> int:
    with path.open("r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def artifact_table(paths: list[str]) -> str:
    rows = []
    for name in paths:
        path = Path(name)
        if not path.exists():
            rows.append([name, "missing", "", ""])
            continue
        rows.append([name, str(path.stat().st_size), str(jsonl_count(path)) if path.suffix == ".jsonl" else "-", sha256(path)])
    return markdown_table(["Artifact", "Bytes", "JSONL rows", "SHA256"], rows)


def split_category_summary(episodes: list[dict]) -> str:
    by_split = Counter(ep["split"] for ep in episodes)
    by_category = Counter(ep["ambiguity_type"] for ep in episodes)
    oracle_ask_rate = sum(1 for ep in episodes if ep["oracle_should_ask"]) / max(len(episodes), 1)
    rows = [["total", str(len(episodes)), "-", format_float(oracle_ask_rate)]]
    rows.extend([["split", split, str(count), ""] for split, count in sorted(by_split.items())])
    rows.extend([["category", category, str(count), ""] for category, count in sorted(by_category.items())])
    return markdown_table(["Group", "Name", "Count", "Oracle ask rate"], rows)


def policy_key(policy: str, order: list[str]) -> tuple[int, str]:
    try:
        return (order.index(policy), policy)
    except ValueError:
        return (999, policy)


def metric_table(rows: list[dict], order: list[str], split_filter: str | None = None) -> str:
    filtered = [row for row in rows if split_filter is None or row["split"] == split_filter]
    table_rows = []
    grouped = group_rows(filtered, ("split", "policy"))
    for split, policy in sorted(grouped, key=lambda item: (item[0][0], policy_key(item[0][1], order))):
        stats = aggregate(grouped[(split, policy)])
        table_rows.append(
            [
                split,
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
        ["Split", "Method", "N", "Net utility", "95% CI", "Success", "Ask rate", "Missed clarif.", "Unnecessary clarif."],
        table_rows,
    )


def cache_summary(path: Path) -> str:
    entries = 0
    models: Counter[str] = Counter()
    tokens: Counter[str] = Counter()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            entries += 1
            models[str(row.get("model", ""))] += 1
            usage = row.get("usage", {}) if isinstance(row.get("usage"), dict) else {}
            tokens["input"] += int(usage.get("input_tokens", 0) or 0)
            tokens["output"] += int(usage.get("output_tokens", 0) or 0)
            tokens["total"] += int(usage.get("total_tokens", 0) or 0)
    model_text = ", ".join(f"{model}: {count}" for model, count in sorted(models.items()))
    return markdown_table(
        ["Cache entries", "Models", "Input tokens", "Output tokens", "Total tokens"],
        [[str(entries), model_text, str(tokens["input"]), str(tokens["output"]), str(tokens["total"])]],
    )


def command_block() -> str:
    return """## Reproduction Commands

Free deterministic regeneration:

```bash
conda run -n ask_dont_guess python src/generate_scenarios.py --train 600 --dev 200 --test 400 --ood-test 200 --seed 13 --out data/generated/episodes.jsonl
conda run -n ask_dont_guess python src/benchmark_categories.py --episodes data/generated/episodes.jsonl --out paper/tables/benchmark_categories.md
conda run -n ask_dont_guess python src/qualitative_examples.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/qualitative_examples.md
conda run -n ask_dont_guess python src/make_dataset_card.py
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/offline_results.jsonl
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/offline_results.jsonl --out-dir paper/tables
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out-dir paper/tables/api_eval_100_extended
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/offline_results.jsonl --out paper/tables/paired_differences.md --splits test,ood_test --comparisons ecu:prompted_heuristic,learned_controller:prompted_heuristic,ecu:ask_always,ecu:direct_act
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_direct_act,api_ask_needed:api_direct_act
conda run -n ask_dont_guess python src/api_subset_stability.py --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/subset_stability.md
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out paper/tables/api_eval_100_extended/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed_cot,api_ecu:api_ask_needed,api_ask_needed_cot:api_ask_needed,api_ask_needed_cot:api_direct_act
conda run -n ask_dont_guess python src/make_style_stress_episodes.py --episodes data/generated/episodes.jsonl --source-split test --out-split style_test --limit-per-category 10 --out data/generated/style_stress_episodes.jsonl
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/api_style_stress_50_results.jsonl --out-dir paper/tables/api_style_stress_50
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/paired_differences.md --splits style_test --comparisons api_ecu:api_ask_needed,api_ecu:api_direct_act,api_ask_needed:api_direct_act
conda run -n ask_dont_guess python src/analyze_results.py --results data/runs/api_second_model_25_results.jsonl --out-dir paper/tables/api_second_model_25
conda run -n ask_dont_guess python src/paired_differences.py --results data/runs/api_second_model_25_results.jsonl --out paper/tables/api_second_model_25/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_direct_act,api_ask_needed:api_direct_act
conda run -n ask_dont_guess python src/calibration_analysis.py --episodes data/generated/episodes.jsonl --results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/calibration_by_margin.md
conda run -n ask_dont_guess python src/calibration_analysis.py --episodes data/generated/style_stress_episodes.jsonl --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/calibration_by_margin.md
conda run -n ask_dont_guess python src/failure_taxonomy.py --episodes data/generated/episodes.jsonl --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out paper/tables/api_eval_100_extended/failure_taxonomy.md
conda run -n ask_dont_guess python src/failure_taxonomy.py --episodes data/generated/style_stress_episodes.jsonl --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/failure_taxonomy.md
conda run -n ask_dont_guess python src/question_usefulness_analysis.py --results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --out paper/tables/api_eval_100_extended/question_usefulness.md
conda run -n ask_dont_guess python src/question_usefulness_analysis.py --results data/runs/api_style_stress_50_results.jsonl --out paper/tables/api_style_stress_50/question_usefulness.md
conda run -n ask_guess python src/analyze_results.py --results data/runs/api_gpt_5_4_mini_test100_results.jsonl --out-dir paper/tables/api_gpt_5_4_mini_test100
conda run -n ask_guess python src/analyze_results.py --results data/runs/api_gpt_5_5_test100_results.jsonl --out-dir paper/tables/api_gpt_5_5_test100
conda run -n ask_guess python src/paired_differences.py --results data/runs/api_gpt_5_4_mini_test100_results.jsonl --out paper/tables/api_gpt_5_4_mini_test100/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_ask_needed_cot,api_ecu:api_direct_act
conda run -n ask_guess python src/paired_differences.py --results data/runs/api_gpt_5_5_test100_results.jsonl --out paper/tables/api_gpt_5_5_test100/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_ask_needed_cot,api_ecu:api_direct_act
conda run -n ask_guess python src/current_model_sweep_report.py --run gpt-4.1-mini=data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl --run gpt-5.4-mini=data/runs/api_gpt_5_4_mini_test100_results.jsonl --run gpt-5.5=data/runs/api_gpt_5_5_test100_results.jsonl --out paper/tables/current_model_sweep.md
conda run -n ask_guess python src/analyze_results.py --results data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl --out-dir paper/tables/api_gpt_5_4_mini_shuffled_test100
conda run -n ask_guess python src/paired_differences.py --results data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl --out paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md --splits test --comparisons api_ecu:api_ask_needed,api_ecu:api_ask_needed_cot,api_ecu:api_direct_act
conda run -n ask_guess python src/scene_format_robustness_report.py --baseline data/runs/api_gpt_5_4_mini_test100_results.jsonl --perturbed data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl --out paper/tables/api_gpt_5_4_mini_scene_format_robustness.md
conda run -n ask_dont_guess python src/api_cache_replay_verification.py --out paper/tables/api_cache_replay_verification.md
conda run -n ask_dont_guess python src/api_ecu_ablation.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/ecu_ablation.md
conda run -n ask_dont_guess python src/api_utility_sensitivity.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/utility_sensitivity.md
conda run -n ask_dont_guess python src/api_ecu_margin_analysis.py --api-results data/runs/api_eval_100_corrected_results.jsonl --out paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md
conda run -n ask_dont_guess python src/make_audit_packet.py --episodes data/generated/episodes.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl,data/runs/api_eval_100_cot_results.jsonl,data/runs/api_style_stress_50_results.jsonl --scenarios-per-category 20 --questions 100 --out-dir paper/audits
conda run -n ask_dont_guess python src/complete_audit_packet.py --audit-dir paper/audits
conda run -n ask_dont_guess python src/robustness_analysis.py --episodes data/generated/episodes.jsonl --results data/runs/offline_results.jsonl --out paper/tables/robustness_breakdown.md
conda run -n ask_dont_guess python src/controller_analysis.py --episodes data/generated/episodes.jsonl --offline-results data/runs/offline_results.jsonl --out paper/tables/controller_analysis.md
conda run -n ask_dont_guess python src/ambiguity_utility_diagnostic.py --episodes data/generated/episodes.jsonl --offline-results data/runs/offline_results.jsonl --out paper/tables/ambiguity_utility_diagnostic.md
conda run -n ask_dont_guess python src/situated_contrast_analysis.py --episodes data/generated/episodes.jsonl --out paper/tables/situated_contrast_analysis.md
conda run -n ask_dont_guess python src/make_ambiguity_mix_shift.py --out data/generated/ambiguity_mix_shift_episodes.jsonl
conda run -n ask_dont_guess python src/run_experiment.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --out data/runs/ambiguity_mix_shift_results.jsonl --eval-splits test,ood_ambiguity_mix
conda run -n ask_dont_guess python src/ambiguity_mix_shift_analysis.py --episodes data/generated/ambiguity_mix_shift_episodes.jsonl --results data/runs/ambiguity_mix_shift_results.jsonl --out paper/tables/ambiguity_mix_shift.md
mkdir -p data/external
curl -L https://raw.githubusercontent.com/zt991211/CLAMBER/main/clamber_benchmark.jsonl -o data/external/clamber_benchmark.jsonl
conda run -n ask_dont_guess python src/clamber_external_sanity.py --input data/external/clamber_benchmark.jsonl --out paper/tables/clamber_external_sanity.md
conda run -n ask_dont_guess python src/simulated_user_audit.py --out paper/tables/simulated_user_audit.md
conda run -n ask_dont_guess python src/paper_consistency_audit.py --out paper/paper_consistency_audit.md
conda run -n ask_dont_guess python src/cost_sensitivity.py --episodes data/generated/episodes.jsonl --out paper/tables/cost_sensitivity.md
conda run -n ask_dont_guess python src/make_figures.py --api-results data/runs/api_eval_100_corrected_results.jsonl --cost-table paper/tables/cost_sensitivity.md --out-dir paper/figures
conda run -n ask_dont_guess python -m unittest discover -s tests
conda run -n ask_dont_guess python src/verify_claims.py --episodes data/generated/episodes.jsonl --offline-results data/runs/offline_results.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --api-cot-results data/runs/api_eval_100_cot_results.jsonl --style-episodes data/generated/style_stress_episodes.jsonl --api-style-results data/runs/api_style_stress_50_results.jsonl --api-cache data/runs/api_cache.jsonl --out paper/claim_verification.md
conda run -n ask_dont_guess python src/make_claim_scope_report.py
conda run -n ask_dont_guess python src/make_submission_readiness_report.py --episodes data/generated/episodes.jsonl --style-episodes data/generated/style_stress_episodes.jsonl --offline-results data/runs/offline_results.jsonl --api-results data/runs/api_eval_100_corrected_results.jsonl --api-cot-results data/runs/api_eval_100_cot_results.jsonl --api-style-results data/runs/api_style_stress_50_results.jsonl --api-cache data/runs/api_cache.jsonl --claim-verification paper/claim_verification.md --pdf paper/latex/main.pdf --out paper/submission_readiness.md
conda run -n ask_dont_guess python src/make_supplement_package.py --manifest-only
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
conda run -n ask_dont_guess python src/audit_supplement_release.py
conda run -n ask_dont_guess python src/make_reproducibility_report.py
conda run -n ask_dont_guess python src/make_supplement_package.py
```

Bounded paid API command for the auxiliary private-reasoning baseline. It is cached in `data/runs/api_cache.jsonl` and should not be rerun unless this baseline needs to be regenerated:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/api_eval_100_cot_results.jsonl --summary-out paper/tables/api_eval_100_cot_results.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_ask_needed_cot
```

Bounded paid API command for the 50-episode paraphrase and answer-style stress set. It is cached in `data/runs/api_cache.jsonl` and should not be rerun unless this stress set needs to be regenerated:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out data/runs/api_style_stress_50_results.jsonl --summary-out paper/tables/api_style_stress_50_results.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu
```

Bounded paid API commands for the current-model 100-episode sweep. These were run after smoke tests and are cached in separate model-specific cache files:

```bash
conda run -n ask_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/api_gpt_5_4_mini_test100_results.jsonl --summary-out paper/tables/api_gpt_5_4_mini_test100_results.md --cache data/runs/api_gpt_5_4_mini_cache.jsonl --api-key-path apikey.txt --model gpt-5.4-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu
conda run -n ask_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/api_gpt_5_5_test100_results.jsonl --summary-out paper/tables/api_gpt_5_5_test100_results.md --cache data/runs/api_gpt_5_5_cache.jsonl --api-key-path apikey.txt --model gpt-5.5 --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu
```

Bounded paid API command for the GPT-5.4-mini shuffled-object-order scene-format robustness check:

```bash
conda run -n ask_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl --summary-out paper/tables/api_gpt_5_4_mini_shuffled_test100_results.md --cache data/runs/api_gpt_5_4_mini_scene_cache.jsonl --api-key-path apikey.txt --model gpt-5.4-mini --split test --limit-per-category 20 --scene-format shuffled_json --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu
```

Safe cached API replay, with no network calls and no API spending. This fails on any cache miss:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_corrected_replay.jsonl --summary-out /tmp/api_eval_100_corrected_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

Safe cached replay for the auxiliary private-reasoning baseline:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_eval_100_cot_replay.jsonl --summary-out /tmp/api_eval_100_cot_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split test --limit-per-category 20 --policies api_ask_needed_cot --cache-only
```

Safe cached replay for the style-stress set:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/style_stress_episodes.jsonl --out /tmp/api_style_stress_50_replay.jsonl --summary-out /tmp/api_style_stress_50_replay.md --cache data/runs/api_cache.jsonl --model gpt-4.1-mini --split style_test --limit-per-category 10 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

Safe cached replay for the auxiliary 25-episode gpt-4.1-nano second-model sanity check:

```bash
conda run -n ask_dont_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_second_model_25_replay.jsonl --summary-out /tmp/api_second_model_25_replay.md --cache data/runs/api_second_model_cache.jsonl --model gpt-4.1-nano --split test --limit-per-category 5 --policies api_direct_act,api_ask_needed,api_ecu --cache-only
```

Safe cached replay for the current-model 100-episode sweeps:

```bash
conda run -n ask_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_gpt_5_4_mini_test100_replay.jsonl --summary-out /tmp/api_gpt_5_4_mini_test100_replay.md --cache data/runs/api_gpt_5_4_mini_cache.jsonl --model gpt-5.4-mini --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu --cache-only
conda run -n ask_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_gpt_5_5_test100_replay.jsonl --summary-out /tmp/api_gpt_5_5_test100_replay.md --cache data/runs/api_gpt_5_5_cache.jsonl --model gpt-5.5 --split test --limit-per-category 20 --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu --cache-only
```

Safe cached replay for the shuffled-object-order scene-format robustness check:

```bash
conda run -n ask_guess python src/run_api_experiment.py --episodes data/generated/episodes.jsonl --out /tmp/api_gpt_5_4_mini_shuffled_test100_replay.jsonl --summary-out /tmp/api_gpt_5_4_mini_shuffled_test100_replay.md --cache data/runs/api_gpt_5_4_mini_scene_cache.jsonl --model gpt-5.4-mini --split test --limit-per-category 20 --scene-format shuffled_json --policies api_direct_act,api_ask_needed,api_ask_needed_cot,api_ecu --cache-only
```

Paper build:

```bash
cd paper/latex && make
```

Supplement archive:

```bash
conda run -n ask_dont_guess python src/make_supplement_package.py
```
"""


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    offline_rows = read_jsonl(args.offline_results)
    api_rows = read_jsonl(args.api_results)
    api_style_rows = read_jsonl(args.api_style_results)
    api_second_model_rows = read_jsonl(args.api_second_model_results)
    api_gpt54_mini_rows = read_jsonl(args.api_gpt54_mini_results)
    api_gpt55_rows = read_jsonl(args.api_gpt55_results)
    api_gpt54_mini_shuffled_rows = read_jsonl(args.api_gpt54_mini_shuffled_results)

    parts = [
        "# Reproducibility Report",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "This report records the canonical data, result, cache, and paper artifacts used by the current draft.",
        "",
        "## Dataset Summary",
        "",
        split_category_summary(episodes),
        "## Offline Metrics",
        "",
        metric_table(offline_rows, OFFLINE_POLICY_ORDER),
        "## API Metrics",
        "",
        metric_table(api_rows, API_POLICY_ORDER, split_filter="test"),
        "## API Style-Stress Metrics",
        "",
        metric_table(api_style_rows, API_POLICY_ORDER, split_filter="style_test"),
        "## Auxiliary Second-Model API Metrics",
        "",
        "This small check uses gpt-4.1-nano on 25 stratified test episodes and is not the headline API result.",
        "",
        metric_table(api_second_model_rows, API_POLICY_ORDER, split_filter="test"),
        "## Current-Model API Metrics",
        "",
        "GPT-5.4-mini on the same 100 stratified test episodes:",
        "",
        metric_table(api_gpt54_mini_rows, ["api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"], split_filter="test"),
        "",
        "GPT-5.5 on the same 100 stratified test episodes:",
        "",
        metric_table(api_gpt55_rows, ["api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"], split_filter="test"),
        "## Scene-Format Robustness API Metrics",
        "",
        "GPT-5.4-mini on the same 100 stratified test episodes with visible scene object order reversed:",
        "",
        metric_table(api_gpt54_mini_shuffled_rows, ["api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"], split_filter="test"),
        "## API Cache",
        "",
        cache_summary(Path(args.api_cache)),
        "## Auxiliary Second-Model API Cache",
        "",
        cache_summary(Path(args.api_second_model_cache)),
        "## Current-Model API Caches",
        "",
        "GPT-5.4-mini cache:",
        "",
        cache_summary(Path(args.api_gpt54_mini_cache)),
        "",
        "GPT-5.5 cache:",
        "",
        cache_summary(Path(args.api_gpt55_cache)),
        "",
        "GPT-5.4-mini shuffled-scene cache:",
        "",
        cache_summary(Path(args.api_gpt54_mini_scene_cache)),
        "## Artifact Hashes",
        "",
        artifact_table(ARTIFACTS),
        command_block(),
    ]
    write_text(args.out, "\n".join(parts))
    print(f"wrote reproducibility report to {args.out}")


if __name__ == "__main__":
    main()
