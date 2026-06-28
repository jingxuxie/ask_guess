from __future__ import annotations

import argparse
from pathlib import Path

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
    "api_direct_act",
    "api_ask_needed",
    "api_ask_needed_cot",
    "api_ecu",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="data/runs/offline_results.jsonl")
    parser.add_argument("--out-dir", default="paper/tables")
    return parser.parse_args()


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def read_result_paths(paths: str) -> list[dict]:
    rows: list[dict] = []
    for path in [part.strip() for part in paths.split(",") if part.strip()]:
        rows.extend(read_jsonl(path))
    return rows


def main_table(rows: list[dict]) -> str:
    table_rows = []
    grouped = group_rows(rows, ("split", "policy"))
    for split, policy in sorted(grouped, key=lambda key: (key[0], policy_sort_key(key[1]))):
        stats = aggregate(grouped[(split, policy)])
        ci = f"[{format_float(stats['net_utility_ci_low'])}, {format_float(stats['net_utility_ci_high'])}]"
        table_rows.append(
            [
                split,
                policy,
                str(stats["n"]),
                format_float(stats["net_utility"]),
                ci,
                format_float(stats["success"]),
                format_float(stats["ask_rate"]),
                format_float(stats["missed_clarification_rate"]),
                format_float(stats["unnecessary_clarification_rate"]),
            ]
        )
    return markdown_table(
        [
            "Split",
            "Method",
            "N",
            "Net utility",
            "95% CI",
            "Success",
            "Ask rate",
            "Missed clarif.",
            "Unnecessary clarif.",
        ],
        table_rows,
    )


def category_table(rows: list[dict]) -> str:
    table_rows = []
    grouped = group_rows(rows, ("split", "ambiguity_type", "policy"))
    for split, category, policy in sorted(grouped, key=lambda key: (key[0], key[1], policy_sort_key(key[2]))):
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
    return markdown_table(
        ["Split", "Category", "Method", "N", "Net utility", "Success", "Ask rate", "Oracle ask rate"],
        table_rows,
    )


def failure_examples(rows: list[dict], limit: int = 20) -> str:
    parts = ["# Failure Examples\n\n"]
    failures = [row for row in rows if not row["success"] or row["asked"] != row["oracle_should_ask"]]
    for row in failures[:limit]:
        parts.append(f"## {row['policy']} / {row['episode_id']}\n")
        parts.append(f"- Split/category: {row['split']} / {row['ambiguity_type']} ({row['variant']})\n")
        parts.append(f"- Asked: {row['asked']} | Oracle should ask: {row['oracle_should_ask']}\n")
        parts.append(f"- Success: {row['success']} | Reward: {row['reward']}\n")
        if row.get("question"):
            parts.append(f"- Question: {row['question']}\n")
            parts.append(f"- Answer: {row.get('answer')}\n")
        parts.append(f"- Final action: `{row['final_action']}`\n\n")
    return "".join(parts)


def main() -> None:
    args = parse_args()
    rows = read_result_paths(args.results)
    out_dir = Path(args.out_dir)
    write_text(out_dir / "main_results.md", "# Main Results\n\n" + main_table(rows))
    write_text(out_dir / "category_breakdown.md", "# Category Breakdown\n\n" + category_table(rows))
    write_text(out_dir / "failure_examples.md", failure_examples(rows))
    print(main_table(rows))
    print(f"wrote tables to {out_dir}")


if __name__ == "__main__":
    main()
