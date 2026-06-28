from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

from api_ecu_ablation import ABLATIONS, replay_row
from api_cache_replay_verification import run_checks as api_cache_replay_checks
from api_candidate_calibration import pearson as candidate_pearson
from api_candidate_calibration import row_records as candidate_row_records
from api_candidate_calibration import spearman as candidate_spearman
from api_subset_stability import CATEGORY_ORDER as API_SUBSET_CATEGORY_ORDER
from api_subset_stability import mean_delta as api_subset_mean_delta
from api_subset_stability import stratified_bootstrap_ci as api_subset_stratified_bootstrap_ci
from api_utility_sensitivity import adjusted_rows as api_cost_adjusted_rows
from api_utility_sensitivity import paired_delta as api_cost_paired_delta
from api_utility_sensitivity import paired_delta_ci as api_cost_paired_delta_ci
from ambiguity_utility_diagnostic import UncertaintyOnlyController
from ambiguity_utility_diagnostic import raw_ambiguity_rows as ambiguity_raw_rows
from ambiguity_utility_diagnostic import uncertainty_controller_rows as ambiguity_controller_rows
from calibration_analysis import margin_bin
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table
from failure_taxonomy import classify_failure
from paper_consistency_audit import DEFAULT_OUT as PAPER_CONSISTENCY_OUT
from paper_consistency_audit import run_checks as paper_consistency_run_checks
from robustness_analysis import HELDOUT_TYPES, episode_has_heldout_object
from situated_contrast_analysis import contrast_slices as situated_contrast_slices
from situated_contrast_analysis import normalized_entropy as situated_normalized_entropy
from run_api_experiment import API_ECU_ASK_MARGIN
from simulated_user_audit import DEFAULT_API_RESULTS as SIM_USER_API_RESULTS
from simulated_user_audit import DEFAULT_EPISODES as SIM_USER_EPISODES
from simulated_user_audit import api_audit_rows as sim_user_api_audit_rows
from simulated_user_audit import generated_audit_rows as sim_user_generated_audit_rows
from simulated_user_audit import read_jsonl_paths as sim_user_read_jsonl_paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--offline-results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--api-cot-results", default="data/runs/api_eval_100_cot_results.jsonl")
    parser.add_argument("--style-episodes", default="data/generated/style_stress_episodes.jsonl")
    parser.add_argument("--api-style-results", default="data/runs/api_style_stress_50_results.jsonl")
    parser.add_argument("--api-second-model-results", default="data/runs/api_second_model_25_results.jsonl")
    parser.add_argument("--api-second-model-cache", default="data/runs/api_second_model_cache.jsonl")
    parser.add_argument("--api-gpt54-mini-results", default="data/runs/api_gpt_5_4_mini_test100_results.jsonl")
    parser.add_argument("--api-gpt55-results", default="data/runs/api_gpt_5_5_test100_results.jsonl")
    parser.add_argument("--api-gpt54-mini-shuffled-results", default="data/runs/api_gpt_5_4_mini_shuffled_test100_results.jsonl")
    parser.add_argument(
        "--api-gpt54-mini-natural-language-results",
        default="data/runs/api_gpt_5_4_mini_natural_language_test100_results.jsonl",
    )
    parser.add_argument("--ambiguity-mix-episodes", default="data/generated/ambiguity_mix_shift_episodes.jsonl")
    parser.add_argument("--ambiguity-mix-results", default="data/runs/ambiguity_mix_shift_results.jsonl")
    parser.add_argument("--api-cache", default="data/runs/api_cache.jsonl")
    parser.add_argument("--out", default="paper/claim_verification.md")
    return parser.parse_args()


def check_equal(rows: list[list[str]], claim: str, observed: object, expected: object, evidence: str) -> bool:
    ok = observed == expected
    rows.append([claim, str(expected), str(observed), "PASS" if ok else "FAIL", evidence])
    return ok


def check_float(rows: list[list[str]], claim: str, observed: float, expected: float, evidence: str, digits: int = 3) -> bool:
    observed_text = format_float(observed, digits)
    expected_text = format_float(expected, digits)
    ok = observed_text == expected_text
    rows.append([claim, expected_text, observed_text, "PASS" if ok else "FAIL", evidence])
    return ok


def cache_totals(path: str) -> dict[str, int]:
    totals = Counter()
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            totals["responses"] += 1
            usage = row.get("usage", {}) if isinstance(row.get("usage"), dict) else {}
            totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
            totals["total_tokens"] += int(usage.get("total_tokens", 0) or 0)
    return dict(totals)


def audit_summary_counts(path: str) -> dict[str, int]:
    text = Path(path).read_text(encoding="utf-8")
    scenario_match = re.search(r"## Scenario Audit.*?- Total reviewed: (\d+).*?- `ok`: (\d+).*?- `minor_issue`: (\d+).*?- `bad_label`: (\d+)", text, re.S)
    question_match = re.search(r"## Question Audit.*?- Total reviewed: (\d+).*?- `ok`: (\d+).*?- `minor_issue`: (\d+).*?- `bad_question`: (\d+)", text, re.S)
    if scenario_match is None or question_match is None:
        raise ValueError(f"Could not parse audit summary: {path}")
    return {
        "scenario_total": int(scenario_match.group(1)),
        "scenario_ok": int(scenario_match.group(2)),
        "scenario_minor_issue": int(scenario_match.group(3)),
        "scenario_bad_label": int(scenario_match.group(4)),
        "question_total": int(question_match.group(1)),
        "question_ok": int(question_match.group(2)),
        "question_minor_issue": int(question_match.group(3)),
        "question_bad_question": int(question_match.group(4)),
    }


def paired_delta(rows: list[dict], policy_a: str, policy_b: str, split: str = "test") -> float:
    filtered = [row for row in rows if row["split"] == split and row["policy"] in {policy_a, policy_b}]
    by_policy = {
        policy: {row["episode_id"]: float(row["reward"]) for row in filtered if row["policy"] == policy}
        for policy in {policy_a, policy_b}
    }
    shared = sorted(set(by_policy[policy_a]) & set(by_policy[policy_b]))
    return mean(by_policy[policy_a][episode_id] - by_policy[policy_b][episode_id] for episode_id in shared)


def ablation_rows(episodes: dict[str, dict], api_rows: list[dict]) -> list[dict]:
    ecu_rows = [row for row in api_rows if row["policy"] == "api_ecu"]
    replayed = []
    for ablation in ABLATIONS:
        for row in ecu_rows:
            replayed.append(replay_row(row, episodes[row["episode_id"]], ablation))
    return replayed


def heldout_slice_stats(episodes: dict[str, dict], offline_rows: list[dict], policy: str) -> dict:
    selected = []
    for row in offline_rows:
        if row["split"] != "ood_test" or row["policy"] != policy:
            continue
        if episode_has_heldout_object(episodes[row["episode_id"]]):
            selected.append(row)
    return aggregate(selected)


def margin_bin_stats(episodes: dict[str, dict], rows: list[dict], split: str, policy: str, bin_name: str) -> dict:
    selected = []
    for row in rows:
        if row["split"] != split or row["policy"] != policy:
            continue
        if margin_bin(float(episodes[row["episode_id"]]["features"]["eu_ask_minus_act"])) == bin_name:
            selected.append(row)
    return aggregate(selected)


def failure_events(rows: list[dict]) -> list[dict]:
    events = []
    for row in rows:
        failure_type = classify_failure(row)
        if failure_type is not None:
            event = dict(row)
            event["failure_type"] = failure_type
            events.append(event)
    return events


def question_usefulness_stats(rows: list[dict], split: str, policy: str) -> dict[str, float]:
    selected = [row for row in rows if row["split"] == split and row["policy"] == policy]
    asked = [row for row in selected if row["asked"]]
    oracle_ask = [row for row in selected if row["oracle_should_ask"]]
    needed_asks = [row for row in asked if row["oracle_should_ask"]]
    unnecessary_asks = [row for row in asked if not row["oracle_should_ask"]]
    successful_after_ask = [row for row in asked if row["success"]]
    return {
        "ask_precision": len(needed_asks) / len(asked) if asked else 0.0,
        "ask_recall": len(needed_asks) / len(oracle_ask) if oracle_ask else 0.0,
        "post_answer_success": len(successful_after_ask) / len(asked) if asked else 0.0,
        "unneeded_ask_share": len(unnecessary_asks) / len(asked) if asked else 0.0,
    }


def rate(rows: list[dict], predicate) -> float:
    return sum(1 for row in rows if predicate(row)) / len(rows) if rows else 0.0


def ask_act_change_rate(baseline_rows: list[dict], perturbed_rows: list[dict], policy: str) -> float:
    baseline = {row["episode_id"]: row for row in baseline_rows if row["policy"] == policy}
    pairs = [(baseline[row["episode_id"]], row) for row in perturbed_rows if row["policy"] == policy and row["episode_id"] in baseline]
    return sum(bool(base["asked"]) != bool(perturbed["asked"]) for base, perturbed in pairs) / len(pairs) if pairs else 0.0


def api_margin_positive(row: dict) -> bool:
    debug = row.get("debug", {})
    return float(debug.get("api_advantage", 0.0)) > float(debug.get("api_ecu_margin", API_ECU_ASK_MARGIN))


def api_context_override(row: dict) -> bool:
    return api_margin_positive(row) and bool(row.get("debug", {}).get("api_context_resolved_enough", False))


def main() -> None:
    args = parse_args()
    episodes_list = read_jsonl(args.episodes)
    episodes = {episode["episode_id"]: episode for episode in episodes_list}
    offline_rows = read_jsonl(args.offline_results)
    api_rows = read_jsonl(args.api_results)
    api_cot_rows = read_jsonl(args.api_cot_results)
    style_episodes = read_jsonl(args.style_episodes)
    api_style_rows = read_jsonl(args.api_style_results)
    api_second_model_rows = read_jsonl(args.api_second_model_results)
    api_gpt54_mini_rows = read_jsonl(args.api_gpt54_mini_results)
    api_gpt55_rows = read_jsonl(args.api_gpt55_results)
    api_gpt54_mini_shuffled_rows = read_jsonl(args.api_gpt54_mini_shuffled_results)
    api_gpt54_mini_natural_language_rows = read_jsonl(args.api_gpt54_mini_natural_language_results)
    ambiguity_mix_episodes = read_jsonl(args.ambiguity_mix_episodes)
    ambiguity_mix_rows = read_jsonl(args.ambiguity_mix_results)
    api_extended_rows = api_rows + api_cot_rows
    report_rows: list[list[str]] = []
    ok = True

    split_counts = Counter(episode["split"] for episode in episodes_list)
    category_counts = Counter(episode["ambiguity_type"] for episode in episodes_list)
    oracle_ask_count = sum(1 for episode in episodes_list if episode["oracle_should_ask"])
    ok &= check_equal(report_rows, "dataset total episodes", len(episodes_list), 1400, args.episodes)
    ok &= check_equal(report_rows, "dataset split counts", dict(sorted(split_counts.items())), {"dev": 200, "ood_test": 200, "test": 400, "train": 600}, args.episodes)
    ok &= check_equal(
        report_rows,
        "dataset category counts",
        dict(sorted(category_counts.items())),
        {
            "context_resolved": 280,
            "equivalent_outcome": 280,
            "preference_social": 280,
            "referential": 280,
            "risk_sensitive": 280,
        },
        args.episodes,
    )
    ok &= check_float(report_rows, "dataset oracle ask rate", oracle_ask_count / len(episodes_list), 0.500, args.episodes)
    category_oracle_expectations = {
        "context_resolved": 0.000,
        "equivalent_outcome": 0.000,
        "preference_social": 0.500,
        "referential": 1.000,
        "risk_sensitive": 1.000,
    }
    for category, expected in category_oracle_expectations.items():
        category_episodes = [episode for episode in episodes_list if episode["ambiguity_type"] == category]
        category_ask_rate = sum(1 for episode in category_episodes if episode["oracle_should_ask"]) / len(category_episodes)
        ok &= check_float(report_rows, f"dataset category {category} oracle ask rate", category_ask_rate, expected, args.episodes)

    style_split_counts = Counter(episode["split"] for episode in style_episodes)
    style_category_counts = Counter(episode["ambiguity_type"] for episode in style_episodes)
    style_oracle_ask_count = sum(1 for episode in style_episodes if episode["oracle_should_ask"])
    ok &= check_equal(report_rows, "style-stress total episodes", len(style_episodes), 50, args.style_episodes)
    ok &= check_equal(report_rows, "style-stress split counts", dict(sorted(style_split_counts.items())), {"style_test": 50}, args.style_episodes)
    ok &= check_equal(
        report_rows,
        "style-stress category counts",
        dict(sorted(style_category_counts.items())),
        {
            "context_resolved": 10,
            "equivalent_outcome": 10,
            "preference_social": 10,
            "referential": 10,
            "risk_sensitive": 10,
        },
        args.style_episodes,
    )
    ok &= check_float(report_rows, "style-stress oracle ask rate", style_oracle_ask_count / len(style_episodes), 0.460, args.style_episodes)

    offline = group_rows(offline_rows, ("split", "policy"))
    offline_expectations = [
        ("test", "direct_act", "net_utility", 0.498),
        ("test", "ask_always", "net_utility", 0.920),
        ("test", "prompted_heuristic", "net_utility", 0.938),
        ("test", "ecu", "net_utility", 0.958),
        ("test", "learned_controller", "net_utility", 0.958),
        ("ood_test", "prompted_heuristic", "net_utility", 0.955),
        ("ood_test", "ecu", "net_utility", 0.975),
        ("test", "ecu", "ask_rate", 0.500),
        ("ood_test", "ecu", "ask_rate", 0.500),
    ]
    for split, policy, metric, expected in offline_expectations:
        stats = aggregate(offline[(split, policy)])
        ok &= check_float(report_rows, f"offline {split} {policy} {metric}", stats[metric], expected, args.offline_results)

    test_episodes = [episode for episode in episodes_list if episode["split"] == "test"]
    surface_ambiguous_test = [episode for episode in test_episodes if len(episode["candidate_intents"]) > 1]
    oracle_ask_surface_test = [episode for episode in surface_ambiguous_test if episode["oracle_should_ask"]]
    oracle_act_surface_test = [episode for episode in surface_ambiguous_test if not episode["oracle_should_ask"]]
    ok &= check_equal(
        report_rows,
        "ambiguity diagnostic test surface-ambiguous episodes",
        len(surface_ambiguous_test),
        400,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ok &= check_equal(
        report_rows,
        "ambiguity diagnostic test oracle-ask among surface-ambiguous",
        len(oracle_ask_surface_test),
        200,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ok &= check_equal(
        report_rows,
        "ambiguity diagnostic test oracle-act among surface-ambiguous",
        len(oracle_act_surface_test),
        200,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ambiguity_raw_test = [row for row in ambiguity_raw_rows(episodes_list) if row["split"] == "test"]
    ambiguity_raw_stats = aggregate(ambiguity_raw_test)
    ok &= check_float(
        report_rows,
        "ambiguity diagnostic surface-ambiguity test net_utility",
        ambiguity_raw_stats["net_utility"],
        0.920,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ok &= check_float(
        report_rows,
        "ambiguity diagnostic surface-ambiguity test unnecessary_clarification_rate",
        ambiguity_raw_stats["unnecessary_clarification_rate"],
        1.000,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ambiguity_controller = UncertaintyOnlyController()
    ambiguity_controller.fit(
        [episode for episode in episodes_list if episode["split"] == "train"],
        [episode for episode in episodes_list if episode["split"] == "dev"],
    )
    ambiguity_controller_test = [
        row for row in ambiguity_controller_rows(episodes_list, ambiguity_controller) if row["split"] == "test"
    ]
    ambiguity_controller_stats = aggregate(ambiguity_controller_test)
    ok &= check_float(
        report_rows,
        "ambiguity diagnostic uncertainty-only test net_utility",
        ambiguity_controller_stats["net_utility"],
        0.900,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ok &= check_float(
        report_rows,
        "ambiguity diagnostic uncertainty-only test missed_clarification_rate",
        ambiguity_controller_stats["missed_clarification_rate"],
        0.070,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )
    ok &= check_float(
        report_rows,
        "ambiguity diagnostic uncertainty-only test unnecessary_clarification_rate",
        ambiguity_controller_stats["unnecessary_clarification_rate"],
        0.400,
        "paper/tables/ambiguity_utility_diagnostic.md",
    )

    situated_slices = situated_contrast_slices(test_episodes)
    situated_expectations = [
        ("bring / 2 candidates / context-resolved", "n", len(situated_slices["bring / 2 candidates / context-resolved"]), 80),
        (
            "bring / 2 candidates / context-resolved",
            "oracle ask rate",
            sum(1 for row in situated_slices["bring / 2 candidates / context-resolved"] if row["oracle_should_ask"])
            / len(situated_slices["bring / 2 candidates / context-resolved"]),
            0.000,
        ),
        ("bring / 2 candidates / referential", "n", len(situated_slices["bring / 2 candidates / referential"]), 80),
        (
            "bring / 2 candidates / referential",
            "oracle ask rate",
            sum(1 for row in situated_slices["bring / 2 candidates / referential"] if row["oracle_should_ask"])
            / len(situated_slices["bring / 2 candidates / referential"]),
            1.000,
        ),
        ("put-away preference / owner visible", "n", len(situated_slices["put-away preference / owner visible"]), 40),
        (
            "put-away preference / owner visible",
            "oracle ask rate",
            sum(1 for row in situated_slices["put-away preference / owner visible"] if row["oracle_should_ask"])
            / len(situated_slices["put-away preference / owner visible"]),
            0.000,
        ),
        ("put-away preference / owner hidden", "n", len(situated_slices["put-away preference / owner hidden"]), 40),
        (
            "put-away preference / owner hidden",
            "oracle ask rate",
            sum(1 for row in situated_slices["put-away preference / owner hidden"] if row["oracle_should_ask"])
            / len(situated_slices["put-away preference / owner hidden"]),
            1.000,
        ),
        (
            "high entropy / equivalent outcomes",
            "mean normalized entropy",
            mean(situated_normalized_entropy(row) for row in situated_slices["high entropy / equivalent outcomes"]),
            0.998,
        ),
        (
            "high entropy / equivalent outcomes",
            "oracle ask rate",
            sum(1 for row in situated_slices["high entropy / equivalent outcomes"] if row["oracle_should_ask"])
            / len(situated_slices["high entropy / equivalent outcomes"]),
            0.000,
        ),
        (
            "high top-prior / high wrong-action cost",
            "mean top prior",
            mean(float(row["features"]["top_prior"]) for row in situated_slices["high top-prior / high wrong-action cost"]),
            0.799,
        ),
        (
            "high top-prior / high wrong-action cost",
            "oracle ask rate",
            sum(1 for row in situated_slices["high top-prior / high wrong-action cost"] if row["oracle_should_ask"])
            / len(situated_slices["high top-prior / high wrong-action cost"]),
            1.000,
        ),
    ]
    for slice_name, metric, observed, expected in situated_expectations:
        if metric == "n":
            ok &= check_equal(
                report_rows,
                f"situated contrast {slice_name} {metric}",
                observed,
                expected,
                "paper/tables/situated_contrast_analysis.md",
            )
        else:
            ok &= check_float(
                report_rows,
                f"situated contrast {slice_name} {metric}",
                observed,
                expected,
                "paper/tables/situated_contrast_analysis.md",
            )

    api = group_rows(api_rows, ("split", "policy"))
    api_expectations = [
        ("api_direct_act", "net_utility", 0.420),
        ("api_direct_act", "success", 0.770),
        ("api_ask_needed", "net_utility", 0.632),
        ("api_ask_needed", "success", 0.880),
        ("api_ask_needed", "missed_clarification_rate", 0.583),
        ("api_ask_needed", "unnecessary_clarification_rate", 0.327),
        ("api_ecu", "net_utility", 0.976),
        ("api_ecu", "success", 1.000),
        ("api_ecu", "ask_rate", 0.480),
        ("api_ecu", "missed_clarification_rate", 0.000),
        ("api_ecu", "unnecessary_clarification_rate", 0.000),
    ]
    for policy, metric, expected in api_expectations:
        stats = aggregate(api[("test", policy)])
        ok &= check_float(report_rows, f"API {policy} {metric}", stats[metric], expected, args.api_results)

    api_cot = group_rows(api_cot_rows, ("split", "policy"))
    cot_expectations = [
        ("api_ask_needed_cot", "net_utility", 0.632),
        ("api_ask_needed_cot", "success", 0.890),
        ("api_ask_needed_cot", "ask_rate", 0.370),
        ("api_ask_needed_cot", "missed_clarification_rate", 0.604),
        ("api_ask_needed_cot", "unnecessary_clarification_rate", 0.346),
    ]
    for policy, metric, expected in cot_expectations:
        stats = aggregate(api_cot[("test", policy)])
        ok &= check_float(report_rows, f"API auxiliary {policy} {metric}", stats[metric], expected, args.api_cot_results)

    api_second_model = group_rows(api_second_model_rows, ("split", "policy"))
    second_model_expectations = [
        ("api_direct_act", "net_utility", 0.040),
        ("api_direct_act", "success", 0.640),
        ("api_ask_needed", "net_utility", 0.098),
        ("api_ask_needed", "success", 0.680),
        ("api_ask_needed", "missed_clarification_rate", 0.909),
        ("api_ecu", "net_utility", 0.722),
        ("api_ecu", "success", 0.880),
        ("api_ecu", "ask_rate", 0.560),
        ("api_ecu", "missed_clarification_rate", 0.182),
    ]
    for policy, metric, expected in second_model_expectations:
        stats = aggregate(api_second_model[("test", policy)])
        ok &= check_float(report_rows, f"API second-model {policy} {metric}", stats[metric], expected, args.api_second_model_results)
    ok &= check_float(
        report_rows,
        "paired second-model ECU - Ask-Needed utility delta",
        paired_delta(api_second_model_rows, "api_ecu", "api_ask_needed"),
        0.624,
        "paper/tables/api_second_model_25/paired_differences.md",
    )
    ok &= check_float(
        report_rows,
        "paired second-model ECU - DirectAct utility delta",
        paired_delta(api_second_model_rows, "api_ecu", "api_direct_act"),
        0.682,
        "paper/tables/api_second_model_25/paired_differences.md",
    )

    current_model_expectations = [
        (
            "gpt-5.4-mini",
            api_gpt54_mini_rows,
            args.api_gpt54_mini_results,
            [
                ("api_direct_act", "net_utility", 0.380),
                ("api_direct_act", "success", 0.750),
                ("api_ask_needed", "net_utility", 0.868),
                ("api_ask_needed", "success", 0.970),
                ("api_ask_needed", "missed_clarification_rate", 0.125),
                ("api_ask_needed", "unnecessary_clarification_rate", 0.519),
                ("api_ask_needed_cot", "net_utility", 0.864),
                ("api_ecu", "net_utility", 0.976),
                ("api_ecu", "success", 1.000),
                ("api_ecu", "ask_rate", 0.480),
                ("api_ecu", "missed_clarification_rate", 0.000),
                ("api_ecu", "unnecessary_clarification_rate", 0.000),
            ],
            [("api_ecu", "api_ask_needed", 0.107), ("api_ecu", "api_ask_needed_cot", 0.112)],
        ),
        (
            "gpt-5.5",
            api_gpt55_rows,
            args.api_gpt55_results,
            [
                ("api_direct_act", "net_utility", 0.240),
                ("api_direct_act", "success", 0.720),
                ("api_ask_needed", "net_utility", 0.821),
                ("api_ask_needed", "success", 0.960),
                ("api_ask_needed", "missed_clarification_rate", 0.271),
                ("api_ask_needed", "unnecessary_clarification_rate", 0.038),
                ("api_ask_needed_cot", "net_utility", 0.976),
                ("api_ecu", "net_utility", 0.976),
                ("api_ecu", "success", 1.000),
                ("api_ecu", "ask_rate", 0.480),
                ("api_ecu", "missed_clarification_rate", 0.000),
                ("api_ecu", "unnecessary_clarification_rate", 0.000),
            ],
            [("api_ecu", "api_ask_needed", 0.155), ("api_ecu", "api_ask_needed_cot", 0.000)],
        ),
    ]
    for model, rows, evidence, expectations, deltas in current_model_expectations:
        grouped = group_rows(rows, ("split", "policy"))
        for policy, metric, expected in expectations:
            stats = aggregate(grouped[("test", policy)])
            ok &= check_float(report_rows, f"current-model {model} {policy} {metric}", stats[metric], expected, evidence)
        for policy_a, policy_b, expected in deltas:
            ok &= check_float(
                report_rows,
                f"paired current-model {model} {policy_a} - {policy_b} utility delta",
                paired_delta(rows, policy_a, policy_b),
                expected,
                "paper/tables/current_model_sweep.md",
            )

    scene_format = group_rows(api_gpt54_mini_shuffled_rows, ("split", "policy"))
    scene_format_expectations = [
        ("api_direct_act", "net_utility", 0.420),
        ("api_ask_needed", "net_utility", 0.908),
        ("api_ask_needed", "missed_clarification_rate", 0.042),
        ("api_ask_needed", "unnecessary_clarification_rate", 0.481),
        ("api_ask_needed_cot", "net_utility", 0.926),
        ("api_ecu", "net_utility", 0.976),
        ("api_ecu", "success", 1.000),
        ("api_ecu", "ask_rate", 0.480),
        ("api_ecu", "missed_clarification_rate", 0.000),
        ("api_ecu", "unnecessary_clarification_rate", 0.000),
    ]
    for policy, metric, expected in scene_format_expectations:
        stats = aggregate(scene_format[("test", policy)])
        ok &= check_float(
            report_rows,
            f"scene-format shuffled gpt-5.4-mini {policy} {metric}",
            stats[metric],
            expected,
            args.api_gpt54_mini_shuffled_results,
        )
    ok &= check_float(
        report_rows,
        "scene-format shuffled gpt-5.4-mini paired ECU - Ask-Needed utility delta",
        paired_delta(api_gpt54_mini_shuffled_rows, "api_ecu", "api_ask_needed"),
        0.068,
        "paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md",
    )
    ok &= check_float(
        report_rows,
        "scene-format shuffled gpt-5.4-mini paired ECU - CoT Ask-Needed utility delta",
        paired_delta(api_gpt54_mini_shuffled_rows, "api_ecu", "api_ask_needed_cot"),
        0.049,
        "paper/tables/api_gpt_5_4_mini_shuffled_test100/paired_differences.md",
    )
    ok &= check_float(
        report_rows,
        "scene-format shuffled gpt-5.4-mini ECU ask-act change rate",
        ask_act_change_rate(api_gpt54_mini_rows, api_gpt54_mini_shuffled_rows, "api_ecu"),
        0.000,
        "paper/tables/api_gpt_5_4_mini_scene_format_robustness.md",
    )

    natural_scene_format = group_rows(api_gpt54_mini_natural_language_rows, ("split", "policy"))
    natural_scene_format_expectations = [
        ("api_direct_act", "net_utility", 0.420),
        ("api_ask_needed", "net_utility", 0.788),
        ("api_ask_needed", "missed_clarification_rate", 0.167),
        ("api_ask_needed", "unnecessary_clarification_rate", 0.519),
        ("api_ask_needed_cot", "net_utility", 0.904),
        ("api_ecu", "net_utility", 0.975),
        ("api_ecu", "success", 1.000),
        ("api_ecu", "ask_rate", 0.490),
        ("api_ecu", "missed_clarification_rate", 0.000),
        ("api_ecu", "unnecessary_clarification_rate", 0.019),
    ]
    for policy, metric, expected in natural_scene_format_expectations:
        stats = aggregate(natural_scene_format[("test", policy)])
        ok &= check_float(
            report_rows,
            f"scene-format natural-language gpt-5.4-mini {policy} {metric}",
            stats[metric],
            expected,
            args.api_gpt54_mini_natural_language_results,
        )
    ok &= check_float(
        report_rows,
        "scene-format natural-language gpt-5.4-mini paired ECU - Ask-Needed utility delta",
        paired_delta(api_gpt54_mini_natural_language_rows, "api_ecu", "api_ask_needed"),
        0.186,
        "paper/tables/api_gpt_5_4_mini_natural_language_test100/paired_differences.md",
    )
    ok &= check_float(
        report_rows,
        "scene-format natural-language gpt-5.4-mini paired ECU - CoT Ask-Needed utility delta",
        paired_delta(api_gpt54_mini_natural_language_rows, "api_ecu", "api_ask_needed_cot"),
        0.070,
        "paper/tables/api_gpt_5_4_mini_natural_language_test100/paired_differences.md",
    )
    ok &= check_float(
        report_rows,
        "scene-format natural-language gpt-5.4-mini ECU ask-act change rate",
        ask_act_change_rate(api_gpt54_mini_rows, api_gpt54_mini_natural_language_rows, "api_ecu"),
        0.010,
        "paper/tables/api_gpt_5_4_mini_natural_language_scene_format_robustness.md",
    )

    question_expectations = [
        (api_rows, "test", "api_ask_needed", "ask_precision", 0.541, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_rows, "test", "api_ask_needed", "ask_recall", 0.417, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_rows, "test", "api_ask_needed", "post_answer_success", 1.000, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_cot_rows, "test", "api_ask_needed_cot", "ask_precision", 0.514, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_cot_rows, "test", "api_ask_needed_cot", "ask_recall", 0.396, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_rows, "test", "api_ecu", "ask_precision", 1.000, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_rows, "test", "api_ecu", "ask_recall", 1.000, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_rows, "test", "api_ecu", "post_answer_success", 1.000, "paper/tables/api_eval_100_extended/question_usefulness.md"),
        (api_rows, "test", "api_ecu", "unneeded_ask_share", 0.000, "paper/tables/api_eval_100_extended/question_usefulness.md"),
    ]
    for rows, split, policy, metric, expected, evidence in question_expectations:
        stats = question_usefulness_stats(rows, split, policy)
        ok &= check_float(report_rows, f"API question usefulness {split} {policy} {metric}", stats[metric], expected, evidence)

    api_ecu_rows = [row for row in api_rows if row["policy"] == "api_ecu"]
    ok &= check_float(
        report_rows,
        "API ECU candidate-margin positive rate",
        rate(api_ecu_rows, api_margin_positive),
        0.490,
        "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate-margin/oracle agreement",
        rate(api_ecu_rows, lambda row: api_margin_positive(row) == bool(row["oracle_should_ask"])),
        0.990,
        "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU effective context override rate",
        rate(api_ecu_rows, api_context_override),
        0.010,
        "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU final ask/oracle agreement",
        rate(api_ecu_rows, lambda row: bool(row["asked"]) == bool(row["oracle_should_ask"])),
        1.000,
        "paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md",
    )

    candidate_calibration_records = candidate_row_records("gpt-4.1-mini", api_rows, episodes)
    candidate_gpt55_records = candidate_row_records("gpt-5.5", api_gpt55_rows, episodes)
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration top benchmark match",
        mean(1.0 if record["top_matches_benchmark"] else 0.0 for record in candidate_calibration_records),
        0.970,
        "paper/tables/api_candidate_calibration.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration top hidden match",
        mean(1.0 if record["top_matches_hidden"] else 0.0 for record in candidate_calibration_records),
        0.770,
        "paper/tables/api_candidate_calibration.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration prior TV",
        mean(float(record["prior_tv"]) for record in candidate_calibration_records),
        0.057,
        "paper/tables/api_candidate_calibration.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration gpt-4.1-mini margin Pearson",
        candidate_pearson(
            [float(record["model_margin"]) for record in candidate_calibration_records],
            [float(record["oracle_margin"]) for record in candidate_calibration_records],
        ),
        0.948,
        "paper/tables/api_candidate_calibration.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration gpt-4.1-mini margin Spearman",
        candidate_spearman(
            [float(record["model_margin"]) for record in candidate_calibration_records],
            [float(record["oracle_margin"]) for record in candidate_calibration_records],
        ),
        0.741,
        "paper/tables/api_candidate_calibration.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration gpt-5.5 margin Pearson",
        candidate_pearson(
            [float(record["model_margin"]) for record in candidate_gpt55_records],
            [float(record["oracle_margin"]) for record in candidate_gpt55_records],
        ),
        0.991,
        "paper/tables/api_candidate_calibration.md",
    )
    ok &= check_float(
        report_rows,
        "API ECU candidate calibration gpt-5.5 margin Spearman",
        candidate_spearman(
            [float(record["model_margin"]) for record in candidate_gpt55_records],
            [float(record["oracle_margin"]) for record in candidate_gpt55_records],
        ),
        0.954,
        "paper/tables/api_candidate_calibration.md",
    )

    cache_replay_checks = api_cache_replay_checks()
    ok &= check_equal(
        report_rows,
        "API cache-only replay checks",
        {
            check["config"].name: {
                "canonical_rows": check["canonical_rows"],
                "replay_rows": check["replay_rows"],
                "mismatches": len(check["mismatches"]),
            }
            for check in cache_replay_checks
        },
        {
            "main_100_gpt41mini": {"canonical_rows": 300, "replay_rows": 300, "mismatches": 0},
            "cot_100_gpt41mini": {"canonical_rows": 100, "replay_rows": 100, "mismatches": 0},
            "style_50_gpt41mini": {"canonical_rows": 150, "replay_rows": 150, "mismatches": 0},
            "second_model_25_gpt41nano": {"canonical_rows": 75, "replay_rows": 75, "mismatches": 0},
            "current_100_gpt54mini": {"canonical_rows": 400, "replay_rows": 400, "mismatches": 0},
            "current_100_gpt55": {"canonical_rows": 400, "replay_rows": 400, "mismatches": 0},
            "shuffled_scene_100_gpt54mini": {"canonical_rows": 400, "replay_rows": 400, "mismatches": 0},
            "natural_language_scene_100_gpt54mini": {"canonical_rows": 400, "replay_rows": 400, "mismatches": 0},
        },
        "paper/tables/api_cache_replay_verification.md",
    )

    sim_user_episodes = sim_user_read_jsonl_paths(SIM_USER_EPISODES)
    sim_user_api_rows = sim_user_read_jsonl_paths(SIM_USER_API_RESULTS)
    sim_user_generated_rows, sim_user_generated_failures = sim_user_generated_audit_rows(sim_user_episodes)
    sim_user_api_table_rows, sim_user_api_failures = sim_user_api_audit_rows(
        sim_user_api_rows,
        {episode["episode_id"]: episode for episode in sim_user_episodes},
    )
    ok &= check_equal(
        report_rows,
        "simulated user visible-answer audit",
        {
            "generated_oracle_ask_answers": sum(int(row[2]) for row in sim_user_generated_rows),
            "generated_failures": len(sim_user_generated_failures),
            "api_asked_answers": sum(int(row[2]) for row in sim_user_api_table_rows),
            "api_failures": len(sim_user_api_failures),
        },
        {
            "generated_oracle_ask_answers": 1233,
            "generated_failures": 0,
            "api_asked_answers": 184,
            "api_failures": 0,
        },
        "paper/tables/simulated_user_audit.md",
    )

    api_subset_all_ids = sorted({row["episode_id"] for row in api_rows})
    api_subset_category_by_episode = {row["episode_id"]: row["ambiguity_type"] for row in api_rows}
    api_subset_leave_category_deltas = []
    for omitted in API_SUBSET_CATEGORY_ORDER:
        kept_ids = [episode_id for episode_id in api_subset_all_ids if api_subset_category_by_episode[episode_id] != omitted]
        api_subset_leave_category_deltas.append(api_subset_mean_delta(api_rows, "api_ecu", "api_ask_needed", kept_ids))
    api_subset_leave_episode_deltas = []
    for omitted in api_subset_all_ids:
        kept_ids = [episode_id for episode_id in api_subset_all_ids if episode_id != omitted]
        api_subset_leave_episode_deltas.append(api_subset_mean_delta(api_rows, "api_ecu", "api_ask_needed", kept_ids))
    api_subset_stratified_lo, _ = api_subset_stratified_bootstrap_ci(api_rows, "api_ecu", "api_ask_needed", samples=2000, seed=0)
    ok &= check_float(
        report_rows,
        "API subset stability minimum leave-one-category ECU - Ask-Needed delta",
        min(api_subset_leave_category_deltas),
        0.190,
        "paper/tables/api_eval_100_corrected/subset_stability.md",
    )
    ok &= check_float(
        report_rows,
        "API subset stability minimum leave-one-episode ECU - Ask-Needed delta",
        min(api_subset_leave_episode_deltas),
        0.307,
        "paper/tables/api_eval_100_corrected/subset_stability.md",
    )
    ok &= check_float(
        report_rows,
        "API subset stability stratified bootstrap lower bound ECU - Ask-Needed",
        api_subset_stratified_lo,
        0.183,
        "paper/tables/api_eval_100_corrected/subset_stability.md",
    )

    ok &= check_float(report_rows, "paired API ECU - Ask-Needed utility delta", paired_delta(api_rows, "api_ecu", "api_ask_needed"), 0.343, args.api_results)
    ok &= check_float(report_rows, "paired API ECU - DirectAct utility delta", paired_delta(api_rows, "api_ecu", "api_direct_act"), 0.556, args.api_results)
    ok &= check_float(report_rows, "paired API ECU - CoT Ask-Needed utility delta", paired_delta(api_extended_rows, "api_ecu", "api_ask_needed_cot"), 0.344, args.api_cot_results)
    ok &= check_float(report_rows, "paired CoT Ask-Needed - plain Ask-Needed utility delta", paired_delta(api_extended_rows, "api_ask_needed_cot", "api_ask_needed"), -0.001, args.api_cot_results)
    ok &= check_float(report_rows, "paired offline ECU - prompted utility delta", paired_delta(offline_rows, "ecu", "prompted_heuristic"), 0.020, args.offline_results)

    api_cost_settings = [(ask_cost, 1.0) for ask_cost in [0.01, 0.05, 0.10, 0.20, 0.35]]
    api_cost_settings.extend((0.05, wrong_cost) for wrong_cost in [0.2, 0.5, 1.0, 2.0, 3.0])
    api_cost_deltas = []
    api_cost_ci_lowers = []
    for ask_cost, wrong_action_cost in api_cost_settings:
        adjusted = api_cost_adjusted_rows(api_rows, episodes, ask_cost, wrong_action_cost)
        api_cost_deltas.append(api_cost_paired_delta(adjusted, "api_ecu", "api_ask_needed"))
        _, ci_low, _ = api_cost_paired_delta_ci(adjusted, "api_ecu", "api_ask_needed", samples=2000, seed=0)
        api_cost_ci_lowers.append(ci_low)
    ok &= check_float(
        report_rows,
        "cached API utility sensitivity minimum ECU - Ask-Needed delta",
        min(api_cost_deltas),
        0.138,
        "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
    )
    ok &= check_float(
        report_rows,
        "cached API utility sensitivity maximum ECU - Ask-Needed delta",
        max(api_cost_deltas),
        0.475,
        "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
    )
    ok &= check_float(
        report_rows,
        "cached API utility sensitivity minimum ECU - Ask-Needed paired CI lower",
        min(api_cost_ci_lowers),
        0.070,
        "paper/tables/api_eval_100_corrected/utility_sensitivity.md",
    )

    calibration_expectations = [
        (episodes, api_rows, "test", "api_ecu", "act_preferred", "ask_rate", 0.000, args.api_results),
        (episodes, api_rows, "test", "api_ecu", "ask_preferred", "ask_rate", 1.000, args.api_results),
        (episodes, api_rows, "test", "api_ask_needed", "act_preferred", "ask_rate", 0.425, args.api_results),
        (episodes, api_rows, "test", "api_ask_needed", "ask_preferred", "ask_rate", 0.417, args.api_results),
        (episodes, api_rows, "test", "api_ecu", "ask_preferred", "net_utility", 0.950, args.api_results),
    ]
    for episode_map, rows, split, policy, bin_name, metric, expected, evidence in calibration_expectations:
        stats = margin_bin_stats(episode_map, rows, split, policy, bin_name)
        ok &= check_float(report_rows, f"API calibration {split} {policy} {bin_name} {metric}", stats[metric], expected, evidence)

    category_api = group_rows(api_rows, ("split", "ambiguity_type", "policy"))
    category_expectations = [
        ("context_resolved", "api_ecu", "net_utility", 1.000),
        ("equivalent_outcome", "api_ecu", "ask_rate", 0.000),
        ("referential", "api_ecu", "ask_rate", 1.000),
        ("risk_sensitive", "api_ecu", "ask_rate", 1.000),
        ("preference_social", "api_ecu", "ask_rate", 0.400),
        ("risk_sensitive", "api_ask_needed", "net_utility", -0.008),
    ]
    for category, policy, metric, expected in category_expectations:
        stats = aggregate(category_api[("test", category, policy)])
        ok &= check_float(report_rows, f"API category {category} {policy} {metric}", stats[metric], expected, args.api_results)

    category_cot = group_rows(api_cot_rows, ("split", "ambiguity_type", "policy"))
    cot_category_expectations = [
        ("equivalent_outcome", "api_ask_needed_cot", "ask_rate", 0.850),
        ("risk_sensitive", "api_ask_needed_cot", "net_utility", -0.200),
        ("preference_social", "api_ask_needed_cot", "net_utility", 0.598),
    ]
    for category, policy, metric, expected in cot_category_expectations:
        stats = aggregate(category_cot[("test", category, policy)])
        ok &= check_float(report_rows, f"API auxiliary category {category} {policy} {metric}", stats[metric], expected, args.api_cot_results)

    api_failure_events = failure_events(api_extended_rows)
    failure_counts = Counter(row["failure_type"] for row in api_failure_events)
    failure_policy_counts = Counter(row["policy"] for row in api_failure_events)
    api_failure_expectations = [
        ("api failure events direct_act", failure_policy_counts["api_direct_act"], 48, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
        ("api failure events ask_needed", failure_policy_counts["api_ask_needed"], 45, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
        ("api failure events ask_needed_cot", failure_policy_counts["api_ask_needed_cot"], 47, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
        ("api failure events ecu", failure_policy_counts["api_ecu"], 0, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
        ("api failure taxonomy risk blindness", failure_counts["risk_blindness"], 57, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
        ("api failure taxonomy equivalence blindness", failure_counts["equivalence_blindness"], 33, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
        ("api failure taxonomy referential guessing", failure_counts["guessing_under_referential_ambiguity"], 25, "paper/tables/api_eval_100_extended/failure_taxonomy.md"),
    ]
    for claim, observed, expected, evidence in api_failure_expectations:
        ok &= check_equal(report_rows, claim, observed, expected, evidence)

    api_style = group_rows(api_style_rows, ("split", "policy"))
    style_expectations = [
        ("api_direct_act", "net_utility", 0.320),
        ("api_direct_act", "success", 0.760),
        ("api_ask_needed", "net_utility", 0.814),
        ("api_ask_needed", "success", 0.920),
        ("api_ask_needed", "missed_clarification_rate", 0.478),
        ("api_ask_needed", "unnecessary_clarification_rate", 0.259),
        ("api_ecu", "net_utility", 0.977),
        ("api_ecu", "success", 1.000),
        ("api_ecu", "ask_rate", 0.460),
        ("api_ecu", "missed_clarification_rate", 0.000),
        ("api_ecu", "unnecessary_clarification_rate", 0.000),
    ]
    for policy, metric, expected in style_expectations:
        stats = aggregate(api_style[("style_test", policy)])
        ok &= check_float(report_rows, f"API style-stress {policy} {metric}", stats[metric], expected, args.api_style_results)
    style_question_expectations = [
        ("api_ask_needed", "ask_precision", 0.632),
        ("api_ask_needed", "ask_recall", 0.522),
        ("api_ask_needed", "post_answer_success", 1.000),
        ("api_ecu", "ask_precision", 1.000),
        ("api_ecu", "ask_recall", 1.000),
        ("api_ecu", "post_answer_success", 1.000),
        ("api_ecu", "unneeded_ask_share", 0.000),
    ]
    for policy, metric, expected in style_question_expectations:
        stats = question_usefulness_stats(api_style_rows, "style_test", policy)
        ok &= check_float(report_rows, f"API style-stress question usefulness {policy} {metric}", stats[metric], expected, "paper/tables/api_style_stress_50/question_usefulness.md")
    ok &= check_float(
        report_rows,
        "paired style-stress ECU - Ask-Needed utility delta",
        paired_delta(api_style_rows, "api_ecu", "api_ask_needed", split="style_test"),
        0.163,
        args.api_style_results,
    )
    ok &= check_float(
        report_rows,
        "paired style-stress ECU - DirectAct utility delta",
        paired_delta(api_style_rows, "api_ecu", "api_direct_act", split="style_test"),
        0.657,
        args.api_style_results,
    )
    style_category_api = group_rows(api_style_rows, ("split", "ambiguity_type", "policy"))
    style_category_expectations = [
        ("equivalent_outcome", "api_ask_needed", "ask_rate", 0.700),
        ("referential", "api_ecu", "ask_rate", 1.000),
        ("risk_sensitive", "api_ecu", "ask_rate", 1.000),
        ("preference_social", "api_ecu", "net_utility", 0.985),
    ]
    for category, policy, metric, expected in style_category_expectations:
        stats = aggregate(style_category_api[("style_test", category, policy)])
        ok &= check_float(report_rows, f"API style-stress category {category} {policy} {metric}", stats[metric], expected, args.api_style_results)
    style_episode_map = {episode["episode_id"]: episode for episode in style_episodes}
    style_calibration_expectations = [
        (style_episode_map, api_style_rows, "style_test", "api_ecu", "act_preferred", "ask_rate", 0.000),
        (style_episode_map, api_style_rows, "style_test", "api_ecu", "ask_preferred", "ask_rate", 1.000),
        (style_episode_map, api_style_rows, "style_test", "api_ask_needed", "act_preferred", "ask_rate", 0.350),
        (style_episode_map, api_style_rows, "style_test", "api_ask_needed", "ask_preferred", "ask_rate", 0.522),
        (style_episode_map, api_style_rows, "style_test", "api_ecu", "ask_preferred", "net_utility", 0.950),
    ]
    for episode_map, rows, split, policy, bin_name, metric, expected in style_calibration_expectations:
        stats = margin_bin_stats(episode_map, rows, split, policy, bin_name)
        ok &= check_float(report_rows, f"API style-stress calibration {policy} {bin_name} {metric}", stats[metric], expected, args.api_style_results)
    style_failure_events = failure_events(api_style_rows)
    style_failure_counts = Counter(row["failure_type"] for row in style_failure_events)
    style_failure_policy_counts = Counter(row["policy"] for row in style_failure_events)
    style_failure_expectations = [
        ("style-stress failure events direct_act", style_failure_policy_counts["api_direct_act"], 23, "paper/tables/api_style_stress_50/failure_taxonomy.md"),
        ("style-stress failure events ask_needed", style_failure_policy_counts["api_ask_needed"], 18, "paper/tables/api_style_stress_50/failure_taxonomy.md"),
        ("style-stress failure events ecu", style_failure_policy_counts["api_ecu"], 0, "paper/tables/api_style_stress_50/failure_taxonomy.md"),
        ("style-stress failure taxonomy referential guessing", style_failure_counts["guessing_under_referential_ambiguity"], 18, "paper/tables/api_style_stress_50/failure_taxonomy.md"),
        ("style-stress failure taxonomy risk blindness", style_failure_counts["risk_blindness"], 10, "paper/tables/api_style_stress_50/failure_taxonomy.md"),
        ("style-stress failure taxonomy equivalence blindness", style_failure_counts["equivalence_blindness"], 7, "paper/tables/api_style_stress_50/failure_taxonomy.md"),
    ]
    for claim, observed, expected, evidence in style_failure_expectations:
        ok &= check_equal(report_rows, claim, observed, expected, evidence)

    replayed = ablation_rows(episodes, api_rows)
    actual_ecu = {row["episode_id"]: row for row in api_rows if row["policy"] == "api_ecu"}
    current_replay = [row for row in replayed if row["policy"] == "current_rule_replay"]
    ok &= check_equal(
        report_rows,
        "ablation current-rule ask decision matches actual API ECU",
        sum(1 for row in current_replay if row["asked"] == actual_ecu[row["episode_id"]]["asked"]),
        100,
        "paper/tables/api_eval_100_corrected/ecu_ablation.md",
    )
    ablation = group_rows(replayed, ("policy",))
    ablation_expectations = [
        ("current_rule_replay", "net_utility", 0.976),
        ("accept_model_equivalence", "net_utility", 0.745),
        ("accept_model_equivalence", "missed_clarification_rate", 0.375),
        ("never_collapse_equivalence", "unnecessary_clarification_rate", 0.385),
        ("no_margin_or_context", "unnecessary_clarification_rate", 0.250),
    ]
    for policy, metric, expected in ablation_expectations:
        stats = aggregate(ablation[(policy,)])
        ok &= check_float(report_rows, f"API ECU ablation {policy} {metric}", stats[metric], expected, "paper/tables/api_eval_100_corrected/ecu_ablation.md")

    heldout_count = sum(1 for episode in episodes_list if episode["split"] == "ood_test" and episode_has_heldout_object(episode))
    heldout_types = sorted(
        {
            obj["type"]
            for episode in episodes_list
            if episode["split"] == "ood_test"
            for obj in episode["scene"]["objects"]
            if obj["type"] in HELDOUT_TYPES
        }
    )
    ok &= check_equal(report_rows, "OOD episodes with held-out object type", heldout_count, 102, "paper/tables/robustness_breakdown.md")
    ok &= check_equal(report_rows, "OOD held-out object types", heldout_types, ["charger", "keys", "notebook", "remote", "water_bottle"], "paper/tables/robustness_breakdown.md")
    for policy in ["ecu", "learned_controller"]:
        stats = heldout_slice_stats(episodes, offline_rows, policy)
        ok &= check_float(report_rows, f"OOD held-out slice {policy} net utility", stats["net_utility"], 0.975, "paper/tables/robustness_breakdown.md")
        ok &= check_float(report_rows, f"OOD held-out slice {policy} success", stats["success"], 1.000, "paper/tables/robustness_breakdown.md")

    ambiguity_mix_split_counts = Counter(episode["split"] for episode in ambiguity_mix_episodes)
    ambiguity_mix_category_by_split = Counter((episode["split"], episode["ambiguity_type"]) for episode in ambiguity_mix_episodes)
    ok &= check_equal(
        report_rows,
        "ambiguity-mix shift split counts",
        dict(sorted(ambiguity_mix_split_counts.items())),
        {"dev": 180, "ood_ambiguity_mix": 200, "test": 300, "train": 600},
        args.ambiguity_mix_episodes,
    )
    ok &= check_equal(
        report_rows,
        "ambiguity-mix train categories",
        sorted(category for split, category in ambiguity_mix_category_by_split if split == "train"),
        ["context_resolved", "equivalent_outcome", "referential"],
        args.ambiguity_mix_episodes,
    )
    ok &= check_equal(
        report_rows,
        "ambiguity-mix held-out categories",
        sorted(category for split, category in ambiguity_mix_category_by_split if split == "ood_ambiguity_mix"),
        ["preference_social", "risk_sensitive"],
        args.ambiguity_mix_episodes,
    )
    ambiguity_mix = group_rows(ambiguity_mix_rows, ("split", "policy"))
    ambiguity_mix_expectations = [
        ("test", "ecu", "net_utility", 0.963),
        ("ood_ambiguity_mix", "ecu", "net_utility", 0.962),
        ("ood_ambiguity_mix", "ecu", "ask_rate", 0.750),
        ("ood_ambiguity_mix", "learned_controller", "net_utility", 0.950),
        ("ood_ambiguity_mix", "learned_controller", "ask_rate", 1.000),
    ]
    for split, policy, metric, expected in ambiguity_mix_expectations:
        stats = aggregate(ambiguity_mix[(split, policy)])
        ok &= check_float(report_rows, f"ambiguity-mix {split} {policy} {metric}", stats[metric], expected, "paper/tables/ambiguity_mix_shift.md")

    audit_counts = audit_summary_counts("paper/audits/AUDIT_SUMMARY.md")
    audit_expectations = [
        ("audit scenario total reviewed", audit_counts["scenario_total"], 100),
        ("audit scenario ok", audit_counts["scenario_ok"], 100),
        ("audit scenario bad_label", audit_counts["scenario_bad_label"], 0),
        ("audit question total reviewed", audit_counts["question_total"], 100),
        ("audit question ok", audit_counts["question_ok"], 73),
        ("audit question minor_issue", audit_counts["question_minor_issue"], 19),
        ("audit question bad_question", audit_counts["question_bad_question"], 8),
    ]
    for claim, observed, expected in audit_expectations:
        ok &= check_equal(report_rows, claim, observed, expected, "paper/audits/AUDIT_SUMMARY.md")

    paper_consistency_failures = [
        result for result in paper_consistency_run_checks() if not result.ok and result.name != "submission readiness status"
    ]
    ok &= check_equal(
        report_rows,
        "paper consistency audit failures",
        len(paper_consistency_failures),
        0,
        PAPER_CONSISTENCY_OUT,
    )

    totals = cache_totals(args.api_cache)
    ok &= check_equal(report_rows, "API cache response count", totals["responses"], 914, args.api_cache)
    ok &= check_equal(report_rows, "API cache input tokens", totals["input_tokens"], 271208, args.api_cache)
    ok &= check_equal(report_rows, "API cache output tokens", totals["output_tokens"], 49117, args.api_cache)
    ok &= check_equal(report_rows, "API cache total tokens", totals["total_tokens"], 320325, args.api_cache)
    second_model_totals = cache_totals(args.api_second_model_cache)
    ok &= check_equal(report_rows, "API second-model cache response count", second_model_totals["responses"], 109, args.api_second_model_cache)
    ok &= check_equal(report_rows, "API second-model cache input tokens", second_model_totals["input_tokens"], 32996, args.api_second_model_cache)
    ok &= check_equal(report_rows, "API second-model cache output tokens", second_model_totals["output_tokens"], 6599, args.api_second_model_cache)
    ok &= check_equal(report_rows, "API second-model cache total tokens", second_model_totals["total_tokens"], 39595, args.api_second_model_cache)

    status = "PASS" if ok else "FAIL"
    text = "\n".join(
        [
            "# Claim Verification Report",
            "",
            f"Overall status: **{status}**",
            "",
            "This report recomputes headline claims from the canonical JSONL artifacts and generated analysis outputs.",
            "",
            markdown_table(["Claim", "Expected", "Observed", "Status", "Evidence"], report_rows),
        ]
    )
    write_text(args.out, text)
    print(f"wrote claim verification report to {args.out}")
    print(f"overall status: {status}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
