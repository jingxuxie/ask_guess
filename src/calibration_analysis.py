from __future__ import annotations

import argparse
from collections import defaultdict

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table


POLICY_ORDER = [
    "api_direct_act",
    "api_ask_needed",
    "api_ask_needed_cot",
    "api_ecu",
    "direct_act",
    "prompted_heuristic",
    "ecu",
    "learned_controller",
]

BIN_ORDER = ["act_preferred", "near_tie", "ask_preferred"]
BIN_LABELS = {
    "act_preferred": "Act preferred",
    "near_tie": "Near tie",
    "ask_preferred": "Ask preferred",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", default="data/generated/episodes.jsonl")
    parser.add_argument("--results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/calibration_by_margin.md")
    return parser.parse_args()


def read_jsonl_paths(paths: str) -> list[dict]:
    rows: list[dict] = []
    for path in [part.strip() for part in paths.split(",") if part.strip()]:
        rows.extend(read_jsonl(path))
    return rows


def policy_sort_key(policy: str) -> tuple[int, str]:
    try:
        return (POLICY_ORDER.index(policy), policy)
    except ValueError:
        return (999, policy)


def margin_bin(margin: float) -> str:
    if margin <= -0.05:
        return "act_preferred"
    if margin <= 0.05:
        return "near_tie"
    return "ask_preferred"


def enrich_rows(episodes: dict[str, dict], rows: list[dict]) -> list[dict]:
    enriched = []
    for row in rows:
        episode = episodes[row["episode_id"]]
        margin = float(episode["features"]["eu_ask_minus_act"])
        new_row = dict(row)
        new_row["eu_ask_minus_act"] = margin
        new_row["utility_margin_bin"] = margin_bin(margin)
        enriched.append(new_row)
    return enriched


def calibration_table(rows: list[dict]) -> str:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["split"], row["utility_margin_bin"], row["policy"])].append(row)

    table_rows = []
    split_order = sorted({row["split"] for row in rows})
    policies = sorted({row["policy"] for row in rows}, key=policy_sort_key)
    for split in split_order:
        for bin_name in BIN_ORDER:
            for policy in policies:
                group = grouped.get((split, bin_name, policy), [])
                if not group:
                    continue
                stats = aggregate(group)
                mean_margin = sum(float(row["eu_ask_minus_act"]) for row in group) / len(group)
                table_rows.append(
                    [
                        split,
                        BIN_LABELS[bin_name],
                        policy,
                        str(stats["n"]),
                        format_float(mean_margin),
                        format_float(stats["oracle_ask_rate"]),
                        format_float(stats["ask_rate"]),
                        format_float(stats["net_utility"]),
                        format_float(stats["missed_clarification_rate"]),
                        format_float(stats["unnecessary_clarification_rate"]),
                    ]
                )
    return markdown_table(
        [
            "Split",
            "Utility-margin bin",
            "Method",
            "N",
            "Mean EU ask-act",
            "Oracle ask",
            "Ask rate",
            "Net utility",
            "Missed clarif.",
            "Unnecessary clarif.",
        ],
        table_rows,
    )


def takeaway(rows: list[dict]) -> str:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["split"], row["utility_margin_bin"], row["policy"])].append(row)
    parts = []
    for split in sorted({row["split"] for row in rows}):
        ecu_ask = aggregate(grouped[(split, "ask_preferred", "api_ecu")])["ask_rate"] if (split, "ask_preferred", "api_ecu") in grouped else None
        ecu_act = aggregate(grouped[(split, "act_preferred", "api_ecu")])["ask_rate"] if (split, "act_preferred", "api_ecu") in grouped else None
        prompted_ask = (
            aggregate(grouped[(split, "ask_preferred", "api_ask_needed")])["ask_rate"]
            if (split, "ask_preferred", "api_ask_needed") in grouped
            else None
        )
        prompted_act = (
            aggregate(grouped[(split, "act_preferred", "api_ask_needed")])["ask_rate"]
            if (split, "act_preferred", "api_ask_needed") in grouped
            else None
        )
        if None in {ecu_ask, ecu_act, prompted_ask, prompted_act}:
            continue
        parts.append(
            f"- `{split}`: ECU asks on {format_float(ecu_ask)} of ask-preferred episodes and "
            f"{format_float(ecu_act)} of act-preferred episodes; Ask-Needed asks on "
            f"{format_float(prompted_ask)} and {format_float(prompted_act)}, respectively."
        )
    return "\n".join(parts) + ("\n" if parts else "")


def main() -> None:
    args = parse_args()
    episodes = {episode["episode_id"]: episode for episode in read_jsonl_paths(args.episodes)}
    rows = enrich_rows(episodes, read_jsonl_paths(args.results))
    text = "\n".join(
        [
            "# Utility-Margin Calibration",
            "",
            "Bins are defined by the oracle expected-utility margin `EU(ask) - EU(act)`: "
            "`Act preferred` is <= -0.05, `Near tie` is (-0.05, 0.05], and `Ask preferred` is > 0.05.",
            "",
            "## Takeaways",
            "",
            takeaway(rows),
            "## Calibration Table",
            "",
            calibration_table(rows),
        ]
    )
    write_text(args.out, text)
    print(f"wrote utility-margin calibration table to {args.out}")


if __name__ == "__main__":
    main()
