from __future__ import annotations

import argparse
from collections import defaultdict

from clarify_to_act.io import read_jsonl, write_text
from clarify_to_act.metrics import format_float, markdown_table


POLICY_ORDER = ["api_direct_act", "api_ask_needed", "api_ask_needed_cot", "api_ecu"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="data/runs/api_eval_100_corrected_results.jsonl")
    parser.add_argument("--out", default="paper/tables/api_eval_100_corrected/question_usefulness.md")
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


def safe_rate(num: int, den: int) -> str:
    if den == 0:
        return "-"
    return format_float(num / den)


def usefulness_stats(rows: list[dict]) -> dict[str, str]:
    asked = [row for row in rows if row["asked"]]
    oracle_ask = [row for row in rows if row["oracle_should_ask"]]
    needed_asks = [row for row in asked if row["oracle_should_ask"]]
    unnecessary_asks = [row for row in asked if not row["oracle_should_ask"]]
    successful_after_ask = [row for row in asked if row["success"]]
    useful_successful_asks = [row for row in needed_asks if row["success"]]
    return {
        "n": str(len(rows)),
        "asked": str(len(asked)),
        "oracle_ask": str(len(oracle_ask)),
        "ask_precision": safe_rate(len(needed_asks), len(asked)),
        "ask_recall": safe_rate(len(needed_asks), len(oracle_ask)),
        "post_answer_success": safe_rate(len(successful_after_ask), len(asked)),
        "useful_success_rate": safe_rate(len(useful_successful_asks), len(asked)),
        "unneeded_ask_share": safe_rate(len(unnecessary_asks), len(asked)),
    }


def question_table(rows: list[dict]) -> str:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["split"], row["policy"])].append(row)

    table_rows = []
    for split, policy in sorted(grouped, key=lambda key: (key[0], policy_sort_key(key[1]))):
        stats = usefulness_stats(grouped[(split, policy)])
        table_rows.append(
            [
                split,
                policy,
                stats["n"],
                stats["asked"],
                stats["oracle_ask"],
                stats["ask_precision"],
                stats["ask_recall"],
                stats["post_answer_success"],
                stats["useful_success_rate"],
                stats["unneeded_ask_share"],
            ]
        )
    return markdown_table(
        [
            "Split",
            "Method",
            "N",
            "Asked",
            "Oracle ask",
            "Ask precision",
            "Ask recall",
            "Post-answer success",
            "Useful successful asks",
            "Unneeded ask share",
        ],
        table_rows,
    )


def takeaway(rows: list[dict]) -> str:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["split"], row["policy"])].append(row)

    parts = []
    for split in sorted({row["split"] for row in rows}):
        ecu = usefulness_stats(grouped[(split, "api_ecu")]) if (split, "api_ecu") in grouped else None
        ask_needed = usefulness_stats(grouped[(split, "api_ask_needed")]) if (split, "api_ask_needed") in grouped else None
        if ecu and ask_needed:
            parts.append(
                f"- `{split}`: ECU ask precision/recall/post-answer success are "
                f"{ecu['ask_precision']}/{ecu['ask_recall']}/{ecu['post_answer_success']}; "
                f"Ask-Needed is {ask_needed['ask_precision']}/{ask_needed['ask_recall']}/{ask_needed['post_answer_success']}."
            )
    return "\n".join(parts) + ("\n" if parts else "")


def main() -> None:
    args = parse_args()
    rows = read_jsonl_paths(args.results)
    text = "\n".join(
        [
            "# Question Usefulness",
            "",
            "This table evaluates whether first-turn questions are both necessary under the utility oracle and successfully grounded after the simulated user answer.",
            "",
            "Ask precision is the fraction of asked questions that were oracle-needed. Ask recall is the fraction of oracle-needed questions that were asked. Post-answer success is final task success conditional on asking.",
            "",
            "## Takeaways",
            "",
            takeaway(rows),
            "## Table",
            "",
            question_table(rows),
        ]
    )
    write_text(args.out, text)
    print(f"wrote question usefulness table to {args.out}")


if __name__ == "__main__":
    main()
