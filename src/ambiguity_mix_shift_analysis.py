from __future__ import annotations

import argparse
from collections import Counter

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, group_rows, markdown_table


POLICY_ORDER = [
    "direct_act",
    "ask_always",
    "raw_ambiguity",
    "prompted_heuristic",
    "ecu",
    "ecu_threshold",
    "learned_controller",
]
KEY_POLICIES = ["prompted_heuristic", "ecu", "ecu_threshold", "learned_controller"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/ambiguity_mix_shift_episodes.jsonl")
    parser.add_argument("--results", default="data/runs/ambiguity_mix_shift_results.jsonl")
    parser.add_argument("--out", default="paper/tables/ambiguity_mix_shift.md")
    return parser.parse_args()


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def split_category_table(episodes: list[dict]) -> str:
    counts = Counter((ep["split"], ep["ambiguity_type"]) for ep in episodes)
    rows = []
    for split, category in sorted(counts):
        rows.append([split, category, str(counts[(split, category)])])
    return markdown_table(["Split", "Category", "Episodes"], rows)


def main_result_table(rows: list[dict]) -> str:
    grouped = group_rows(rows, ("split", "policy"))
    table_rows = []
    for split, policy in sorted(grouped, key=lambda item: (item[0], policy_sort_key(item[1]))):
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


def ood_delta_table(rows: list[dict]) -> str:
    grouped = group_rows(rows, ("split", "policy"))
    table_rows = []
    for policy in KEY_POLICIES:
        seen = grouped.get(("test", policy), [])
        ood = grouped.get(("ood_ambiguity_mix", policy), [])
        if not seen or not ood:
            continue
        seen_stats = aggregate(seen)
        ood_stats = aggregate(ood)
        table_rows.append(
            [
                policy,
                format_float(seen_stats["net_utility"]),
                format_float(ood_stats["net_utility"]),
                format_float(ood_stats["net_utility"] - seen_stats["net_utility"]),
                format_float(seen_stats["success"]),
                format_float(ood_stats["success"]),
                format_float(seen_stats["ask_rate"]),
                format_float(ood_stats["ask_rate"]),
            ]
        )
    return markdown_table(
        ["Method", "Seen-test utility", "Held-out utility", "Held-out - seen", "Seen success", "Held-out success", "Seen ask", "Held-out ask"],
        table_rows,
    )


def category_table(rows: list[dict]) -> str:
    grouped = group_rows([row for row in rows if row["policy"] in set(KEY_POLICIES)], ("split", "ambiguity_type", "policy"))
    table_rows = []
    for split, category, policy in sorted(grouped, key=lambda item: (item[0], item[1], policy_sort_key(item[2]))):
        stats = aggregate(grouped[(split, category, policy)])
        table_rows.append(
            [
                split,
                category,
                policy,
                str(stats["n"]),
                format_float(stats["net_utility"]),
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["oracle_ask_rate"]),
            ]
        )
    return markdown_table(["Split", "Category", "Method", "N", "Net utility", "Success", "Ask rate", "Oracle ask"], table_rows)


def interpretation(rows: list[dict]) -> str:
    grouped = group_rows(rows, ("split", "policy"))
    lines = []
    for policy in KEY_POLICIES:
        seen = grouped.get(("test", policy), [])
        ood = grouped.get(("ood_ambiguity_mix", policy), [])
        if not seen or not ood:
            continue
        seen_stats = aggregate(seen)
        ood_stats = aggregate(ood)
        lines.append(
            f"- `{policy}`: seen utility {format_float(seen_stats['net_utility'])}, "
            f"held-out utility {format_float(ood_stats['net_utility'])}, "
            f"held-out ask rate {format_float(ood_stats['ask_rate'])}."
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    episodes = read_jsonl(args.episodes)
    rows = read_jsonl(args.results)
    text = "\n".join(
        [
            "# Held-Out Ambiguity-Mix Shift",
            "",
            "This offline diagnostic trains and tunes on referential, context-resolved, and equivalent-outcome episodes, then evaluates transfer to risk-sensitive and preference/social episodes. It is a no-API robustness check for category-shift sensitivity, not a substitute for a broad API model sweep.",
            "",
            "## Split and Category Coverage",
            "",
            split_category_table(episodes),
            "## Main Results",
            "",
            main_result_table(rows),
            "## Held-Out Deltas",
            "",
            ood_delta_table(rows),
            "## Category Breakdown",
            "",
            category_table(rows),
            "## Interpretation",
            "",
            interpretation(rows),
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote ambiguity-mix shift analysis to {args.out}")


if __name__ == "__main__":
    main()
