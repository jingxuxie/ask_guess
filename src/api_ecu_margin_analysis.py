from __future__ import annotations

import argparse
from collections import defaultdict
from statistics import mean

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import aggregate, format_float, markdown_table
from run_api_experiment import API_ECU_ASK_MARGIN


CATEGORY_ORDER = ["context_resolved", "equivalent_outcome", "preference_social", "referential", "risk_sensitive"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/api_ecu_margin_analysis.md")
    return parser.parse_args()


def api_advantage(row: dict) -> float:
    return float(row.get("debug", {}).get("api_advantage", 0.0))


def api_margin(row: dict) -> float:
    return float(row.get("debug", {}).get("api_ecu_margin", API_ECU_ASK_MARGIN))


def margin_positive(row: dict) -> bool:
    return api_advantage(row) > api_margin(row)


def context_override(row: dict) -> bool:
    return margin_positive(row) and bool(row.get("debug", {}).get("api_context_resolved_enough", False))


def rate(rows: list[dict], predicate) -> float:
    return sum(1 for row in rows if predicate(row)) / max(len(rows), 1)


def mean_advantage(rows: list[dict]) -> float:
    return mean(api_advantage(row) for row in rows) if rows else 0.0


def summary_table(rows: list[dict]) -> str:
    final_ask_agree = rate(rows, lambda row: bool(row["asked"]) == bool(row["oracle_should_ask"]))
    margin_oracle_agree = rate(rows, lambda row: margin_positive(row) == bool(row["oracle_should_ask"]))
    table_rows = [
        ["API ECU rows", str(len(rows)), "cached rows with `policy == api_ecu`"],
        ["Rows with API advantage", str(sum("api_advantage" in row.get("debug", {}) for row in rows)), "debug field present"],
        ["Mean API advantage", format_float(mean_advantage(rows)), "model-derived candidate utility margin"],
        ["Configured API ECU margin", format_float(API_ECU_ASK_MARGIN), "ask when advantage is greater than this, unless context override applies"],
        ["Margin-positive rate", format_float(rate(rows, margin_positive)), "`api_advantage > api_ecu_margin`"],
        ["Context-override rate", format_float(rate(rows, context_override)), "margin-positive but context-resolved enough to act"],
        ["Oracle ask rate", format_float(rate(rows, lambda row: bool(row["oracle_should_ask"]))), "benchmark label"],
        ["Final ask rate", format_float(rate(rows, lambda row: bool(row["asked"]))), "actual API ECU first-turn decision"],
        ["Margin/oracle agreement", format_float(margin_oracle_agree), "before context override"],
        ["Final ask/oracle agreement", format_float(final_ask_agree), "after margin rule and context override"],
    ]
    return markdown_table(["Quantity", "Value", "Definition"], table_rows)


def margin_bin_table(rows: list[dict]) -> str:
    groups = [
        ("margin <= threshold", [row for row in rows if not margin_positive(row)]),
        ("margin > threshold", [row for row in rows if margin_positive(row)]),
    ]
    table_rows = []
    for label, group in groups:
        stats = aggregate(group)
        table_rows.append(
            [
                label,
                str(stats["n"]),
                format_float(mean_advantage(group)),
                format_float(rate(group, lambda row: bool(row["oracle_should_ask"]))),
                format_float(rate(group, lambda row: bool(row["asked"]))),
                format_float(rate(group, context_override)),
                format_float(stats["success"]),
                format_float(stats["net_utility"]),
            ]
        )
    return markdown_table(
        ["API margin bin", "N", "Mean API advantage", "Oracle ask", "Final ask", "Context override", "Success", "Net utility"],
        table_rows,
    )


def category_table(rows: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["ambiguity_type"]].append(row)

    table_rows = []
    for category in CATEGORY_ORDER:
        group = grouped.get(category, [])
        if not group:
            continue
        stats = aggregate(group)
        table_rows.append(
            [
                category,
                str(stats["n"]),
                format_float(mean_advantage(group)),
                format_float(rate(group, margin_positive)),
                format_float(rate(group, context_override)),
                format_float(stats["oracle_ask_rate"]),
                format_float(stats["ask_rate"]),
                format_float(stats["success"]),
                format_float(stats["net_utility"]),
            ]
        )
    return markdown_table(
        [
            "Category",
            "N",
            "Mean API advantage",
            "Margin positive",
            "Context override",
            "Oracle ask",
            "Final ask",
            "Success",
            "Net utility",
        ],
        table_rows,
    )


def disagreement_table(rows: list[dict]) -> str:
    disagreements = [row for row in rows if margin_positive(row) != bool(row["oracle_should_ask"])]
    if not disagreements:
        return "No cached API ECU row has a margin-threshold decision that disagrees with the oracle ask label."

    table_rows = []
    for row in disagreements:
        table_rows.append(
            [
                row["episode_id"],
                row["ambiguity_type"],
                format_float(api_advantage(row)),
                str(margin_positive(row)),
                str(context_override(row)),
                str(bool(row["oracle_should_ask"])),
                str(bool(row["asked"])),
                format_float(float(row["reward"])),
            ]
        )
    return markdown_table(
        ["Episode", "Category", "API advantage", "Margin positive", "Context override", "Oracle ask", "Final ask", "Reward"],
        table_rows,
    )


def main() -> None:
    args = parse_args()
    rows = [row for row in read_jsonl(args.api_results) if row["policy"] == "api_ecu"]
    text = "\n".join(
        [
            "# API ECU Candidate-Margin Analysis",
            "",
            "This no-API diagnostic inspects cached GPT-4.1-mini API ECU rows. The API ECU first asks the model for candidate interpretations and probabilities, computes a utility margin from those model-derived candidates, then asks only when the margin clears the configured threshold unless the model also marks the instruction as sufficiently context-resolved.",
            "",
            "## Summary",
            "",
            summary_table(rows),
            "## By API Candidate-Margin Bin",
            "",
            margin_bin_table(rows),
            "## By Ambiguity Category",
            "",
            category_table(rows),
            "## Margin/Oracle Disagreements",
            "",
            disagreement_table(rows),
            "## Interpretation",
            "",
            "- The diagnostic uses cached API debug fields and does not make new model calls.",
            "- It tests whether the API-side candidate utility margin aligns with the benchmark ask labels on the final 100-episode API subset.",
            "- It should be read as an internal calibration check for the API ECU pipeline, not as an independent benchmark result.",
            "",
        ]
    )
    write_text(args.out, text)
    print(f"wrote API ECU candidate-margin analysis to {args.out}")


if __name__ == "__main__":
    main()
