from __future__ import annotations

import argparse
import math
from collections import defaultdict
from statistics import mean

from clarify_to_act.generator import eu_advantage
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


UNKNOWN_CLASS = "__unknown__"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Run label and result path formatted as label=path.",
    )
    parser.add_argument("--out", default="paper/tables/api_candidate_calibration.md")
    return parser.parse_args()


def parse_run_spec(spec: str) -> tuple[str, str]:
    label, sep, path = spec.partition("=")
    if not sep or not label.strip() or not path.strip():
        raise ValueError(f"Invalid --run {spec!r}; expected label=path.")
    return label.strip(), path.strip()


def success_class_priors(episode: dict) -> dict[str, float]:
    priors: dict[str, float] = defaultdict(float)
    for intent in episode["candidate_intents"]:
        priors[str(intent["success_equivalence_class"])] += float(intent["prior"])
    return dict(priors)


def target_to_success_class(episode: dict) -> dict[str, str]:
    return {
        str(intent["target_id"]): str(intent["success_equivalence_class"])
        for intent in episode["candidate_intents"]
    }


def hidden_success_class(episode: dict) -> str:
    intents = {intent["intent_id"]: intent for intent in episode["candidate_intents"]}
    return str(intents[episode["hidden_intent_id"]]["success_equivalence_class"])


def normalize_masses(masses: dict[str, float]) -> dict[str, float]:
    cleaned = {key: max(0.0, float(value)) for key, value in masses.items()}
    total = sum(cleaned.values())
    if total <= 0:
        return cleaned
    return {key: value / total for key, value in cleaned.items()}


def model_success_class_masses(row: dict, episode: dict) -> dict[str, float]:
    target_classes = target_to_success_class(episode)
    masses: dict[str, float] = defaultdict(float)
    for candidate in (row.get("debug") or {}).get("api_candidates", []):
        target_id = str(candidate.get("target_id", ""))
        success_class = target_classes.get(target_id, UNKNOWN_CLASS)
        masses[success_class] += float(candidate.get("prior", 0.0) or 0.0)
    return normalize_masses(masses)


def top_key(masses: dict[str, float]) -> str | None:
    if not masses:
        return None
    return max(masses, key=masses.get)


def brier_score(masses: dict[str, float], hidden_class: str, benchmark_classes: set[str]) -> float:
    keys = set(masses) | set(benchmark_classes) | {UNKNOWN_CLASS}
    return sum((float(masses.get(key, 0.0)) - (1.0 if key == hidden_class else 0.0)) ** 2 for key in keys)


def total_variation_distance(model_masses: dict[str, float], benchmark_priors: dict[str, float]) -> float:
    keys = set(model_masses) | set(benchmark_priors) | {UNKNOWN_CLASS}
    return 0.5 * sum(abs(float(model_masses.get(key, 0.0)) - float(benchmark_priors.get(key, 0.0))) for key in keys)


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    x_bar = mean(xs)
    y_bar = mean(ys)
    num = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - x_bar) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - y_bar) ** 2 for y in ys))
    return num / (den_x * den_y) if den_x and den_y else 0.0


def ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        rank = (i + j - 1) / 2.0 + 1.0
        for k in range(i, j):
            out[indexed[k][0]] = rank
        i = j
    return out


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(ranks(xs), ranks(ys))


def margin_bin(abs_margin: float) -> str:
    if abs_margin < 0.05:
        return "<0.05"
    if abs_margin < 0.20:
        return "0.05-0.20"
    if abs_margin < 0.50:
        return "0.20-0.50"
    return ">=0.50"


def top_prob_bin(probability: float) -> str:
    if probability < 0.50:
        return "<0.50"
    if probability < 0.60:
        return "0.50-0.60"
    if probability < 0.70:
        return "0.60-0.70"
    if probability < 0.80:
        return "0.70-0.80"
    if probability < 0.90:
        return "0.80-0.90"
    return ">=0.90"


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def row_records(label: str, rows: list[dict], episodes: dict[str, dict]) -> list[dict]:
    records = []
    for row in rows:
        if row.get("policy") != "api_ecu":
            continue
        episode = episodes[row["episode_id"]]
        benchmark_priors = success_class_priors(episode)
        benchmark_top = top_key(benchmark_priors)
        hidden_class = hidden_success_class(episode)
        model_masses = model_success_class_masses(row, episode)
        model_top = top_key(model_masses)
        model_top_probability = float(model_masses.get(model_top, 0.0)) if model_top else 0.0
        oracle_margin = eu_advantage(episode["candidate_intents"], episode["ask_cost"], episode["wrong_action_cost"])
        model_margin = float((row.get("debug") or {}).get("api_advantage", 0.0) or 0.0)
        records.append(
            {
                "label": label,
                "episode_id": row["episode_id"],
                "category": row["ambiguity_type"],
                "model_top": model_top,
                "benchmark_top": benchmark_top,
                "hidden_class": hidden_class,
                "model_top_probability": model_top_probability,
                "hidden_probability": float(model_masses.get(hidden_class, 0.0)),
                "unknown_probability": float(model_masses.get(UNKNOWN_CLASS, 0.0)),
                "top_matches_benchmark": model_top == benchmark_top,
                "top_matches_hidden": model_top == hidden_class,
                "prior_tv": total_variation_distance(model_masses, benchmark_priors),
                "brier": brier_score(model_masses, hidden_class, set(benchmark_priors)),
                "oracle_margin": oracle_margin,
                "model_margin": model_margin,
                "ask_agrees_oracle": bool(row["asked"]) == bool(row["oracle_should_ask"]),
            }
        )
    return records


def ece(records: list[dict]) -> float:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[top_prob_bin(float(record["model_top_probability"]))].append(record)
    total = len(records)
    if total == 0:
        return 0.0
    return sum(
        (len(group) / total)
        * abs(safe_mean([float(r["model_top_probability"]) for r in group]) - safe_mean([1.0 if r["top_matches_hidden"] else 0.0 for r in group]))
        for group in groups.values()
    )


def summary_table(all_records: dict[str, list[dict]]) -> str:
    rows = []
    for label, records in all_records.items():
        oracle_margins = [float(record["oracle_margin"]) for record in records]
        model_margins = [float(record["model_margin"]) for record in records]
        rows.append(
            [
                label,
                str(len(records)),
                format_float(safe_mean([1.0 if r["top_matches_benchmark"] else 0.0 for r in records])),
                format_float(safe_mean([1.0 if r["top_matches_hidden"] else 0.0 for r in records])),
                format_float(safe_mean([float(r["prior_tv"]) for r in records])),
                format_float(safe_mean([float(r["hidden_probability"]) for r in records])),
                format_float(safe_mean([float(r["brier"]) for r in records])),
                format_float(ece(records)),
                format_float(pearson(model_margins, oracle_margins)),
                format_float(spearman(model_margins, oracle_margins)),
                format_float(safe_mean([1.0 if r["ask_agrees_oracle"] else 0.0 for r in records])),
                format_float(safe_mean([float(r["unknown_probability"]) for r in records])),
            ]
        )
    return markdown_table(
        [
            "Run",
            "N",
            "Top matches benchmark",
            "Top matches hidden",
            "Prior TV",
            "Mean hidden prob.",
            "Brier",
            "Top-prob. ECE",
            "Margin Pearson",
            "Margin Spearman",
            "Ask/oracle agree",
            "Unknown prob.",
        ],
        rows,
    )


def top_probability_table(records: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[top_prob_bin(float(record["model_top_probability"]))].append(record)
    rows = []
    for label in ["<0.50", "0.50-0.60", "0.60-0.70", "0.70-0.80", "0.80-0.90", ">=0.90"]:
        group = groups.get(label, [])
        if not group:
            continue
        rows.append(
            [
                label,
                str(len(group)),
                format_float(safe_mean([float(r["model_top_probability"]) for r in group])),
                format_float(safe_mean([1.0 if r["top_matches_hidden"] else 0.0 for r in group])),
                format_float(safe_mean([1.0 if r["top_matches_benchmark"] else 0.0 for r in group])),
                format_float(safe_mean([float(r["prior_tv"]) for r in group])),
                format_float(safe_mean([float(r["hidden_probability"]) for r in group])),
                format_float(safe_mean([float(r["brier"]) for r in group])),
            ]
        )
    return markdown_table(
        ["Top-prob. bin", "N", "Mean top prob.", "Hidden accuracy", "Benchmark top match", "Prior TV", "Mean hidden prob.", "Brier"],
        rows,
    )


def margin_table(records: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[margin_bin(abs(float(record["oracle_margin"])))].append(record)
    rows = []
    for label in ["<0.05", "0.05-0.20", "0.20-0.50", ">=0.50"]:
        group = groups.get(label, [])
        if not group:
            continue
        rows.append(
            [
                label,
                str(len(group)),
                format_float(safe_mean([float(r["oracle_margin"]) for r in group])),
                format_float(safe_mean([float(r["model_margin"]) for r in group])),
                format_float(safe_mean([1.0 if r["ask_agrees_oracle"] else 0.0 for r in group])),
                format_float(safe_mean([1.0 if r["top_matches_benchmark"] else 0.0 for r in group])),
                format_float(safe_mean([float(r["prior_tv"]) for r in group])),
                format_float(safe_mean([float(r["brier"]) for r in group])),
            ]
        )
    return markdown_table(
        ["Oracle-margin abs. bin", "N", "Mean oracle margin", "Mean model margin", "Ask/oracle agree", "Top benchmark match", "Prior TV", "Brier"],
        rows,
    )


def category_table(records: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        groups[str(record["category"])].append(record)
    rows = []
    for category in sorted(groups):
        group = groups[category]
        rows.append(
            [
                category,
                str(len(group)),
                format_float(safe_mean([1.0 if r["top_matches_benchmark"] else 0.0 for r in group])),
                format_float(safe_mean([1.0 if r["top_matches_hidden"] else 0.0 for r in group])),
                format_float(safe_mean([float(r["prior_tv"]) for r in group])),
                format_float(safe_mean([float(r["hidden_probability"]) for r in group])),
                format_float(safe_mean([float(r["brier"]) for r in group])),
                format_float(safe_mean([1.0 if r["ask_agrees_oracle"] else 0.0 for r in group])),
            ]
        )
    return markdown_table(
        ["Category", "N", "Top benchmark match", "Top hidden match", "Prior TV", "Mean hidden prob.", "Brier", "Ask/oracle agree"],
        rows,
    )


def main() -> None:
    args = parse_args()
    episodes = {episode["episode_id"]: episode for episode in read_jsonl(args.episodes)}
    all_records = {}
    for spec in args.run:
        label, path = parse_run_spec(spec)
        all_records[label] = row_records(label, read_jsonl(path), episodes)

    primary_label = next(iter(all_records))
    primary_records = all_records[primary_label]
    text = "\n".join(
        [
            "# API ECU Candidate-Probability Calibration",
            "",
            "This no-API diagnostic inspects cached `api_ecu` rows. It maps model-generated candidate target IDs back to benchmark success classes, compares model probabilities with benchmark priors and hidden success classes, and compares model-derived utility margins with oracle utility margins.",
            "",
            "## Run Summary",
            "",
            summary_table(all_records),
            f"## Top-Probability Calibration ({primary_label})",
            "",
            top_probability_table(primary_records),
            f"## Ask/Oracle Agreement by Oracle-Margin Size ({primary_label})",
            "",
            margin_table(primary_records),
            f"## Category Breakdown ({primary_label})",
            "",
            category_table(primary_records),
            "## Interpretation",
            "",
            "- The analysis uses shipped cached API debug fields and makes no model calls.",
            "- Top-probability calibration is measured against the sampled hidden success class, so it is noisy on 100-row subsets.",
            "- The margin-correlation rows test whether model-derived candidate probabilities preserve the ordering of utility-relevant uncertainty, not whether they are perfectly calibrated probabilities.",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote API candidate calibration report to {args.out}")


if __name__ == "__main__":
    main()
