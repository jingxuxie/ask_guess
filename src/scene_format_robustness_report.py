from __future__ import annotations

import argparse
from collections import defaultdict

from clarify_to_act.environment import normalize_action
from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--perturbed", required=True)
    parser.add_argument("--out", default="paper/tables/scene_format_robustness.md")
    return parser.parse_args()


def first_turn_signature(row: dict) -> tuple[str, str, str]:
    if row.get("asked"):
        return ("ASK", "", "")
    final = row.get("final_action") or {}
    return ("ACT", normalize_action(final.get("action")), str(final.get("target_id", "")))


def row_key(row: dict) -> tuple[str, str]:
    return (row["episode_id"], row["policy"])


def paired_rows(baseline: list[dict], perturbed: list[dict]) -> list[tuple[dict, dict]]:
    by_key = {row_key(row): row for row in baseline}
    pairs = []
    for row in perturbed:
        base = by_key.get(row_key(row))
        if base is not None:
            pairs.append((base, row))
    return pairs


def comparison_table(pairs: list[tuple[dict, dict]]) -> str:
    by_policy: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for base, perturbed in pairs:
        by_policy[base["policy"]].append((base, perturbed))

    rows = []
    for policy in sorted(by_policy):
        policy_pairs = by_policy[policy]
        base_rows = [base for base, _ in policy_pairs]
        perturbed_rows = [perturbed for _, perturbed in policy_pairs]
        base_stats = aggregate(base_rows)
        perturbed_stats = aggregate(perturbed_rows)
        ask_act_changes = sum(bool(base["asked"]) != bool(perturbed["asked"]) for base, perturbed in policy_pairs)
        first_output_changes = sum(first_turn_signature(base) != first_turn_signature(perturbed) for base, perturbed in policy_pairs)
        rows.append(
            [
                policy,
                str(len(policy_pairs)),
                format_float(base_stats["net_utility"]),
                format_float(perturbed_stats["net_utility"]),
                format_float(perturbed_stats["net_utility"] - base_stats["net_utility"]),
                format_float(base_stats["ask_rate"]),
                format_float(perturbed_stats["ask_rate"]),
                format_float(ask_act_changes / len(policy_pairs) if policy_pairs else 0.0),
                format_float(first_output_changes / len(policy_pairs) if policy_pairs else 0.0),
                format_float(perturbed_stats["missed_clarification_rate"]),
                format_float(perturbed_stats["unnecessary_clarification_rate"]),
            ]
        )

    return markdown_table(
        [
            "Policy",
            "Shared N",
            "Baseline utility",
            "Perturbed utility",
            "Delta",
            "Baseline ask",
            "Perturbed ask",
            "Ask/act changed",
            "First output changed",
            "Perturbed missed",
            "Perturbed unnecessary",
        ],
        rows,
    )


def category_table(pairs: list[tuple[dict, dict]]) -> str:
    by_category_policy: dict[tuple[str, str], list[tuple[dict, dict]]] = defaultdict(list)
    for base, perturbed in pairs:
        by_category_policy[(base["ambiguity_type"], base["policy"])].append((base, perturbed))

    rows = []
    for category, policy in sorted(by_category_policy):
        policy_pairs = by_category_policy[(category, policy)]
        base_rows = [base for base, _ in policy_pairs]
        perturbed_rows = [perturbed for _, perturbed in policy_pairs]
        base_stats = aggregate(base_rows)
        perturbed_stats = aggregate(perturbed_rows)
        ask_act_changes = sum(bool(base["asked"]) != bool(perturbed["asked"]) for base, perturbed in policy_pairs)
        rows.append(
            [
                category,
                policy,
                str(len(policy_pairs)),
                format_float(base_stats["net_utility"]),
                format_float(perturbed_stats["net_utility"]),
                format_float(ask_act_changes / len(policy_pairs) if policy_pairs else 0.0),
                format_float(perturbed_stats["missed_clarification_rate"]),
                format_float(perturbed_stats["unnecessary_clarification_rate"]),
            ]
        )

    return markdown_table(
        ["Category", "Policy", "Shared N", "Baseline utility", "Perturbed utility", "Ask/act changed", "Perturbed missed", "Perturbed unnecessary"],
        rows,
    )


def main() -> None:
    args = parse_args()
    baseline = read_jsonl(args.baseline)
    perturbed = read_jsonl(args.perturbed)
    pairs = paired_rows(baseline, perturbed)
    text = "\n".join(
        [
            "# Scene-Format Robustness",
            "",
            "This report compares baseline JSON prompts against a perturbed scene serialization on shared episode-policy pairs.",
            "",
            "## Policy Summary",
            "",
            comparison_table(pairs),
            "",
            "## Category Summary",
            "",
            category_table(pairs),
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote scene-format robustness report to {args.out}")


if __name__ == "__main__":
    main()
